import { Template, Category, Tool, Platform } from '../types';

// Mock Categories
export const mockCategories: Category[] = [
  {
    id: 'produtividade',
    name: 'Produtividade',
    slug: 'produtividade',
    description: 'Automações para otimizar tarefas e aumentar eficiência',
    color: '#3B82F6'
  },
  {
    id: 'marketing',
    name: 'Marketing',
    slug: 'marketing',
    description: 'Automações para marketing digital e geração de leads',
    color: '#EF4444'
  },
  {
    id: 'ecommerce',
    name: 'E-commerce',
    slug: 'ecommerce',
    description: 'Automações para lojas online e vendas',
    color: '#10B981'
  },
  {
    id: 'redes-sociais',
    name: 'Redes Sociais',
    slug: 'redes-sociais',
    description: 'Automações para gestão de mídias sociais',
    color: '#8B5CF6'
  },
  {
    id: 'financas',
    name: 'Finanças',
    slug: 'financas',
    description: 'Automações para controle financeiro e contabilidade',
    color: '#F59E0B'
  },
  {
    id: 'atendimento',
    name: 'Atendimento',
    slug: 'atendimento',
    description: 'Automações para suporte ao cliente',
    color: '#06B6D4'
  }
];

// Mock Tools
export const mockTools: Tool[] = [
  { id: 'openai', name: 'OpenAI', slug: 'openai', icon: '🤖', color: '#10A37F' },
  { id: 'google-sheets', name: 'Google Sheets', slug: 'google-sheets', icon: '📊', color: '#34A853' },
  { id: 'slack', name: 'Slack', slug: 'slack', icon: '💬', color: '#4A154B' },
  { id: 'telegram', name: 'Telegram', slug: 'telegram', icon: '✈️', color: '#0088CC' },
  { id: 'discord', name: 'Discord', slug: 'discord', icon: '🎮', color: '#5865F2' },
  { id: 'notion', name: 'Notion', slug: 'notion', icon: '📝', color: '#000000' },
  { id: 'airtable', name: 'Airtable', slug: 'airtable', icon: '🗃️', color: '#18BFFF' },
  { id: 'webflow', name: 'Webflow', slug: 'webflow', icon: '🌐', color: '#4353FF' },
  { id: 'stripe', name: 'Stripe', slug: 'stripe', icon: '💳', color: '#008CDD' },
  { id: 'gmail', name: 'Gmail', slug: 'gmail', icon: '📧', color: '#EA4335' }
];

