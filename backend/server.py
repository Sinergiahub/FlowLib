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

# Initialize sample data
@app.on_event("startup")
async def startup_db():
    # Categories
    categories = [
        {"id": "produtividade", "name": "Produtividade", "slug": "produtividade", "description": "Automações para otimizar tarefas"},
        {"id": "marketing", "name": "Marketing", "slug": "marketing", "description": "Automações para marketing digital"},
        {"id": "vendas", "name": "Vendas", "slug": "vendas", "description": "Automações para processos de venda"},
        {"id": "redes-sociais", "name": "Redes Sociais", "slug": "redes-sociais", "description": "Automações para social media"},
        {"id": "atendimento", "name": "Atendimento", "slug": "atendimento", "description": "Automações para suporte ao cliente"},
        {"id": "leads", "name": "Geração de Leads", "slug": "leads", "description": "Automações para captura de leads"},
        {"id": "pesquisa", "name": "Pesquisa", "slug": "pesquisa", "description": "Automações para coleta de dados"}
    ]
    
    # Tools
    tools = [
        {"id": "openai", "name": "OpenAI", "slug": "openai"},
        {"id": "slack", "name": "Slack", "slug": "slack"},
        {"id": "google-sheets", "name": "Google Sheets", "slug": "google-sheets"},
        {"id": "webflow", "name": "Webflow", "slug": "webflow"},
        {"id": "voiceflow", "name": "Voiceflow", "slug": "voiceflow"},
        {"id": "adzuna", "name": "Adzuna API", "slug": "adzuna"},
        {"id": "make", "name": "Make", "slug": "make"},
        {"id": "zapier", "name": "Zapier", "slug": "zapier"},
        {"id": "n8n", "name": "n8n", "slug": "n8n"}
    ]
    
    # Templates
    templates = [
        {
            "id": str(uuid.uuid4()),
            "title": "Assistente Virtual para TikTok",
            "slug": "assistente-virtual-tiktok",
            "description": "Sistema completo de IA que gera clips virais do TikTok automaticamente, criando conteúdo envolvente a partir de temas populares.",
            "platform": "n8n",
            "author_name": "AutoFlow Pro",
            "preview_url": "https://images.unsplash.com/photo-1531403009284-440f080d1e12",
            "tutorial_url": "https://youtube.com/watch?v=demo1",
            "downloads_count": 2847,
            "rating_avg": 4.8,
            "categories": ["redes-sociais", "marketing"],
            "tools": ["openai", "n8n"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "$6k Por Mês com IA",
            "slug": "6k-por-mes-ia",
            "description": "Template de automação para geração de renda usando IA. Criação de modelos de negócio escaláveis com inteligência artificial.",
            "platform": "Make",
            "author_name": "AI Revenue",
            "preview_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
            "tutorial_url": "https://youtube.com/watch?v=demo2",
            "downloads_count": 1923,
            "rating_avg": 4.7,
            "categories": ["produtividade", "vendas"],
            "tools": ["openai", "make"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "100% Automação SEO",
            "slug": "100-automacao-seo",
            "description": "Sistema de automação completo para SEO. Análise de palavras-chave, criação de conteúdo e otimização automática de sites.",
            "platform": "Zapier",
            "author_name": "SEO Master",
            "preview_url": "https://images.unsplash.com/photo-1518770660439-4636190af475",
            "tutorial_url": "https://youtube.com/watch?v=demo3",
            "downloads_count": 3156,
            "rating_avg": 4.9,
            "categories": ["marketing", "produtividade"],
            "tools": ["openai", "google-sheets", "zapier"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Análise de Vídeos com IA",
            "slug": "analise-videos-ia",
            "description": "Ferramenta avançada de análise de vídeos usando IA. Extração de insights, legendas automáticas e métricas de engajamento.",
            "platform": "n8n",
            "author_name": "Video AI Lab",
            "preview_url": "https://images.unsplash.com/photo-1531297484001-80022131f5a1",
            "tutorial_url": "https://youtube.com/watch?v=demo4",
            "downloads_count": 1567,
            "rating_avg": 4.6,
            "categories": ["redes-sociais", "pesquisa"],
            "tools": ["openai", "n8n"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Chatbot para Agência de Viagens",
            "slug": "chatbot-agencia-viagens",
            "description": "Chatbot inteligente para agências de viagens. Coleta leads, responde dúvidas sobre destinos e facilita o processo de reserva.",
            "platform": "Voiceflow",
            "author_name": "Travel Bot",
            "preview_url": "https://images.unsplash.com/photo-1743385779347-1549dabf1320",
            "tutorial_url": "https://youtube.com/watch?v=demo5",
            "downloads_count": 892,
            "rating_avg": 4.5,
            "categories": ["atendimento", "leads"],
            "tools": ["voiceflow", "google-sheets"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Follow-up Inteligente de Leads",
            "slug": "followup-inteligente-leads",
            "description": "Sistema automatizado de follow-up de leads com IA. Personalização de mensagens e acompanhamento de conversões.",
            "platform": "Make",
            "author_name": "Lead Master",
            "preview_url": "https://images.unsplash.com/photo-1542744094-24638eff58bb",
            "tutorial_url": "https://youtube.com/watch?v=demo6",
            "downloads_count": 2134,
            "rating_avg": 4.8,
            "categories": ["marketing", "leads", "vendas"],
            "tools": ["openai", "slack", "webflow"],
            "status": "published",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Insert data if collections are empty
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many(categories)
    
    if await db.tools.count_documents({}) == 0:
        await db.tools.insert_many(tools)
    
    if await db.templates.count_documents({}) == 0:
        await db.templates.insert_many(templates)

# Routes
@api_router.get("/")
async def root():
    return {"message": "FlowLib API - Biblioteca de Automações"}

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