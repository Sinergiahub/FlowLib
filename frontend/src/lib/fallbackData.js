// Fallback data to use when database is empty
export const fallbackTemplates = [
  {
    id: 'fallback-1',
    title: 'Assistente Virtual para TikTok com IA',
    slug: 'assistente-virtual-tiktok-ia',
    description: 'Sistema completo de inteligência artificial que automatiza a criação de conteúdo viral para TikTok. Analisa tendências, gera scripts envolventes e otimiza o timing de publicação para maximizar alcance e engajamento.',
    platform: 'n8n',
    author_name: 'AutoFlow Pro',
    preview_image_url: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 2847,
    rating_avg: 4.8,
    categories: ['redes-sociais', 'marketing'],
    tools: ['openai', 'n8n'],
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-02-20T15:30:00Z'
  },
  {
    id: 'fallback-2',
    title: 'Gerador de Renda com IA - $6k/mês',
    slug: 'gerador-renda-ia-6k-mes',
    description: 'Template completo para criar múltiplas fontes de renda usando inteligência artificial. Inclui automações para criação de conteúdo, vendas online, atendimento ao cliente e análise de mercado. Sistema testado e aprovado por centenas de empreendedores.',
    platform: 'Make',
    author_name: 'AI Revenue Lab',
    preview_image_url: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 1923,
    rating_avg: 4.7,
    categories: ['produtividade', 'marketing'],
    tools: ['openai', 'make', 'stripe'],
    created_at: '2024-01-22T14:00:00Z',
    updated_at: '2024-03-01T09:15:00Z'
  },
  {
    id: 'fallback-3',
    title: 'SEO Automático 100% - Dominação Orgânica',
    slug: 'seo-automatico-100-dominacao-organica',
    description: 'Sistema de automação SEO mais avançado do mercado. Realiza pesquisa de palavras-chave, cria conteúdo otimizado, monitora concorrentes, constrói backlinks naturais e acompanha rankings em tempo real. Ideal para agências e profissionais de marketing.',
    platform: 'Zapier',
    author_name: 'SEO Master Agency',
    preview_image_url: 'https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 3156,
    rating_avg: 4.9,
    categories: ['marketing', 'produtividade'],
    tools: ['openai', 'google-sheets', 'zapier'],
    created_at: '2024-02-01T08:30:00Z',
    updated_at: '2024-03-10T16:45:00Z'
  },
  {
    id: 'fallback-4',
    title: 'Chatbot Inteligente para E-commerce',
    slug: 'chatbot-inteligente-ecommerce',
    description: 'Chatbot avançado com IA para lojas online que automatiza atendimento 24/7, resolve dúvidas sobre produtos, processa pedidos, calcula fretes e oferece suporte pós-venda. Integração nativa com principais plataformas de e-commerce brasileiras.',
    platform: 'Voiceflow',
    author_name: 'E-commerce Solutions',
    preview_image_url: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 1456,
    rating_avg: 4.6,
    categories: ['ecommerce', 'atendimento'],
    tools: ['openai', 'slack', 'stripe'],
    created_at: '2024-02-10T11:15:00Z',
    updated_at: '2024-03-15T14:20:00Z'
  },
  {
    id: 'fallback-5',
    title: 'Análise Financeira Automatizada com IA',
    slug: 'analise-financeira-automatizada-ia',
    description: 'Sistema completo de análise financeira que coleta dados de múltiplas fontes, categoriza transações automaticamente, gera relatórios detalhados e identifica oportunidades de economia. Inclui alertas inteligentes e previsões baseadas em IA.',
    platform: 'n8n',
    author_name: 'FinTech Automations',
    preview_image_url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 987,
    rating_avg: 4.5,
    categories: ['financas', 'produtividade'],
    tools: ['openai', 'google-sheets', 'airtable'],
    created_at: '2024-02-18T13:45:00Z',
    updated_at: '2024-03-20T10:30:00Z'
  },
  {
    id: 'fallback-6',
    title: 'Automação Completa de Instagram',
    slug: 'automacao-completa-instagram',
    description: 'Suite completa para automatizar sua presença no Instagram. Programa posts, responde DMs automaticamente, monitora menções, analisa métricas de engajamento e identifica os melhores horários para publicação. Perfeito para influencers e marcas.',
    platform: 'Make',
    author_name: 'Social Media Pro',
    preview_image_url: 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0',
    tutorial_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    status: 'published',
    downloads_count: 2134,
    rating_avg: 4.7,
    categories: ['redes-sociais', 'marketing'],
    tools: ['openai', 'airtable', 'notion'],
    created_at: '2024-02-25T16:20:00Z',
    updated_at: '2024-03-25T12:10:00Z'
  }
];

export const fallbackCategories = [
  { key: 'produtividade', name: 'Produtividade' },
  { key: 'marketing', name: 'Marketing' },
  { key: 'ecommerce', name: 'E-commerce' },
  { key: 'redes-sociais', name: 'Redes Sociais' },
  { key: 'financas', name: 'Finanças' },
  { key: 'atendimento', name: 'Atendimento' }
];

export const fallbackTools = [
  { key: 'openai', name: 'OpenAI' },
  { key: 'google-sheets', name: 'Google Sheets' },
  { key: 'slack', name: 'Slack' },
  { key: 'notion', name: 'Notion' },
  { key: 'airtable', name: 'Airtable' },
  { key: 'stripe', name: 'Stripe' },
  { key: 'zapier', name: 'Zapier' },
  { key: 'make', name: 'Make' },
  { key: 'n8n', name: 'n8n' }
];

export const fallbackFacets = {
  platforms: ['n8n', 'Make', 'Zapier', 'Voiceflow'],
  categories: fallbackCategories.map(c => c.key),
  tools: fallbackTools.map(t => t.key)
};