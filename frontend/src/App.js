import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Search, Filter, Download, Star, ExternalLink, Users, Zap, Bot, Layers, TrendingUp, Sun, Moon, ChevronDown, LogIn, LogOut, User, Heart, MoreHorizontal } from "lucide-react";
import { Toaster } from 'react-hot-toast';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
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

// Login Modal Component
const LoginModal = ({ isOpen, onClose }) => {
  const { login, loginWithGoogle, sendMagicLink } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [magicLinkMode, setMagicLinkMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    if (!email || (!password && !magicLinkMode)) return;

    try {
      setLoading(true);
      if (magicLinkMode) {
        await sendMagicLink(email);
      } else {
        await login(email, password);
        onClose();
      }
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      await loginWithGoogle();
      onClose();
    } catch (error) {
      console.error('Google login error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="login-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="login-header">
          <h2>Entrar no FlowLib</h2>
          <p>Acesse sua conta para baixar templates exclusivos</p>
        </div>

        <div className="login-content">
          {/* Google Login */}
          <button 
            className="google-login-btn"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12V14.46h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continuar com Google
          </button>

          <div className="login-divider">
            <span>ou</span>
          </div>

          {/* Email Login Form */}
          <form onSubmit={handleEmailLogin} className="login-form">
            <div className="form-group">
              <label>E-mail</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                required
              />
            </div>

            {!magicLinkMode && (
              <div className="form-group">
                <label>Senha</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Digite sua senha"
                  required
                />
              </div>
            )}

            <button 
              type="submit" 
              className="login-submit-btn"
              disabled={loading}
            >
              {loading ? 'Processando...' : 
               magicLinkMode ? 'Enviar Link Mágico' : 'Entrar'}
            </button>
          </form>

          <div className="login-footer">
            <button 
              className="toggle-magic-link"
              onClick={() => setMagicLinkMode(!magicLinkMode)}
            >
              {magicLinkMode ? 'Usar senha' : 'Entrar sem senha (link mágico)'}
            </button>
            
            <div className="demo-accounts">
              <p className="demo-title">Contas de teste:</p>
              <div className="demo-buttons">
                <button onClick={() => { setEmail('admin@flowlib.com'); setPassword('admin'); }}>
                  Admin
                </button>
                <button onClick={() => { setEmail('buyer@test.com'); setPassword('buyer'); }}>
                  Comprador
                </button>
                <button onClick={() => { setEmail('user@test.com'); setPassword('user'); }}>
                  Usuário
                </button>
              </div>
            </div>
          </div>
        </div>
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
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isAuthenticated } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  const scrollToAgents = () => {
    const agentsSection = document.querySelector('.agents-section');
    if (agentsSection) {
      agentsSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
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
              {/* Go to Agents Button */}
              <button className="btn-agents" onClick={scrollToAgents}>
                <Bot size={16} />
                Ir para Agentes GPT
              </button>

              {/* Theme Toggle */}
              <button className="theme-toggle" onClick={toggleTheme}>
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>

              {/* Auth Section */}
              {isAuthenticated() ? (
                <div className="user-menu">
                  <button 
                    className="user-button"
                    onClick={() => setShowUserMenu(!showUserMenu)}
                  >
                    {user.avatarUrl && (
                      <img src={user.avatarUrl} alt={user.name} className="user-avatar" />
                    )}
                    <span className="user-name">{user.name}</span>
                    <ChevronDown size={16} />
                  </button>
                  
                  {showUserMenu && (
                    <div className="user-dropdown">
                      <div className="user-info">
                        <p className="user-email">{user.email}</p>
                        <span className={`user-role user-role-${user.role}`}>
                          {user.role === 'admin' ? 'Administrador' : 
                           user.role === 'buyer' ? 'Comprador' : 'Registrado'}
                        </span>
                      </div>
                      {user.role === 'admin' && (
                        <a href="/admin/import" className="dropdown-link">
                          <Bot size={16} />
                          Painel Admin
                        </a>
                      )}
                      <button className="dropdown-button" onClick={() => {
                        logout();
                        setShowUserMenu(false);
                      }}>
                        <LogOut size={16} />
                        Sair
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="auth-buttons">
                  <button 
                    className="btn-secondary"
                    onClick={() => setShowLoginModal(true)}
                  >
                    <LogIn size={16} />
                    Entrar
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>
      
      {showLoginModal && (
        <LoginModal 
          isOpen={showLoginModal} 
          onClose={() => setShowLoginModal(false)} 
        />
      )}
    </>
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
        <div className="hero-content-centered">
          <h1 className="hero-title-centered">
            Descubra <span className="highlight">Automações</span><br />
            que Transformam seu Negócio
          </h1>
          <p className="hero-description-centered">
            Biblioteca completa de templates para n8n, Make, Zapier e mais.
            Automatize processos, aumente produtividade e escale seus resultados.
          </p>
          
          <div className="hero-stats-centered">
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
        
        {/* Removed featured section due to errors */}
      </div>
    </section>
  );
};

// Filters Sidebar
const FiltersSidebar = ({ categories, tools, filters, onFilterChange, showFeatured, onShowFeaturedChange, showFavorites, onShowFavoritesChange }) => {
  return (
    <aside className="filters-sidebar">
      <div className="filters-header">
        <Filter size={20} />
        <span>Filtros</span>
      </div>

      {/* Special Filters */}
      <div className="filter-section">
        <h4>Especiais</h4>
        <div className="filter-options">
          <label className="filter-option">
            <input
              type="checkbox"
              checked={showFeatured}
              onChange={(e) => onShowFeaturedChange(e.target.checked)}
            />
            <span>⭐ Apenas em Destaque</span>
          </label>
          <label className="filter-option">
            <input
              type="checkbox"
              checked={showFavorites}
              onChange={(e) => onShowFavoritesChange(e.target.checked)}
            />
            <span>❤️ Apenas Favoritos</span>
          </label>
        </div>
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

// Template Card Component
const TemplateCard = ({ template, onClick, onFavoriteToggle, onRating }) => {
  const getPlatformIcon = (platform) => {
    const platformLower = platform.toLowerCase();
    switch (platformLower) {
      case 'n8n':
        return <Layers className="platform-icon" />;
      case 'make':
        return <Zap className="platform-icon" />;
      case 'zapier':
        return <Bot className="platform-icon" />;
      default:
        return <Layers className="platform-icon" />;
    }
  };

  const handleFavoriteClick = (e) => {
    e.stopPropagation();
    onFavoriteToggle(template.id);
  };

  const handleRatingClick = (e, rating) => {
    e.stopPropagation();
    onRating(template.id, rating);
  };

  const renderStars = () => {
    return (
      <div className="template-rating-interactive">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={16}
            className={`star-interactive ${
              template.user_rating && star <= template.user_rating
                ? 'star-filled'
                : template.rating_avg && star <= Math.round(template.rating_avg)
                ? 'star-avg'
                : 'star-empty'
            }`}
            onClick={(e) => handleRatingClick(e, star)}
          />
        ))}
        <span className="rating-text">
          {template.rating_avg ? template.rating_avg.toFixed(1) : 'N/A'}
        </span>
      </div>
    );
  };

  return (
    <div className="template-card" onClick={() => onClick(template)}>
      <div className="template-header">
        <div className="template-platform">
          {getPlatformIcon(template.platform)}
          <span>{template.platform}</span>
        </div>
        <button 
          className={`favorite-button ${template.is_favorited ? 'favorited' : ''}`}
          onClick={handleFavoriteClick}
        >
          <Heart 
            size={18} 
            fill={template.is_favorited ? '#ff4444' : 'transparent'}
            stroke={template.is_favorited ? '#ff4444' : 'currentColor'}
          />
        </button>
      </div>
      
      <div className="template-image">
        <img 
          src={template.preview_image_url || template.preview_url || 'https://images.unsplash.com/photo-1518770660439-4636190af475'} 
          alt={template.title}
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1518770660439-4636190af475';
          }}
        />
      </div>
      
      <div className="template-content">
        <h3 className="template-title">{template.title}</h3>
        <p className="template-description">
          {template.description || template.shortDescription || 'Descrição não disponível'}
        </p>
        
        <div className="template-author">
          <Users size={14} />
          <span>{template.author_name || 'Community'}</span>
        </div>
        
        <div className="template-stats">
          <div className="stat">
            <Download size={14} />
            <span>{(template.downloads_count || 0).toLocaleString()}</span>
          </div>
          {renderStars()}
        </div>
        
        <div className="template-tags">
          {(template.categories || []).slice(0, 2).map((category) => (
            <span key={category} className="tag category-tag">{category}</span>
          ))}
          {(template.tools || []).slice(0, 2).map((tool) => (
            <span key={tool} className="tag tool-tag">{tool}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Template Detail Modal
const TemplateDetailModal = ({ template, isOpen, onClose }) => {
  const { user, canDownload, isAuthenticated } = useAuth();
  
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
    if (!canDownload()) {
      // This should not happen as button is conditionally rendered
      return;
    }

    try {
      await axios.post(`${API}/templates/${template.id}/download`);
      // Track download event
      await axios.post(`${API}/analytics/download`, {
        template_slug: template.slug,
        user_id: user?.id,
        timestamp: new Date().toISOString()
      });
      
      if (template.download_url || template.file_url) {
        window.open(template.download_url || template.file_url, '_blank');
      } else {
        // Simulate download
        const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${template.slug}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Erro no download:', error);
    }
  };

  const getDownloadButton = () => {
    if (!isAuthenticated()) {
      return (
        <button className="btn-auth-required">
          <LogIn size={18} />
          Entrar para baixar
        </button>
      );
    }

    if (!canDownload()) {
      return (
        <button className="btn-upgrade-required">
          <Star size={18} />
          Comprar para baixar
        </button>
      );
    }

    return (
      <button className="btn-download" onClick={handleDownload}>
        <Download size={18} />
        Baixar Template
      </button>
    );
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
              {getDownloadButton()}
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
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [usingFallback, setUsingFallback] = useState(false);
  const [userId, setUserId] = useState(() => {
    // Generate or get persistent user ID for favorites/ratings
    let id = localStorage.getItem('flowlib_user_id');
    if (!id) {
      id = 'user_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('flowlib_user_id', id);
    }
    return id;
  });
  const [filters, setFilters] = useState({
    platforms: [],
    categories: [],
    tools: []
  });
  const [showFeatured, setShowFeatured] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    // Debounced search effect - only search, no reset
    const timeoutId = setTimeout(() => {
      loadTemplates();
    }, 300); // Reduced to 300ms

    return () => clearTimeout(timeoutId);
  }, [searchTerm, filters]);

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

  const loadTemplates = async (isLoadMore = false) => {
    try {
      if (!isLoadMore) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      
      const pageToLoad = isLoadMore ? currentPage + 1 : 1;
      
      const params = new URLSearchParams();
      params.append('page', pageToLoad.toString());
      params.append('page_size', '15'); // Show 15 templates per page as requested
      params.append('user_id', userId); // Add user_id for favorites/ratings
      
      if (searchTerm) params.append('search', searchTerm);
      if (filters.platforms.length > 0) {
        params.append('platform', filters.platforms[0]);
      }
      if (filters.categories.length > 0) {
        params.append('category', filters.categories[0]);
      }
      if (filters.tools.length > 0) {
        params.append('tool', filters.tools[0]);
      }
      if (showFeatured) {
        params.append('featured', 'true');
      }
      if (showFavorites) {
        params.append('favorites', 'true');
      }

      const response = await axios.get(`${API}/templates?${params.toString()}`);
      const data = response.data;

      if (isLoadMore) {
        // Append new templates to existing ones
        setTemplates(prevTemplates => [...prevTemplates, ...data.items]);
        setCurrentPage(pageToLoad);
      } else {
        // Replace templates - but don't clear immediately
        setTemplates(data.items || []);
        setCurrentPage(1);
      }
      
      setTotalItems(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setHasMore(pageToLoad < (data.total_pages || 1));
      setUsingFallback(false);

    } catch (error) {
      console.error('Erro ao carregar templates:', error);
      
      if (!isLoadMore && !searchTerm) {
        const { fallbackTemplates } = await import('./lib/fallbackData.js');
        setTemplates(fallbackTemplates);
        setTotalItems(fallbackTemplates.length);
        setTotalPages(1);
        setHasMore(false);
        setUsingFallback(true);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      loadTemplates(true);
    }
  };

  const handleFavoriteToggle = async (templateId) => {
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      
      const response = await axios.post(`${API}/templates/${templateId}/favorite`, formData);
      
      // Update template in state
      setTemplates(prevTemplates => 
        prevTemplates.map(template => 
          template.id === templateId 
            ? { ...template, is_favorited: response.data.favorited }
            : template
        )
      );
      
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const handleRating = async (templateId, rating) => {
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('rating', rating.toString());
      
      await axios.post(`${API}/templates/${templateId}/rate`, formData);
      
      // Update template in state
      setTemplates(prevTemplates => 
        prevTemplates.map(template => 
          template.id === templateId 
            ? { ...template, user_rating: rating }
            : template
        )
      );
      
    } catch (error) {
      console.error('Error rating template:', error);
    }
  };

  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
    setModalOpen(true);
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
    // Don't reset page or templates here - let useEffect handle it
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
    setTemplates([]); // Clear existing templates
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
      <Header onSearch={handleSearch} searchTerm={searchTerm} />
      <HeroSection featuredTemplates={featuredTemplates} />
      
      <main className="main-content">
        <div className="container">
          <div className="content-grid">
            <FiltersSidebar
              categories={categories}
              tools={tools}
              filters={filters}
              onFilterChange={handleFilterChange}
              showFeatured={showFeatured}
              onShowFeaturedChange={setShowFeatured}
              showFavorites={showFavorites}
              onShowFavoritesChange={setShowFavorites}
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
                    onFavoriteToggle={handleFavoriteToggle}
                    onRating={handleRating}
                  />
                ))}
              </div>
              
              {/* Load More Section */}
              {hasMore && (
                <div className="load-more-section">
                  <button 
                    className={`load-more-button ${loadingMore ? 'loading' : ''}`}
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                  >
                    {loadingMore ? (
                      <>
                        <div className="loading-spinner-small"></div>
                        Carregando...
                      </>
                    ) : (
                      <>
                        <MoreHorizontal size={20} />
                        Load More Templates • {totalItems - templates.length} more available
                      </>
                    )}
                  </button>
                  <div className="templates-counter">
                    Showing {templates.length} of {totalItems} templates
                  </div>
                </div>
              )}
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
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="App">
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-primary)',
                },
              }}
            />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/admin/import" element={<AdminImport />} />
            </Routes>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;