// Mock Templates
export const mockTemplates: Template[] = [
  {
    id: '1',
    title: 'Assistente Virtual para TikTok com IA',
    slug: 'assistente-virtual-tiktok-ia',
    description: 'Sistema completo de inteligência artificial que automatiza a criação de conteúdo viral para TikTok. Analisa tendências, gera scripts envolventes e otimiza o timing de publicação para maximizar alcance e engajamento.',
    shortDescription: 'Crie conteúdo viral automaticamente para TikTok usando IA avançada',
    platform: 'n8n' as Platform,
    author: 'AutoFlow Pro',
    authorAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/tiktok-assistant.json',
    status: 'published' as const,
    downloadCount: 2847,
    rating: 4.8,
    ratingCount: 234,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-02-20T15:30:00Z',
    categories: [mockCategories[1], mockCategories[3]], // Marketing, Redes Sociais
    tools: [mockTools[0], mockTools[4]], // OpenAI, Discord
    isFavorited: false
  },
  {
    id: '2',
    title: 'Gerador de Renda com IA - $6k/mês',
    slug: 'gerador-renda-ia-6k-mes',
    description: 'Template completo para criar múltiplas fontes de renda usando inteligência artificial. Inclui automações para criação de conteúdo, vendas online, atendimento ao cliente e análise de mercado. Sistema testado e aprovado por centenas de empreendedores.',
    shortDescription: 'Sistema completo para gerar renda automatizada com IA',
    platform: 'Make' as Platform,
    author: 'AI Revenue Lab',
    authorAvatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/ai-revenue-generator.json',
    status: 'published' as const,
    downloadCount: 1923,
    rating: 4.7,
    ratingCount: 156,
    createdAt: '2024-01-22T14:00:00Z',
    updatedAt: '2024-03-01T09:15:00Z',
    categories: [mockCategories[0], mockCategories[1]], // Produtividade, Marketing
    tools: [mockTools[0], mockTools[1], mockTools[8]], // OpenAI, Google Sheets, Stripe
    isFavorited: true
  },
  {
    id: '3',
    title: 'SEO Automático 100% - Dominação Orgânica',
    slug: 'seo-automatico-100-dominacao-organica',
    description: 'Sistema de automação SEO mais avançado do mercado. Realiza pesquisa de palavras-chave, cria conteúdo otimizado, monitora concorrentes, constrói backlinks naturais e acompanha rankings em tempo real. Ideal para agências e profissionais de marketing.',
    shortDescription: 'Automação completa de SEO para dominar os resultados de busca',
    platform: 'Zapier' as Platform,
    author: 'SEO Master Agency',
    authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/seo-automation.json',
    status: 'published' as const,
    downloadCount: 3156,
    rating: 4.9,
    ratingCount: 298,
    createdAt: '2024-02-01T08:30:00Z',
    updatedAt: '2024-03-10T16:45:00Z',
    categories: [mockCategories[1], mockCategories[0]], // Marketing, Produtividade
    tools: [mockTools[0], mockTools[1], mockTools[5]], // OpenAI, Google Sheets, Notion
    isFavorited: false
  },
  {
    id: '4',
    title: 'Chatbot Inteligente para E-commerce',
    slug: 'chatbot-inteligente-ecommerce',
    description: 'Chatbot avançado com IA para lojas online que automatiza atendimento 24/7, resolve dúvidas sobre produtos, processa pedidos, calcula fretes e oferece suporte pós-venda. Integração nativa com principais plataformas de e-commerce brasileiras.',
    shortDescription: 'Atendimento automatizado inteligente para sua loja online',
    platform: 'Voiceflow' as Platform,
    author: 'E-commerce Solutions',
    authorAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b332e234?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/ecommerce-chatbot.json',
    status: 'published' as const,
    downloadCount: 1456,
    rating: 4.6,
    ratingCount: 127,
    createdAt: '2024-02-10T11:15:00Z',
    updatedAt: '2024-03-15T14:20:00Z',
    categories: [mockCategories[2], mockCategories[5]], // E-commerce, Atendimento
    tools: [mockTools[0], mockTools[2], mockTools[8]], // OpenAI, Slack, Stripe
    isFavorited: false
  },
  {
    id: '5',
    title: 'Análise Financeira Automatizada com IA',
    slug: 'analise-financeira-automatizada-ia',
    description: 'Sistema completo de análise financeira que coleta dados de múltiplas fontes, categoriza transações automaticamente, gera relatórios detalhados e identifica oportunidades de economia. Inclui alertas inteligentes e previsões baseadas em IA.',
    shortDescription: 'Controle financeiro inteligente com análises automáticas',
    platform: 'n8n' as Platform,
    author: 'FinTech Automations',
    authorAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/financial-analysis.json',
    status: 'published' as const,
    downloadCount: 987,
    rating: 4.5,
    ratingCount: 89,
    createdAt: '2024-02-18T13:45:00Z',
    updatedAt: '2024-03-20T10:30:00Z',
    categories: [mockCategories[4], mockCategories[0]], // Finanças, Produtividade
    tools: [mockTools[0], mockTools[1], mockTools[6]], // OpenAI, Google Sheets, Airtable
    isFavorited: true
  },
  {
    id: '6',
    title: 'Automação Completa de Instagram',
    slug: 'automacao-completa-instagram',
    description: 'Suite completa para automatizar sua presença no Instagram. Programa posts, responde DMs automaticamente, monitora menções, analisa métricas de engajamento e identifica os melhores horários para publicação. Perfeito para influencers e marcas.',
    shortDescription: 'Gerencie seu Instagram no piloto automático',
    platform: 'Make' as Platform,
    author: 'Social Media Pro',
    authorAvatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/instagram-automation.json',
    status: 'published' as const,
    downloadCount: 2134,
    rating: 4.7,
    ratingCount: 178,
    createdAt: '2024-02-25T16:20:00Z',
    updatedAt: '2024-03-25T12:10:00Z',
    categories: [mockCategories[3], mockCategories[1]], // Redes Sociais, Marketing
    tools: [mockTools[0], mockTools[6], mockTools[5]], // OpenAI, Airtable, Notion
    isFavorited: false
  },
  {
    id: '7',
    title: 'Lead Magnet Inteligente com Follow-up',
    slug: 'lead-magnet-inteligente-followup',
    description: 'Sistema automatizado de captação e nutrição de leads que cria iscas digitais personalizadas, captura dados de prospects, envia sequências de e-mail inteligentes e pontua leads automaticamente. Perfeito para consultores e agências.',
    shortDescription: 'Capture e nutra leads automaticamente com IA',
    platform: 'Zapier' as Platform,
    author: 'Lead Generation Hub',
    authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/lead-magnet-system.json',
    status: 'published' as const,
    downloadCount: 1678,
    rating: 4.8,
    ratingCount: 142,
    createdAt: '2024-03-01T09:30:00Z',
    updatedAt: '2024-03-28T15:45:00Z',
    categories: [mockCategories[1], mockCategories[0]], // Marketing, Produtividade
    tools: [mockTools[0], mockTools[9], mockTools[7]], // OpenAI, Gmail, Webflow
    isFavorited: true
  },
  {
    id: '8',
    title: 'Automação de Vendas B2B Avançada',
    slug: 'automacao-vendas-b2b-avancada',
    description: 'Pipeline completo de vendas B2B automatizado que qualifica prospects, envia propostas personalizadas, agenda reuniões automaticamente e acompanha todo o ciclo de vendas. Inclui CRM integrado e relatórios de performance.',
    shortDescription: 'Pipeline de vendas B2B 100% automatizado',
    platform: 'n8n' as Platform,
    author: 'B2B Sales Expert',
    authorAvatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop&crop=face',
    previewUrl: 'https://images.unsplash.com/photo-1553028826-f4804a6dba3b',
    tutorialUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    fileUrl: '/templates/b2b-sales-automation.json',
    status: 'published' as const,
    downloadCount: 892,
    rating: 4.6,
    ratingCount: 76,
    createdAt: '2024-03-05T14:15:00Z',
    updatedAt: '2024-03-30T11:25:00Z',
    categories: [mockCategories[1], mockCategories[0]], // Marketing, Produtividade
    tools: [mockTools[0], mockTools[1], mockTools[2]], // OpenAI, Google Sheets, Slack
    isFavorited: false
  }
];

// Helper functions
export const getTemplateBySlug = (slug: string): Template | undefined => {
  return mockTemplates.find(template => template.slug === slug);
};

export const getFeaturedTemplates = (limit: number = 6): Template[] => {
  return mockTemplates
    .filter(template => template.rating >= 4.6)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit);
};

export const filterTemplates = (filters: Partial<{
  platforms: Platform[];
  categories: string[];
  tools: string[];
  search: string;
}>): Template[] => {
  let filtered = [...mockTemplates];

  if (filters.platforms?.length) {
    filtered = filtered.filter(template => 
      filters.platforms!.includes(template.platform)
    );
  }

  if (filters.categories?.length) {
    filtered = filtered.filter(template =>
      template.categories.some(cat => filters.categories!.includes(cat.id))
    );
  }

  if (filters.tools?.length) {
    filtered = filtered.filter(template =>
      template.tools.some(tool => filters.tools!.includes(tool.id))
    );
  }

  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(template =>
      template.title.toLowerCase().includes(searchLower) ||
      template.description.toLowerCase().includes(searchLower) ||
      template.shortDescription.toLowerCase().includes(searchLower)
    );
  }

  return filtered;
};