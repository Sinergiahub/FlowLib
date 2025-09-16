from fastapi import FastAPI, APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
import re
from datetime import datetime, timezone
import pandas as pd
from io import StringIO
import asyncio
import requests

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase connection
supabase_url = os.environ['SUPABASE_URL']
supabase_key = os.environ['SUPABASE_SERVICE_KEY']
supabase: Client = create_client(supabase_url, supabase_key)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models (same as before)
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    display_name: str
    avatar_url: Optional[str] = None
    role: str = "user"  # user, pro, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Category(BaseModel):
    key: str  # primary key (e.g., "marketing", "productivity")
    name: str

class Tool(BaseModel):
    key: str  # primary key (e.g., "openai", "slack")
    name: str

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    title: str
    description: Optional[str] = None
    platform: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    tutorial_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    download_url: Optional[str] = None
    json_url: Optional[str] = None
    language: str = "pt-BR"
    status: str = "draft"  # draft, published, archived
    rating_avg: Optional[float] = None
    downloads_count: int = 0
    tags: Optional[str] = None
    notes: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    categories: List[str] = []  # category keys
    tools: List[str] = []  # tool keys

    @validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug deve conter apenas letras minúsculas, números e hífens')
        return v

    @validator('rating_avg')
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Rating deve estar entre 0 and 5')
        return v

    @validator('downloads_count')
    def validate_downloads(cls, v):
        if v < 0:
            raise ValueError('Downloads count deve ser >= 0')
        return v

    @validator('tutorial_url', 'preview_image_url', 'download_url', 'json_url')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL deve começar com http:// ou https://')
        return v

