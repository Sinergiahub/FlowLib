import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Search, Filter, Download, Star, ExternalLink, Users, Zap, Bot, Layers, TrendingUp, Sun, Moon, ChevronDown } from "lucide-react";
import { Toaster } from 'react-hot-toast';
import AdminImport from './pages/AdminImport';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mock data for GPT Agents
const gptAgents = [
  {
    id: 'agent-1',
    title: 'AI Workflow Optimizer',
    description: 'Analisa seus templates de automação e sugere melhorias de performance e eficiência',
    banner_url: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    gpt_url: 'https://chat.openai.com/g/g-workflow-optimizer'
  },
  {
    id: 'agent-2', 
    title: 'N8N Flow Builder',
    description: 'Converte suas ideias em fluxos estruturados de n8n com nós e conexões otimizadas',
    banner_url: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31',
    gpt_url: 'https://chat.openai.com/g/g-n8n-builder'
  },
  {
    id: 'agent-3',
    title: 'Automation Code Generator', 
    description: 'Gera códigos JavaScript, Python e webhooks personalizados para suas automações',
    banner_url: 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4',
    gpt_url: 'https://chat.openai.com/g/g-code-generator'
  },
  {
    id: 'agent-4',
    title: 'Business Process Mapper',
    description: 'Mapeia processos de negócio e sugere pontos ideais para implementar automações',
    banner_url: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43',
    gpt_url: 'https://chat.openai.com/g/g-process-mapper'
  },
  {
    id: 'agent-5',
    title: 'API Integration Helper',
    description: 'Ajuda a conectar diferentes APIs e serviços em seus fluxos de automação',
    banner_url: 'https://images.unsplash.com/photo-1558494944-a2e5cf62a8b1',
    gpt_url: 'https://chat.openai.com/g/g-api-helper'
  }
];

// Agent Card Component  
const AgentCard = ({ agent }) => {
  const handleAgentClick = (agentId, gptUrl) => {
    // Optional: Track click event
    try {
      // Simple analytics tracking (you can replace with your preferred analytics)
      console.log(`Agent clicked: ${agentId}`);
      
      // Optional: Send to analytics endpoint
      // axios.post(`${API}/analytics/agent-click`, { agentId, timestamp: new Date() });
    } catch (error) {
      console.error('Error tracking agent click:', error);
    }

    // Open GPT in new tab
    if (gptUrl) {
      window.open(gptUrl, '_blank', 'noopener,noreferrer');
    }
  };

  // Don't render if no GPT URL
  if (!agent.gpt_url) {
    return null;
  }

  return (
    <div className="agent-card">
      <div className="agent-banner">
        <img src={agent.banner_url} alt={agent.title} />
        <div className="agent-overlay"></div>
      </div>
      
      <div className="agent-content">
        <h3 className="agent-title">{agent.title}</h3>
        <p className="agent-description">{agent.description}</p>
        
        <button 
          className="agent-button"
          onClick={() => handleAgentClick(agent.id, agent.gpt_url)}
        >
          <Bot size={16} />
          Abrir no ChatGPT
        </button>
      </div>
    </div>
  );
};

