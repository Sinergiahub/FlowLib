-- FlowLib Supabase Schema
-- Drop existing tables if they exist
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS tools CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    display_name TEXT NOT NULL,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'pro', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
    key TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tools table
CREATE TABLE tools (
    key TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Templates table
CREATE TABLE templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    platform TEXT NOT NULL,
    author_name TEXT,
    author_email TEXT,
    tutorial_url TEXT,
    preview_image_url TEXT,
    download_url TEXT,
    json_url TEXT,
    language TEXT DEFAULT 'pt-BR',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    rating_avg DECIMAL(3,2) CHECK (rating_avg >= 0 AND rating_avg <= 5),
    downloads_count INTEGER DEFAULT 0 CHECK (downloads_count >= 0),
    tags TEXT,
    notes TEXT,
    external_id TEXT,
    categories TEXT[] DEFAULT '{}',
    tools TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_templates_slug ON templates(slug);
CREATE INDEX idx_templates_platform ON templates(platform);
CREATE INDEX idx_templates_status ON templates(status);
CREATE INDEX idx_templates_categories ON templates USING GIN(categories);
CREATE INDEX idx_templates_tools ON templates USING GIN(tools);
CREATE INDEX idx_templates_downloads ON templates(downloads_count DESC);
CREATE INDEX idx_templates_rating ON templates(rating_avg DESC);
CREATE INDEX idx_templates_created ON templates(created_at DESC);

-- Insert initial categories
INSERT INTO categories (key, name) VALUES 
('produtividade', 'Produtividade'),
('marketing', 'Marketing'),
('vendas', 'Vendas'),
('redes-sociais', 'Redes Sociais'),
('atendimento', 'Atendimento'),
('leads', 'Geração de Leads'),
('pesquisa', 'Pesquisa'),
('ecommerce', 'E-commerce'),
('financas', 'Finanças');

-- Insert initial tools
INSERT INTO tools (key, name) VALUES 
('openai', 'OpenAI'),
('slack', 'Slack'),
('google-sheets', 'Google Sheets'),
('webflow', 'Webflow'),
('voiceflow', 'Voiceflow'),
('adzuna', 'Adzuna API'),
('make', 'Make'),
('zapier', 'Zapier'),
('n8n', 'n8n'),
('telegram', 'Telegram'),
('discord', 'Discord'),
('notion', 'Notion'),
('airtable', 'Airtable'),
('stripe', 'Stripe'),
('gmail', 'Gmail');

-- Insert sample templates
INSERT INTO templates (
    id, slug, title, description, platform, author_name, 
    preview_image_url, tutorial_url, downloads_count, rating_avg, 
    categories, tools, status
) VALUES 
(
    gen_random_uuid(),
    'assistente-virtual-tiktok',
    'Assistente Virtual para TikTok',
    'Sistema completo de IA que gera clips virais do TikTok automaticamente, criando conteúdo envolvente a partir de temas populares.',
    'n8n',
    'AutoFlow Pro',
    'https://images.unsplash.com/photo-1531403009284-440f080d1e12',
    'https://youtube.com/watch?v=demo1',
    2847,
    4.8,
    '{"redes-sociais", "marketing"}',
    '{"openai", "n8n"}',
    'published'
),
(
    gen_random_uuid(),
    '6k-por-mes-ia',
    '$6k Por Mês com IA',
    'Template de automação para geração de renda usando IA. Criação de modelos de negócio escaláveis com inteligência artificial.',
    'Make',
    'AI Revenue',
    'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b',
    'https://youtube.com/watch?v=demo2',
    1923,
    4.7,
    '{"produtividade", "vendas"}',
    '{"openai", "make"}',
    'published'
),
(
    gen_random_uuid(),
    '100-automacao-seo',
    '100% Automação SEO',
    'Sistema de automação completo para SEO. Análise de palavras-chave, criação de conteúdo e otimização automática de sites.',
    'Zapier',
    'SEO Master',
    'https://images.unsplash.com/photo-1518770660439-4636190af475',
    'https://youtube.com/watch?v=demo3',
    3156,
    4.9,
    '{"marketing", "produtividade"}',
    '{"openai", "google-sheets", "zapier"}',
    'published'
);

-- Enable RLS (Row Level Security) - optional for future auth
-- ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;