# New models for favorites and ratings
class Favorite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    template_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    template_id: str
    rating: int = Field(..., ge=1, le=5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TemplateWithUserData(Template):
    is_favorited: bool = False
    user_rating: Optional[int] = None

class ImportReport(BaseModel):
    inserted: int = 0
    updated: int = 0
    deleted: int = 0
    errors: List[str] = []

class PreviewRow(BaseModel):
    line_number: int
    slug: str
    title: str
    action: str
    status: str  # insert|update|delete|error
    message: str
    data: Dict[str, Any] = {}

class PreviewReport(BaseModel):
    total_rows: int = 0
    insert_count: int = 0
    update_count: int = 0
    delete_count: int = 0
    error_count: int = 0
    rows: List[PreviewRow] = []

class PaginatedTemplateResponse(BaseModel):
    items: List[Template]
    total: int
    page: int
    page_size: int
    total_pages: int
    facets: Dict[str, List[str]]

class TemplateFacets(BaseModel):
    platforms: List[str]
    categories: List[str] 
    tools: List[str]

# CSV Import utilities (same as before)
def safe_str_strip(value) -> str:
    """Safely convert value to string and strip, handling NaN and None"""
    if value is None or pd.isna(value):
        return ''
    return str(value).strip()

def safe_str_strip_or_none(value) -> Optional[str]:
    """Safely convert value to string and strip, return None if empty"""
    result = safe_str_strip(value)
    return result if result else None

def parse_pipe_separated(value: str) -> List[str]:
    """Parse pipe-separated values and return list"""
    if not value or pd.isna(value):
        return []
    return [v.strip() for v in str(value).split('|') if v.strip()]

def validate_template_data(row: Dict[str, Any]) -> List[str]:
    """Validate template data and return list of errors - RELAXED VALIDATION"""
    errors = []
    
    # Required fields - more flexible
    slug = safe_str_strip(row.get('slug', ''))
    if not slug:
        errors.append("Slug é obrigatório")
    elif len(slug) < 2:
        errors.append("Slug deve ter pelo menos 2 caracteres")
    elif not re.match(r'^[a-z0-9-_]+$', slug):
        errors.append(f"Slug inválido: {slug} (apenas letras minúsculas, números, hífens e underscores)")
    
    # Platform validation - more flexible
    platform = safe_str_strip(row.get('platform', ''))
    if not platform:
        # Set default platform if not provided
        row['platform'] = 'n8n'
    
    # URL validation - more relaxed
    url_fields = ['tutorial_url', 'preview_image_url', 'download_url', 'json_url']
    for field in url_fields:
        url = row.get(field)
        if url and not pd.isna(url) and url.strip():
            url_str = str(url).strip()
            # More flexible URL validation
            if url_str and not (url_str.startswith('http://') or url_str.startswith('https://') or url_str.startswith('/')):
                # Instead of error, auto-fix by adding https://
                if '.' in url_str:  # Looks like a domain
                    row[field] = f"https://{url_str}"
                else:
                    errors.append(f"{field} parece ser uma URL inválida: {url_str}")
    
    # Rating validation - more flexible
    if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
        try:
            rating = float(row['rating_avg'])
            if rating < 0:
                row['rating_avg'] = 0  # Auto-fix negative ratings
            elif rating > 5:
                row['rating_avg'] = 5  # Auto-fix ratings above 5
        except (ValueError, TypeError):
            # Remove invalid rating instead of error
            row['rating_avg'] = None
    
    # Downloads validation - more flexible
    if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
        try:
            downloads = int(float(row['downloads_count']))  # Handle decimal numbers
            if downloads < 0:
                row['downloads_count'] = 0  # Auto-fix negative downloads
        except (ValueError, TypeError):
            # Set to 0 instead of error
            row['downloads_count'] = 0
    
    return errors

def convert_google_sheets_url(sheet_url: str) -> str:
    """Convert Google Sheets URL to CSV export URL"""
    if 'docs.google.com/spreadsheets' not in sheet_url:
        raise ValueError("URL deve ser um Google Sheets válido")
    
    # Extract sheet ID from various Google Sheets URL formats
    if '/edit' in sheet_url:
        sheet_id = sheet_url.split('/d/')[1].split('/edit')[0]
    elif '/d/' in sheet_url:
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    else:
        raise ValueError("Formato de URL do Google Sheets inválido")
    
    # Return CSV export URL
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

async def fetch_csv_from_url(url: str) -> str:
    """Fetch CSV content from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Erro ao buscar CSV da URL: {str(e)}")

async def preview_template_row(row: Dict[str, Any], action: str, line_number: int) -> PreviewRow:
    """Preview a single template row without saving - RELAXED VALIDATION"""
    
    slug = safe_str_strip(row.get('slug', ''))
    title = safe_str_strip(row.get('title', ''))
    
    # Use slug as title if title is empty
    if not title and slug:
        title = slug.replace('-', ' ').replace('_', ' ').title()
    
    preview_row = PreviewRow(
        line_number=line_number,
        slug=slug,
        title=title,
        action=action,
        status="error",
        message="",
        data={}
    )
    
    try:
        if not slug:
            preview_row.message = "Slug/Key é obrigatório"
            return preview_row
        
        if action == "delete":
            # Check if template exists for deletion
            existing = supabase.table('templates').select('*').eq('slug', slug).execute()
            if existing.data:
                preview_row.status = "delete"
                preview_row.message = f"Template '{title or slug}' será deletado"
            else:
                preview_row.status = "error"
                preview_row.message = f"Template com slug '{slug}' não encontrado para exclusão"
            return preview_row
        
        # Validate data for upsert - but continue even with warnings
        validation_errors = validate_template_data(row)
        
        # Check if template exists
        existing = supabase.table('templates').select('*').eq('slug', slug).execute()
        
        # Prepare preview data with all available fields
        preview_data = {
            "slug": slug,
            "title": title or f"Template {slug}",
            "platform": safe_str_strip(row.get('platform', 'n8n')),
            "author_name": safe_str_strip_or_none(row.get('author_name')) or 'Admin',
            "description": safe_str_strip_or_none(row.get('description')) or '',
            "categories": parse_pipe_separated(row.get('categories', '')),
            "tools": parse_pipe_separated(row.get('tools', '')),
            "status": safe_str_strip(row.get('status', 'published'))
        }
        
        # Add rating and downloads if present - with auto-correction
        if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
            try:
                rating = float(row['rating_avg'])
                preview_data["rating_avg"] = max(0, min(5, rating))  # Clamp between 0-5
            except:
                preview_data["rating_avg"] = None
        
        if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
            try:
                downloads = int(float(row['downloads_count']))
                preview_data["downloads_count"] = max(0, downloads)  # Ensure non-negative
            except:
                preview_data["downloads_count"] = 0
        
        preview_row.data = preview_data
        
        # Set status and message
        if validation_errors:
            preview_row.status = "error"
            preview_row.message = "; ".join(validation_errors)
        elif existing.data:
            preview_row.status = "update"
            preview_row.message = f"Template '{title}' será atualizado"
        else:
            preview_row.status = "insert"
            preview_row.message = f"Template '{title}' será inserido"
        
        return preview_row
        
    except Exception as e:
        preview_row.status = "error"
        preview_row.message = f"Erro ao processar linha: {str(e)}"
        return preview_row

async def process_template_row(row: Dict[str, Any], action: str) -> Dict[str, Any]:
    """Process a single template row"""
    result = {"success": False, "action": action, "errors": []}
    
    try:
        slug = safe_str_strip(row.get('slug', ''))
        if not slug:
            result["errors"].append("Slug é obrigatório")
            return result
        
        if action == "delete":
            # Delete template by slug
            delete_result = supabase.table('templates').delete().eq('slug', slug).execute()
            if delete_result.data:
                result["success"] = True
                result["action"] = "deleted"
            else:
                result["errors"].append(f"Template com slug '{slug}' não encontrado para exclusão")
            return result
        
        # Validate data for upsert
        validation_errors = validate_template_data(row)
        if validation_errors:
            result["errors"] = validation_errors
            return result
        
        # Prepare template data
        template_data = {
            "slug": slug,
            "title": safe_str_strip(row.get('title', '')),
            "description": safe_str_strip_or_none(row.get('description')),
            "platform": safe_str_strip(row.get('platform', '')),
            "author_name": safe_str_strip_or_none(row.get('author_name')),
            "author_email": safe_str_strip_or_none(row.get('author_email')),
            "tutorial_url": safe_str_strip_or_none(row.get('tutorial_url')),
            "preview_image_url": safe_str_strip_or_none(row.get('preview_image_url')),
            "download_url": safe_str_strip_or_none(row.get('download_url')),
            "json_url": safe_str_strip_or_none(row.get('json_url')),
            "language": safe_str_strip(row.get('language', 'pt-BR')) or 'pt-BR',
            "status": safe_str_strip(row.get('status', 'draft')) or 'draft',
            "tags": safe_str_strip_or_none(row.get('tags')),
            "notes": safe_str_strip_or_none(row.get('notes')),
            "external_id": safe_str_strip_or_none(row.get('external_id')),
            "categories": parse_pipe_separated(row.get('categories', '')),
            "tools": parse_pipe_separated(row.get('tools', '')),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Handle numeric fields
        if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
            template_data["rating_avg"] = float(row['rating_avg'])
        
        if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
            template_data["downloads_count"] = int(row['downloads_count'])
        
        # Check if template exists
        existing = supabase.table('templates').select('*').eq('slug', slug).execute()
        
        if existing.data:
            # Update existing template
            update_result = supabase.table('templates').update(template_data).eq('slug', slug).execute()
            result["success"] = True
            result["action"] = "updated"
        else:
            # Insert new template
            template_data["id"] = str(uuid.uuid4())
            template_data["created_at"] = datetime.now(timezone.utc).isoformat()
            template_data.setdefault("downloads_count", 0)
            
            insert_result = supabase.table('templates').insert(template_data).execute()
            result["success"] = True
            result["action"] = "inserted"
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Erro ao processar linha: {str(e)}")
        return result

def get_template_facets() -> TemplateFacets:
    """Get available facets for filtering"""
    try:
        # Get distinct platforms
        platforms_result = supabase.rpc('get_distinct_platforms').execute()
        platforms = platforms_result.data if platforms_result.data else []
        
        # Get distinct categories (we'll use a simple query since Supabase RPC might not be set up)
        templates = supabase.table('templates').select('categories, tools, platform').eq('status', 'published').execute()
        
        all_categories = set()
        all_tools = set()
        all_platforms = set()
        
        for template in templates.data:
            if template.get('categories'):
                all_categories.update(template['categories'])
            if template.get('tools'):
                all_tools.update(template['tools'])
            if template.get('platform'):
                all_platforms.add(template['platform'])
        
        return TemplateFacets(
            platforms=sorted(list(all_platforms)),
            categories=sorted(list(all_categories)),
            tools=sorted(list(all_tools))
        )
    except Exception as e:
        logger.error(f"Error getting facets: {str(e)}")
        return TemplateFacets(platforms=[], categories=[], tools=[])

def get_templates_with_filters(
    search: Optional[str] = None,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    tool: Optional[str] = None,
    page: int = 1,
    page_size: int = 12
) -> PaginatedTemplateResponse:
    """Get templates with filtering and pagination"""
    
    try:
        # Start with base query
        query = supabase.table('templates').select('*', count='exact').eq('status', 'published')
        
        # Add platform filter
        if platform:
            query = query.eq('platform', platform)
        
        # Add category filter
        if category:
            query = query.contains('categories', [category])
        
        # Add tool filter
        if tool:
            query = query.contains('tools', [tool])
        
        # Enhanced search functionality
        if search:
            search_term = search.lower().strip()
            # Use text search on multiple fields with case-insensitive matching
            search_query = f"title.ilike.*{search_term}*,description.ilike.*{search_term}*,tags.ilike.*{search_term}*,author_name.ilike.*{search_term}*,platform.ilike.*{search_term}*"
            query = query.or_(search_query)
        
        # Get total count first
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
        
        # Apply pagination and ordering
        skip = (page - 1) * page_size
        paginated_query = query.order('downloads_count', desc=True).range(skip, skip + page_size - 1)
        
        result = paginated_query.execute()
        templates = result.data
        
        # Convert to Template objects
        template_items = []
        for template in templates:
            # Convert datetime strings back to datetime objects
            if isinstance(template.get('created_at'), str):
                template['created_at'] = datetime.fromisoformat(template['created_at'].replace('Z', '+00:00'))
            if isinstance(template.get('updated_at'), str):
                template['updated_at'] = datetime.fromisoformat(template['updated_at'].replace('Z', '+00:00'))
            template_items.append(Template(**template))
        
        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        
        # Get facets
        facets = get_template_facets()
        
        return PaginatedTemplateResponse(
            items=template_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            facets={
                "platforms": facets.platforms,
                "categories": facets.categories,
                "tools": facets.tools
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return PaginatedTemplateResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0,
            facets={"platforms": [], "categories": [], "tools": []}
        )

# API Endpoints
@api_router.post("/import/templates", response_model=ImportReport)
async def import_templates(file: UploadFile = File(...)):
    """Import templates from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
    
    report = ImportReport()
    
    try:
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_content))
        
        # Validate required columns - MORE FLEXIBLE
        required_columns = ['action']  # Only action is truly required
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Coluna obrigatória ausente: {', '.join(missing_columns)}"
            )
        
        # Auto-add missing common columns with defaults
        if 'slug' not in df.columns and 'key' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="É necessário ter pelo menos uma coluna 'slug' ou 'key' para identificar os registros"
            )
        
        # If we have 'key' but not 'slug', use 'key' as 'slug'
        if 'key' in df.columns and 'slug' not in df.columns:
            df['slug'] = df['key']
        
        # Auto-add missing optional columns with defaults
        optional_defaults = {
            'title': 'Título não informado',
            'platform': 'n8n',
            'status': 'published',
            'description': '',
            'author_name': 'Admin',
            'categories': '',
            'tools': '',
            'rating_avg': '',
            'downloads_count': '0'
        }
        
        for col, default_value in optional_defaults.items():
            if col not in df.columns:
                df[col] = default_value
        
        # Process each row
        for index, row in df.iterrows():
            try:
                action = str(row.get('action', '')).strip().lower()
                
                if action not in ['upsert', 'delete']:
                    report.errors.append(f"Linha {index + 2}: Ação inválida '{action}' (deve ser 'upsert' ou 'delete')")
                    continue
                
                # Process the row
                result = await process_template_row(row.to_dict(), action)
                
                if result["success"]:
                    if result["action"] == "inserted":
                        report.inserted += 1
                    elif result["action"] == "updated":
                        report.updated += 1
                    elif result["action"] == "deleted":
                        report.deleted += 1
                else:
                    for error in result["errors"]:
                        report.errors.append(f"Linha {index + 2}: {error}")
                        
            except Exception as e:
                report.errors.append(f"Linha {index + 2}: Erro inesperado - {str(e)}")
        
        logger.info(f"Import completed: {report.inserted} inserted, {report.updated} updated, {report.deleted} deleted, {len(report.errors)} errors")
        
        return report
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Arquivo CSV está vazio")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao fazer parse do CSV: {str(e)}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Erro de codificação. Arquivo deve estar em UTF-8")
    except Exception as e:
        logger.error(f"Erro inesperado no import: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@api_router.post("/import/preview", response_model=PreviewReport)
async def preview_import(
    file: Optional[UploadFile] = File(None),
    sheet_url: Optional[str] = Form(None)
):
    """Preview CSV import without saving data"""
    
    if not file and not sheet_url:
        raise HTTPException(status_code=400, detail="Deve fornecer um arquivo CSV ou URL do Google Sheets")
    
    if file and sheet_url:
        raise HTTPException(status_code=400, detail="Forneça apenas um arquivo CSV ou URL, não ambos")
    
    report = PreviewReport()
    
    try:
        # Get CSV content
        if file:
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
            
            content = await file.read()
            csv_content = content.decode('utf-8')
        else:
            # Handle Google Sheets URL
            try:
                csv_export_url = convert_google_sheets_url(sheet_url)
                csv_content = await fetch_csv_from_url(csv_export_url)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_content))
        
        # Validate required columns - MORE FLEXIBLE
        required_columns = ['action']  # Only action is truly required
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Coluna obrigatória ausente: {', '.join(missing_columns)}"
            )
        
        # Auto-add missing common columns with defaults
        if 'slug' not in df.columns and 'key' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="É necessário ter pelo menos uma coluna 'slug' ou 'key' para identificar os registros"
            )
        
        # If we have 'key' but not 'slug', use 'key' as 'slug'
        if 'key' in df.columns and 'slug' not in df.columns:
            df['slug'] = df['key']
        
        # Auto-add missing optional columns with defaults
        optional_defaults = {
            'title': 'Título não informado',
            'platform': 'n8n',
            'status': 'published',
            'description': '',
            'author_name': 'Admin',
            'categories': '',
            'tools': '',
            'rating_avg': '',
            'downloads_count': '0'
        }
        
        for col, default_value in optional_defaults.items():
            if col not in df.columns:
                df[col] = default_value
        
        report.total_rows = len(df)
        
        # Preview each row
        for index, row in df.iterrows():
            try:
                action = str(row.get('action', '')).strip().lower()
                line_number = index + 2  # +2 because CSV starts at line 1 and we skip header
                
                if action not in ['upsert', 'delete']:
                    preview_row = PreviewRow(
                        line_number=line_number,
                        slug=safe_str_strip(row.get('slug', '')),
                        title=safe_str_strip(row.get('title', '')),
                        action=action,
                        status="error",
                        message=f"Ação inválida '{action}' (deve ser 'upsert' ou 'delete')"
                    )
                    report.rows.append(preview_row)
                    report.error_count += 1
                    continue
                
                # Preview the row
                preview_row = await preview_template_row(row.to_dict(), action, line_number)
                report.rows.append(preview_row)
                
                # Update counters
                if preview_row.status == "insert":
                    report.insert_count += 1
                elif preview_row.status == "update":
                    report.update_count += 1
                elif preview_row.status == "delete":
                    report.delete_count += 1
                else:
                    report.error_count += 1
                        
            except Exception as e:
                preview_row = PreviewRow(
                    line_number=index + 2,
                    slug=safe_str_strip(row.get('slug', '')),
                    title=safe_str_strip(row.get('title', '')),
                    action=action if 'action' in locals() else 'unknown',
                    status="error",
                    message=f"Erro inesperado: {str(e)}"
                )
                report.rows.append(preview_row)
                report.error_count += 1
        
        logger.info(f"Preview completed: {report.total_rows} rows, {report.insert_count} insert, {report.update_count} update, {report.delete_count} delete, {report.error_count} errors")
        
        return report
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Arquivo CSV está vazio")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao fazer parse do CSV: {str(e)}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Erro de codificação. Arquivo deve estar em UTF-8")
    except Exception as e:
        logger.error(f"Erro inesperado no preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@api_router.get("/templates", response_model=PaginatedTemplateResponse)
async def get_templates(
    search: Optional[str] = Query(None, description="Search in title, description, tags"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tool: Optional[str] = Query(None, description="Filter by tool"),
    user_id: Optional[str] = Query(None, description="User ID for favorites and ratings"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=50, description="Items per page")
):
    """Get templates with advanced filtering, pagination, and user data"""
    return get_templates_with_user_data(
        user_id=user_id,
        search=search,
        platform=platform,
        category=category,
        tool=tool,
        page=page,
        page_size=page_size
    )

@api_router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    result = supabase.table('templates').select('*').eq('id', template_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template = result.data[0]
    # Convert datetime strings
    if isinstance(template.get('created_at'), str):
        template['created_at'] = datetime.fromisoformat(template['created_at'].replace('Z', '+00:00'))
    if isinstance(template.get('updated_at'), str):
        template['updated_at'] = datetime.fromisoformat(template['updated_at'].replace('Z', '+00:00'))
    
    return Template(**template)

@api_router.get("/templates/slug/{slug}", response_model=Template)
async def get_template_by_slug(slug: str):
    result = supabase.table('templates').select('*').eq('slug', slug).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template = result.data[0]
    # Convert datetime strings
    if isinstance(template.get('created_at'), str):
        template['created_at'] = datetime.fromisoformat(template['created_at'].replace('Z', '+00:00'))
    if isinstance(template.get('updated_at'), str):
        template['updated_at'] = datetime.fromisoformat(template['updated_at'].replace('Z', '+00:00'))
    
    return Template(**template)

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    result = supabase.table('categories').select('*').execute()
    return [Category(key=cat['key'], name=cat['name']) for cat in result.data]

@api_router.get("/tools", response_model=List[Tool])
async def get_tools():
    result = supabase.table('tools').select('*').execute()
    return [Tool(key=tool['key'], name=tool['name']) for tool in result.data]

@api_router.get("/featured", response_model=List[Template])
async def get_featured_templates():
    result = supabase.table('templates').select('*').eq('status', 'published').order('rating_avg', desc=True).limit(6).execute()
    
    templates = []
    for template in result.data:
        # Convert datetime strings
        if isinstance(template.get('created_at'), str):
            template['created_at'] = datetime.fromisoformat(template['created_at'].replace('Z', '+00:00'))
        if isinstance(template.get('updated_at'), str):
            template['updated_at'] = datetime.fromisoformat(template['updated_at'].replace('Z', '+00:00'))
        templates.append(Template(**template))
    
    return templates

@api_router.post("/templates/{template_id}/download")
async def download_template(template_id: str):
    # Increment download count
    result = supabase.table('templates').select('downloads_count').eq('id', template_id).execute()
    if result.data:
        current_count = result.data[0].get('downloads_count', 0)
        supabase.table('templates').update({'downloads_count': current_count + 1}).eq('id', template_id).execute()
    
    return {"message": "Download registrado"}

# Import endpoints for specific sections
@api_router.post("/import/platforms/preview", response_model=PreviewReport)
async def preview_platforms_import(
    file: Optional[UploadFile] = File(None),
    sheet_url: Optional[str] = Form(None)
):
    """Preview platforms import without saving data"""
    # Reuse the same logic as templates preview but for platforms
    return await preview_import(file, sheet_url)

@api_router.post("/import/platforms", response_model=ImportReport)
async def import_platforms(file: UploadFile = File(...)):
    """Import platforms from CSV file"""
    # Reuse the same logic as templates import but for platforms
    return await import_templates(file)

@api_router.post("/import/categories/preview", response_model=PreviewReport)
async def preview_categories_import(
    file: Optional[UploadFile] = File(None),
    sheet_url: Optional[str] = Form(None)
):
    """Preview categories import without saving data"""
    return await preview_import(file, sheet_url)

@api_router.post("/import/categories", response_model=ImportReport)
async def import_categories(file: UploadFile = File(...)):
    """Import categories from CSV file"""
    return await import_templates(file)

@api_router.post("/import/tools/preview", response_model=PreviewReport)
async def preview_tools_import(
    file: Optional[UploadFile] = File(None),
    sheet_url: Optional[str] = Form(None)
):
    """Preview tools import without saving data"""
    return await preview_import(file, sheet_url)

@api_router.post("/import/tools", response_model=ImportReport)
async def import_tools(file: UploadFile = File(...)):
    """Import tools from CSV file"""
    return await import_templates(file)

@api_router.post("/import/agents/preview", response_model=PreviewReport)
async def preview_agents_import(
    file: Optional[UploadFile] = File(None),
    sheet_url: Optional[str] = Form(None)
):
    """Preview GPT agents import without saving data"""
    return await preview_import(file, sheet_url)

@api_router.post("/import/agents", response_model=ImportReport)
async def import_agents(file: UploadFile = File(...)):
    """Import GPT agents from CSV file"""
    return await import_templates(file)

@api_router.post("/templates/{template_id}/favorite")
async def toggle_favorite(template_id: str, user_id: str = Form(...)):
    """Toggle favorite status for a template"""
    try:
        # Check if already favorited
        existing = supabase.table('favorites').select('*').eq('user_id', user_id).eq('template_id', template_id).execute()
        
        if existing.data:
            # Remove favorite
            supabase.table('favorites').delete().eq('user_id', user_id).eq('template_id', template_id).execute()
            return {"favorited": False, "message": "Removido dos favoritos"}
        else:
            # Add favorite
            supabase.table('favorites').insert({
                "user_id": user_id,
                "template_id": template_id
            }).execute()
            return {"favorited": True, "message": "Adicionado aos favoritos"}
            
    except Exception as e:
        logger.error(f"Error toggling favorite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao alterar favorito: {str(e)}")

@api_router.post("/templates/{template_id}/rate")
async def rate_template(template_id: str, user_id: str = Form(...), rating: int = Form(...)):
    """Rate a template (1-5 stars)"""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating deve estar entre 1 e 5")
    
    try:
        # Upsert rating (insert or update)
        result = supabase.table('ratings').upsert({
            "user_id": user_id,
            "template_id": template_id,
            "rating": rating,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        return {"success": True, "rating": rating, "message": f"Avaliação de {rating} estrelas registrada"}
        
    except Exception as e:
        logger.error(f"Error rating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao avaliar template: {str(e)}")

@api_router.get("/user/{user_id}/favorites")
async def get_user_favorites(user_id: str):
    """Get user's favorite templates"""
    try:
        result = supabase.table('favorites').select('template_id').eq('user_id', user_id).execute()
        template_ids = [fav['template_id'] for fav in result.data]
        return {"template_ids": template_ids}
    except Exception as e:
        logger.error(f"Error getting favorites: {str(e)}")
        return {"template_ids": []}

def get_templates_with_user_data(
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    tool: Optional[str] = None,
    page: int = 1,
    page_size: int = 15  # Changed default to 15
) -> PaginatedTemplateResponse:
    """Get templates with user-specific data (favorites, ratings)"""
    
    try:
        # Start with base query
        query = supabase.table('templates').select('*', count='exact').eq('status', 'published')
        
        # Add platform filter
        if platform:
            query = query.eq('platform', platform)
        
        # Add category filter
        if category:
            query = query.contains('categories', [category])
        
        # Add tool filter
        if tool:
            query = query.contains('tools', [tool])
        
        # Enhanced search functionality
        if search:
            search_term = search.lower().strip()
            search_query = f"title.ilike.*{search_term}*,description.ilike.*{search_term}*,tags.ilike.*{search_term}*,author_name.ilike.*{search_term}*,platform.ilike.*{search_term}*"
            query = query.or_(search_query)
        
        # Get total count first
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
        
        # Apply pagination and ordering
        skip = (page - 1) * page_size
        paginated_query = query.order('downloads_count', desc=True).range(skip, skip + page_size - 1)
        
        result = paginated_query.execute()
        templates = result.data
        
        # Get user favorites and ratings if user_id provided
        user_favorites = set()
        user_ratings = {}
        
        if user_id:
            try:
                # Get user favorites
                favorites_result = supabase.table('favorites').select('template_id').eq('user_id', user_id).execute()
                user_favorites = {fav['template_id'] for fav in favorites_result.data}
                
                # Get user ratings
                ratings_result = supabase.table('ratings').select('template_id, rating').eq('user_id', user_id).execute()
                user_ratings = {rating['template_id']: rating['rating'] for rating in ratings_result.data}
            except Exception as e:
                logger.error(f"Error getting user data: {str(e)}")
        
        # Convert to Template objects with user data
        template_items = []
        for template in templates:
            # Convert datetime strings back to datetime objects
            if isinstance(template.get('created_at'), str):
                template['created_at'] = datetime.fromisoformat(template['created_at'].replace('Z', '+00:00'))
            if isinstance(template.get('updated_at'), str):
                template['updated_at'] = datetime.fromisoformat(template['updated_at'].replace('Z', '+00:00'))
            
            # Add user-specific data
            template['is_favorited'] = template['id'] in user_favorites
            template['user_rating'] = user_ratings.get(template['id'])
            
            template_items.append(TemplateWithUserData(**template))
        
        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        
        # Get facets
        facets = get_template_facets()
        
        return PaginatedTemplateResponse(
            items=template_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            facets={
                "platforms": facets.platforms,
                "categories": facets.categories,
                "tools": facets.tools
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting templates with user data: {str(e)}")
        return PaginatedTemplateResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0,
            facets={"platforms": [], "categories": [], "tools": []}
        )

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)