// GPT Agents Section
const AgentsSection = () => {
  return (
    <section className="agents-section">
      <div className="container">
        <div className="agents-header">
          <h2 className="agents-title">
            🤖 Dobre seus Resultados com <span className="highlight">Agentes GPT</span>
          </h2>
          <p className="agents-subtitle">
            Baixe nossos templates e leve para os agentes especializados. 
            Eles vão otimizar, personalizar e turbinar suas automações.
          </p>
        </div>
        
        <div className="agents-grid">
          {gptAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
        
        <div className="agents-footer">
          <p className="agents-note">
            💡 <strong>Como usar:</strong> Baixe qualquer template, copie o conteúdo e cole no agente GPT. 
            Ele vai analisar e sugerir melhorias específicas para seu caso.
          </p>
        </div>
      </div>
    </section>
  );
};

// Header Component
const Header = ({ onSearch, searchTerm }) => {
  return (
    <header className="header">
      <div className="container">
        <div className="nav">
          <div className="logo">
            <Zap className="logo-icon" />
            <span className="logo-text">FlowLib</span>
          </div>
          
          <div className="search-container">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Buscar automações..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => onSearch(e.target.value)}
            />
          </div>
          
          <div className="nav-actions">
            <button className="btn-secondary">Entrar</button>
            <button className="btn-primary">Cadastrar</button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Hero Section
const HeroSection = ({ featuredTemplates }) => {
  return (
    <section className="hero">
      <div className="hero-background">
        <img src="https://images.unsplash.com/photo-1531403009284-440f080d1e12" alt="Automation Background" />
        <div className="hero-overlay"></div>
      </div>
      
      <div className="container">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Descubra <span className="highlight">Automações</span><br />
              que Transformam seu Negócio
            </h1>
            <p className="hero-description">
              Biblioteca completa de templates para n8n, Make, Zapier e mais.
              Automatize processos, aumente produtividade e escale seus resultados.
            </p>
            
            <div className="hero-stats">
              <div className="stat">
                <div className="stat-number">500+</div>
                <div className="stat-label">Templates</div>
              </div>
              <div className="stat">
                <div className="stat-number">50k+</div>
                <div className="stat-label">Downloads</div>
              </div>
              <div className="stat">
                <div className="stat-number">15k+</div>
                <div className="stat-label">Usuários</div>
              </div>
            </div>
          </div>
        </div>
        
        {featuredTemplates.length > 0 && (
          <div className="featured-carousel">
            <h3 className="featured-title">🔥 Automações em Destaque</h3>
            <div className="featured-grid">
              {featuredTemplates.slice(0, 3).map((template) => (
                <div key={template.id} className="featured-card">
                  <div className="featured-image">
                    <img src={template.preview_url} alt={template.title} />
                  </div>
                  <div className="featured-info">
                    <h4>{template.title}</h4>
                    <p>{template.description.substring(0, 80)}...</p>
                    <div className="featured-meta">
                      <span className="downloads">
                        <Download size={14} />
                        {template.downloads_count.toLocaleString()}
                      </span>
                      <span className="rating">
                        <Star size={14} />
                        {template.rating_avg}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

// Filters Sidebar
const FiltersSidebar = ({ categories, tools, filters, onFilterChange }) => {
  return (
    <aside className="filters-sidebar">
      <div className="filters-header">
        <Filter size={20} />
        <span>Filtros</span>
      </div>
      
      <div className="filter-section">
        <h4>Plataforma</h4>
        <div className="filter-options">
          {['n8n', 'Make', 'Zapier', 'Voiceflow'].map((platform) => (
            <label key={platform} className="filter-option">
              <input
                type="checkbox"
                checked={filters.platforms.includes(platform)}
                onChange={(e) => {
                  const platforms = e.target.checked
                    ? [...filters.platforms, platform]
                    : filters.platforms.filter(p => p !== platform);
                  onFilterChange({ ...filters, platforms });
                }}
              />
              <span>{platform}</span>
            </label>
          ))}
        </div>
      </div>
      
      <div className="filter-section">
        <h4>Categoria</h4>
        <div className="filter-options">
          {categories.map((category) => (
            <label key={category.id} className="filter-option">
              <input
                type="checkbox"
                checked={filters.categories.includes(category.id)}
                onChange={(e) => {
                  const categories = e.target.checked
                    ? [...filters.categories, category.id]
                    : filters.categories.filter(c => c !== category.id);
                  onFilterChange({ ...filters, categories });
                }}
              />
              <span>{category.name}</span>
            </label>
          ))}
        </div>
      </div>
      
      <div className="filter-section">
        <h4>Ferramentas</h4>
        <div className="filter-options">
          {tools.slice(0, 6).map((tool) => (
            <label key={tool.id} className="filter-option">
              <input
                type="checkbox"
                checked={filters.tools.includes(tool.id)}
                onChange={(e) => {
                  const tools = e.target.checked
                    ? [...filters.tools, tool.id]
                    : filters.tools.filter(t => t !== tool.id);
                  onFilterChange({ ...filters, tools });
                }}
              />
              <span>{tool.name}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  );
};

// Template Card
const TemplateCard = ({ template, onClick }) => {
  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'n8n': return <Bot size={16} />;
      case 'Make': return <Layers size={16} />;
      case 'Zapier': return <Zap size={16} />;
      case 'Voiceflow': return <Users size={16} />;
      default: return <Bot size={16} />;
    }
  };

  return (
    <div className="template-card" onClick={() => onClick(template)}>
      <div className="template-image">
        <img src={template.preview_url} alt={template.title} />
        <div className="template-overlay">
          <div className="platform-badge">
            {getPlatformIcon(template.platform)}
            <span>{template.platform}</span>
          </div>
        </div>
      </div>
      
      <div className="template-content">
        <h3 className="template-title">{template.title}</h3>
        <p className="template-description">
          {template.description.substring(0, 120)}...
        </p>
        
        <div className="template-meta">
          <span className="author">Por {template.author_name}</span>
          <div className="template-stats">
            <span className="downloads">
              <Download size={14} />
              {template.downloads_count.toLocaleString()}
            </span>
            <span className="rating">
              <Star size={14} />
              {template.rating_avg}
            </span>
          </div>
        </div>
        
        <div className="template-tags">
          {template.categories.slice(0, 2).map((category) => (
            <span key={category} className="tag">{category}</span>
          ))}
        </div>
        
        <div className="template-tools">
          {template.tools.slice(0, 3).map((tool) => (
            <span key={tool} className="tool-tag">{tool}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Template Detail Modal
const TemplateDetailModal = ({ template, isOpen, onClose }) => {
  if (!isOpen || !template) return null;

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'n8n': return <Bot size={16} />;
      case 'Make': return <Layers size={16} />;
      case 'Zapier': return <Zap size={16} />;
      case 'Voiceflow': return <Users size={16} />;
      default: return <Bot size={16} />;
    }
  };

  const handleDownload = async () => {
    try {
      await axios.post(`${API}/templates/${template.id}/download`);
      // In a real app, this would trigger file download
      if (template.download_url || template.file_url) {
        window.open(template.download_url || template.file_url, '_blank');
      } else {
        alert('Download iniciado! (Demo)');
      }
    } catch (error) {
      console.error('Erro no download:', error);
    }
  };

  const previewImage = template.preview_image_url || template.preview_url || 'https://images.unsplash.com/photo-1518770660439-4636190af475';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content-enhanced" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-layout">
          {/* Left side - Preview Image */}
          <div className="modal-preview">
            <img src={previewImage} alt={template.title} className="modal-preview-image" />
            <div className="modal-platform-badge">
              {getPlatformIcon(template.platform)}
              <span>{template.platform}</span>
            </div>
          </div>
          
          {/* Right side - Details */}
          <div className="modal-details">
            <div className="modal-header-content">
              <h2 className="modal-title">{template.title}</h2>
              <p className="modal-description-enhanced">
                {template.description || template.shortDescription || 'Descrição não disponível'}
              </p>
            </div>
            
            <div className="modal-metadata">
              <div className="metadata-grid">
                <div className="metadata-item">
                  <span className="metadata-label">Autor</span>
                  <span className="metadata-value">{template.author_name || 'Community'}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Downloads</span>
                  <span className="metadata-value">
                    <Download size={14} />
                    {(template.downloads_count || 0).toLocaleString()}
                  </span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Avaliação</span>
                  <span className="metadata-value">
                    <Star size={14} />
                    {template.rating_avg || 'N/A'}
                  </span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Plataforma</span>
                  <span className="metadata-value">{template.platform}</span>
                </div>
              </div>
            </div>
            
            <div className="modal-chips-section">
              <div className="chips-group">
                <h4 className="chips-title">Categorias</h4>
                <div className="chips-container">
                  {(template.categories || []).map((category) => (
                    <span key={category} className="category-chip">{category}</span>
                  ))}
                </div>
              </div>
              
              <div className="chips-group">
                <h4 className="chips-title">Ferramentas</h4>
                <div className="chips-container">
                  {(template.tools || []).map((tool) => (
                    <span key={tool} className="tool-chip">{tool}</span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="modal-actions-enhanced">
              <button className="btn-download" onClick={handleDownload}>
                <Download size={18} />
                Baixar Template
              </button>
              {template.tutorial_url && (
                <button className="btn-tutorial" onClick={() => window.open(template.tutorial_url, '_blank')}>
                  <ExternalLink size={18} />
                  Ver Tutorial
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">
              <Zap className="footer-logo-icon" />
              <span className="footer-logo-text">FlowLib</span>
            </div>
            <p className="footer-tagline">
              Biblioteca completa de templates de automação para transformar seu negócio.
            </p>
          </div>
          
          <div className="footer-links">
            <a href="/quem-somos" className="footer-link">Quem somos</a>
            <a href="/contato" className="footer-link">Contato</a>
            <a href="/privacidade" className="footer-link">Política de Privacidade</a>
            <a href="/termos" className="footer-link">Termos de Uso</a>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="footer-copyright">
            © 2025 FlowLib. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
const Home = () => {
  const [templates, setTemplates] = useState([]);
  const [featuredTemplates, setFeaturedTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [usingFallback, setUsingFallback] = useState(false);
  const [filters, setFilters] = useState({
    platforms: [],
    categories: [],
    tools: []
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadTemplates();
  }, [searchTerm, filters, currentPage]);

  const loadInitialData = async () => {
    try {
      const [featuredRes, categoriesRes, toolsRes] = await Promise.all([
        axios.get(`${API}/featured`),
        axios.get(`${API}/categories`),
        axios.get(`${API}/tools`)
      ]);

      setFeaturedTemplates(featuredRes.data);
      setCategories(categoriesRes.data);
      setTools(toolsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
      // Use fallback data if initial data fails
      const { fallbackCategories, fallbackTools, fallbackTemplates } = await import('./lib/fallbackData.js');
      setFeaturedTemplates(fallbackTemplates.slice(0, 6));
      setCategories(fallbackCategories);
      setTools(fallbackTools);
      setUsingFallback(true);
    }
  };

  const loadTemplates = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '12');
      
      if (searchTerm) params.append('search', searchTerm);
      if (filters.platforms.length > 0) {
        params.append('platform', filters.platforms[0]); // Single platform for now
      }
      if (filters.categories.length > 0) {
        params.append('category', filters.categories[0]); // Single category for now
      }
      if (filters.tools.length > 0) {
        params.append('tool', filters.tools[0]); // Single tool for now
      }

      const response = await axios.get(`${API}/templates?${params.toString()}`);
      const data = response.data;

      // Use real database data
      setTemplates(data.items || []);
      setTotalItems(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setUsingFallback(false);

      // Only use fallback if we have no templates at all and it's the initial load
      if (data.total === 0 && currentPage === 1 && !searchTerm && filters.platforms.length === 0 && filters.categories.length === 0 && filters.tools.length === 0) {
        // Check if database is completely empty by trying to get any template
        try {
          const checkResponse = await axios.get(`${API}/templates/legacy?limit=1`);
          if (checkResponse.data.length === 0) {
            // Database is empty, use fallback
            const { fallbackTemplates } = await import('./lib/fallbackData.js');
            setTemplates(fallbackTemplates);
            setTotalItems(fallbackTemplates.length);
            setTotalPages(1);
            setUsingFallback(true);
            return;
          }
        } catch (error) {
          console.error('Error checking database:', error);
        }
      }

    } catch (error) {
      console.error('Erro ao carregar templates:', error);
      
      // On error, try fallback data
      if (currentPage === 1) {
        const { fallbackTemplates } = await import('./lib/fallbackData.js');
        setTemplates(fallbackTemplates);
        setTotalItems(fallbackTemplates.length);
        setTotalPages(1);
        setUsingFallback(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
    setModalOpen(true);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  if (loading && templates.length === 0) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Carregando automações...</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Carregando automações...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Header onSearch={setSearchTerm} searchTerm={searchTerm} />
      <HeroSection featuredTemplates={featuredTemplates} />
      
      <main className="main-content">
        <div className="container">
          <div className="content-grid">
            <FiltersSidebar
              categories={categories}
              tools={tools}
              filters={filters}
              onFilterChange={handleFilterChange}
            />
            
            <div className="templates-section">
              <div className="section-header">
                <h2>Biblioteca de Automações</h2>
                <div className="section-info">
                  <p>{totalItems} templates encontrados</p>
                  {usingFallback && (
                    <span className="fallback-indicator">
                      📚 Dados de demonstração (banco vazio)
                    </span>
                  )}
                </div>
              </div>
              
              <div className="templates-grid">
                {templates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onClick={handleTemplateClick}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <AgentsSection />
      <Footer />
      
      <TemplateDetailModal
        template={selectedTemplate}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1a1a1b',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            },
          }}
        />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin/import" element={<AdminImport />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;