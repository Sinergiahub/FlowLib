from fastapi import FastAPI, APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
# Models
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

class TemplateCreate(BaseModel):
    title: str
    description: str
    platform: str
    author_name: str = "Community"
    categories: List[str] = []
    tools: List[str] = []

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

# Initialize collections and sample data
@app.on_event("startup")
async def startup_db():
    # Categories
    categories = [
        {"key": "produtividade", "name": "Produtividade"},
        {"key": "marketing", "name": "Marketing"},
        {"key": "vendas", "name": "Vendas"},
        {"key": "redes-sociais", "name": "Redes Sociais"},
        {"key": "atendimento", "name": "Atendimento"},
        {"key": "leads", "name": "Geração de Leads"},
        {"key": "pesquisa", "name": "Pesquisa"},
        {"key": "ecommerce", "name": "E-commerce"},
        {"key": "financas", "name": "Finanças"}
    ]
    
    # Tools
    tools = [
        {"key": "openai", "name": "OpenAI"},
        {"key": "slack", "name": "Slack"},
        {"key": "google-sheets", "name": "Google Sheets"},
        {"key": "webflow", "name": "Webflow"},
        {"key": "voiceflow", "name": "Voiceflow"},
        {"key": "adzuna", "name": "Adzuna API"},
        {"key": "make", "name": "Make"},
        {"key": "zapier", "name": "Zapier"},
        {"key": "n8n", "name": "n8n"},
        {"key": "telegram", "name": "Telegram"},
        {"key": "discord", "name": "Discord"},
        {"key": "notion", "name": "Notion"},
        {"key": "airtable", "name": "Airtable"},
        {"key": "stripe", "name": "Stripe"},
        {"key": "gmail", "name": "Gmail"}
    ]
    
    # Templates (existing ones converted to new schema)
    templates = [
        {
            "id": str(uuid.uuid4()),
            "slug": "assistente-virtual-tiktok",
            "title": "Assistente Virtual para TikTok",
            "description": "Sistema completo de IA que gera clips virais do TikTok automaticamente, criando conteúdo envolvente a partir de temas populares.",
            "platform": "n8n",
            "author_name": "AutoFlow Pro",
            "preview_image_url": "https://images.unsplash.com/photo-1531403009284-440f080d1e12",
            "tutorial_url": "https://youtube.com/watch?v=demo1",
            "downloads_count": 2847,
            "rating_avg": 4.8,
            "categories": ["redes-sociais", "marketing"],
            "tools": ["openai", "n8n"],
            "status": "published",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "6k-por-mes-ia",
            "title": "$6k Por Mês com IA",
            "description": "Template de automação para geração de renda usando IA. Criação de modelos de negócio escaláveis com inteligência artificial.",
            "platform": "Make",
            "author_name": "AI Revenue",
            "preview_image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
            "tutorial_url": "https://youtube.com/watch?v=demo2",
            "downloads_count": 1923,
            "rating_avg": 4.7,
            "categories": ["produtividade", "vendas"],
            "tools": ["openai", "make"],
            "status": "published",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "100-automacao-seo",
            "title": "100% Automação SEO",
            "description": "Sistema de automação completo para SEO. Análise de palavras-chave, criação de conteúdo e otimização automática de sites.",
            "platform": "Zapier",
            "author_name": "SEO Master",
            "preview_image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475",
            "tutorial_url": "https://youtube.com/watch?v=demo3",
            "downloads_count": 3156,
            "rating_avg": 4.9,
            "categories": ["marketing", "produtividade"],
            "tools": ["openai", "google-sheets", "zapier"],
            "status": "published",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    # Insert data if collections are empty
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many(categories)
    
    if await db.tools.count_documents({}) == 0:
        await db.tools.insert_many(tools)
    
    if await db.templates.count_documents({}) == 0:
        await db.templates.insert_many(templates)

# CSV Import utilities
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
    """Validate template data and return list of errors"""
    errors = []
    
    # Required fields
    if not row.get('slug'):
        errors.append("Slug é obrigatório")
    elif not re.match(r'^[a-z0-9-]+$', str(row['slug'])):
        errors.append(f"Slug inválido: {row['slug']} (deve conter apenas letras minúsculas, números e hífens)")
    
    if not row.get('platform'):
        errors.append("Platform é obrigatório")
    
    # URL validation
    url_fields = ['tutorial_url', 'preview_image_url', 'download_url', 'json_url']
    for field in url_fields:
        url = row.get(field)
        if url and not pd.isna(url) and url.strip():
            url_str = str(url).strip()
            if not (url_str.startswith('http://') or url_str.startswith('https://')):
                errors.append(f"{field} deve começar com http:// ou https://: {url_str}")
    
    # Rating validation
    if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
        try:
            rating = float(row['rating_avg'])
            if rating < 0 or rating > 5:
                errors.append(f"rating_avg deve estar entre 0 e 5: {rating}")
        except (ValueError, TypeError):
            errors.append(f"rating_avg deve ser um número: {row['rating_avg']}")
    
    # Downloads validation
    if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
        try:
            downloads = int(row['downloads_count'])
            if downloads < 0:
                errors.append(f"downloads_count deve ser >= 0: {downloads}")
        except (ValueError, TypeError):
            errors.append(f"downloads_count deve ser um número: {row['downloads_count']}")
    
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
    """Preview a single template row without saving"""
    
    slug = safe_str_strip(row.get('slug', ''))
    title = safe_str_strip(row.get('title', ''))
    
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
            preview_row.message = "Slug é obrigatório"
            return preview_row
        
        if action == "delete":
            # Check if template exists for deletion
            existing = await db.templates.find_one({"slug": slug})
            if existing:
                preview_row.status = "delete"
                preview_row.message = f"Template '{title or slug}' será deletado"
            else:
                preview_row.message = f"Template com slug '{slug}' não encontrado para exclusão"
            return preview_row
        
        # Validate data for upsert
        validation_errors = validate_template_data(row)
        if validation_errors:
            preview_row.message = "; ".join(validation_errors)
            return preview_row
        
        # Check if template exists
        existing = await db.templates.find_one({"slug": slug})
        
        # Prepare preview data
        preview_data = {
            "slug": slug,
            "title": title,
            "platform": safe_str_strip(row.get('platform', '')),
            "author_name": safe_str_strip_or_none(row.get('author_name')),
            "categories": parse_pipe_separated(row.get('categories', '')),
            "tools": parse_pipe_separated(row.get('tools', '')),
        }
        
        # Add rating and downloads if present
        if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
            preview_data["rating_avg"] = float(row['rating_avg'])
        
        if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
            preview_data["downloads_count"] = int(row['downloads_count'])
        
        preview_row.data = preview_data
        
        if existing:
            preview_row.status = "update"
            preview_row.message = f"Template '{title}' será atualizado"
        else:
            preview_row.status = "insert"
            preview_row.message = f"Template '{title}' será inserido"
        
        return preview_row
        
    except Exception as e:
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
            delete_result = await db.templates.delete_one({"slug": slug})
            if delete_result.deleted_count > 0:
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
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Handle numeric fields
        if 'rating_avg' in row and row['rating_avg'] is not None and not pd.isna(row['rating_avg']):
            template_data["rating_avg"] = float(row['rating_avg'])
        
        if 'downloads_count' in row and row['downloads_count'] is not None and not pd.isna(row['downloads_count']):
            template_data["downloads_count"] = int(row['downloads_count'])
        
        # Check if template exists
        existing = await db.templates.find_one({"slug": slug})
        
        if existing:
            # Update existing template
            await db.templates.update_one(
                {"slug": slug},
                {"$set": template_data}
            )
            result["success"] = True
            result["action"] = "updated"
        else:
            # Insert new template
            template_data["id"] = str(uuid.uuid4())
            template_data["created_at"] = datetime.now(timezone.utc)
            template_data.setdefault("downloads_count", 0)
            
            await db.templates.insert_one(template_data)
            result["success"] = True
            result["action"] = "inserted"
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Erro ao processar linha: {str(e)}")
        return result

async def get_template_facets() -> TemplateFacets:
    """Get available facets for filtering"""
    try:
        # Get distinct platforms
        platforms = await db.templates.distinct("platform", {"status": "published"})
        
        # Get distinct categories from all templates
        categories_pipeline = [
            {"$match": {"status": "published"}},
            {"$unwind": "$categories"},
            {"$group": {"_id": "$categories"}},
            {"$sort": {"_id": 1}}
        ]
        categories_result = await db.templates.aggregate(categories_pipeline).to_list(None)
        categories = [item["_id"] for item in categories_result if item["_id"]]
        
        # Get distinct tools from all templates
        tools_pipeline = [
            {"$match": {"status": "published"}},
            {"$unwind": "$tools"},
            {"$group": {"_id": "$tools"}},
            {"$sort": {"_id": 1}}
        ]
        tools_result = await db.templates.aggregate(tools_pipeline).to_list(None)
        tools = [item["_id"] for item in tools_result if item["_id"]]
        
        return TemplateFacets(
            platforms=sorted(platforms) if platforms else [],
            categories=categories,
            tools=tools
        )
    except Exception as e:
        logger.error(f"Error getting facets: {str(e)}")
        return TemplateFacets(platforms=[], categories=[], tools=[])

async def get_templates_with_filters(
    search: Optional[str] = None,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    tool: Optional[str] = None,
    page: int = 1,
    page_size: int = 12
) -> PaginatedTemplateResponse:
    """Get templates with filtering and pagination"""
    
    # Build filter query
    filter_query = {"status": "published"}
    
    # Add platform filter
    if platform:
        filter_query["platform"] = platform
    
    # Add category filter
    if category:
        filter_query["categories"] = {"$in": [category]}
    
    # Add tool filter  
    if tool:
        filter_query["tools"] = {"$in": [tool]}
    
    # Add search filter
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        filter_query["$or"] = [
            {"title": search_regex},
            {"description": search_regex},
            {"tags": search_regex}
        ]
    
    try:
        # Get total count
        total = await db.templates.count_documents(filter_query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        
        # Get templates with pagination
        templates_cursor = db.templates.find(filter_query).sort("downloads_count", -1).skip(skip).limit(page_size)
        templates = await templates_cursor.to_list(page_size)
        
        # Convert to Template objects
        template_items = [Template(**template) for template in templates]
        
        # Get facets
        facets = await get_template_facets()
        
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
    return {"message": "AutomaçãoHub API - Biblioteca de Automações"}

# CSV Import endpoint
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
        
        # Validate required columns
        required_columns = ['action', 'slug']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
            )
        
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

# CSV Import Preview endpoint
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
        
        # Validate required columns
        required_columns = ['action', 'slug']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
            )
        
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

# Existing endpoints with updated schema
@api_router.get("/templates", response_model=List[Template])
async def get_templates(
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tool: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    filter_query = {"status": "published"}
    
    if platform:
        filter_query["platform"] = platform
    if category:
        filter_query["categories"] = {"$in": [category]}
    if tool:
        filter_query["tools"] = {"$in": [tool]}
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    templates = await db.templates.find(filter_query).sort("downloads_count", -1).limit(limit).to_list(limit)
    return [Template(**template) for template in templates]

@api_router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return Template(**template)

@api_router.get("/templates/slug/{slug}", response_model=Template)
async def get_template_by_slug(slug: str):
    template = await db.templates.find_one({"slug": slug})
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return Template(**template)

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    categories = await db.categories.find().to_list(100)
    return [Category(**category) for category in categories]

@api_router.get("/tools", response_model=List[Tool])
async def get_tools():
    tools = await db.tools.find().to_list(100)
    return [Tool(**tool) for tool in tools]

@api_router.get("/featured", response_model=List[Template])
async def get_featured_templates():
    templates = await db.templates.find({"status": "published"}).sort("rating_avg", -1).limit(6).to_list(6)
    return [Template(**template) for template in templates]

@api_router.post("/templates/{template_id}/download")
async def download_template(template_id: str):
    # Increment download count
    await db.templates.update_one(
        {"id": template_id},
        {"$inc": {"downloads_count": 1}}
    )
    return {"message": "Download registrado"}

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()