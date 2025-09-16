import React, { useState } from 'react';
import { Upload, FileText, Link, Eye, Download, AlertCircle, CheckCircle, XCircle, Trash2, Package, Tag, Wrench, Bot } from 'lucide-react';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminImport = () => {
  const [activeSection, setActiveSection] = useState('templates');
  const [selectedFile, setSelectedFile] = useState(null);
  const [sheetUrl, setSheetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [importCompleted, setImportCompleted] = useState(false);
  const [finalReport, setFinalReport] = useState(null);

  const sections = {
    templates: {
      title: 'Templates',
      description: 'Importar templates de automação',
      icon: Package,
      endpoint: 'templates',
      color: 'blue'
    },
    platforms: {
      title: 'Tipos de Plataformas',
      description: 'Importar plataformas de automação',
      icon: Package,
      endpoint: 'platforms',
      color: 'green'
    },
    categories: {
      title: 'Tipos de Categorias',
      description: 'Importar categorias de templates',
      icon: Tag,
      endpoint: 'categories',
      color: 'purple'
    },
    tools: {
      title: 'Ferramentas',
      description: 'Importar ferramentas e integrações',
      icon: Wrench,
      endpoint: 'tools',
      color: 'orange'
    },
    agents: {
      title: 'Adicionar Agentes GPT',
      description: 'Importar agentes GPT e assistentes',
      icon: Bot,
      endpoint: 'agents',
      color: 'pink'
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        toast.error('Por favor, selecione um arquivo CSV');
        return;
      }
      setSelectedFile(file);
      setSheetUrl('');
      setPreviewData(null);
      setImportCompleted(false);
      setFinalReport(null);
    }
  };

  const handleUrlChange = (value) => {
    setSheetUrl(value);
    if (value) {
      setSelectedFile(null);
      setPreviewData(null);
      setImportCompleted(false);
      setFinalReport(null);
    }
  };

  const validateInput = () => {
    if (!selectedFile && !sheetUrl) {
      toast.error('Selecione um arquivo CSV ou insira uma URL do Google Sheets');
      return false;
    }
    return true;
  };

  const getApiEndpoint = (action) => {
    const section = sections[activeSection];
    if (activeSection === 'templates') {
      return `${API}/import/${action}`;
    }
    return `${API}/import/${section.endpoint}/${action}`;
  };

  const handleValidate = async () => {
    if (!validateInput()) return;

    setLoading(true);
    try {
      const formData = new FormData();
      
      if (selectedFile) {
        formData.append('file', selectedFile);
      } else if (sheetUrl) {
        formData.append('sheet_url', sheetUrl);
      }

      const response = await fetch(getApiEndpoint('preview'), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro na validação');
      }

      const data = await response.json();
      setPreviewData(data);
      setImportCompleted(false);
      setFinalReport(null);
      
      toast.success(`Validação concluída: ${data.total_rows} linhas analisadas`);
    } catch (error) {
      toast.error(`Erro na validação: ${error.message}`);
      console.error('Validation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!validateInput()) return;

    setLoading(true);
    try {
      const formData = new FormData();
      
      if (selectedFile) {
        formData.append('file', selectedFile);
      } else if (sheetUrl) {
        // For import, we need to re-upload the file since the preview endpoint doesn't store it
        if (sheetUrl) {
          // Convert Google Sheets URL to CSV export URL and fetch
          toast.error('Importação direta via URL do Google Sheets não suportada ainda. Use o arquivo CSV.');
          return;
        }
      }

      const response = await fetch(getApiEndpoint(''), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro na importação');
      }

      const data = await response.json();
      setFinalReport(data);
      setImportCompleted(true);
      
      const successCount = data.inserted + data.updated + data.deleted;
      toast.success(`Importação concluída! ${successCount} operações realizadas`);
      
      if (data.errors.length > 0) {
        toast.error(`${data.errors.length} erros encontrados`);
      }
    } catch (error) {
      toast.error(`Erro na importação: ${error.message}`);
      console.error('Import error:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadExampleCSV = () => {
    const section = sections[activeSection];
    let csvContent = '';
    
    switch (activeSection) {
      case 'templates':
        csvContent = `action,slug,title,description,platform,author_name,categories,tools,downloads_count
upsert,exemplo-simples,Exemplo Simples,Descrição básica,n8n,Admin,produtividade,openai,100
upsert,exemplo-completo,Exemplo Completo,Descrição detalhada do template,Make,Autor Teste,marketing|vendas,make|gmail|slack,250
delete,template-antigo,,,,,,,`;
        break;
      case 'platforms':
        csvContent = `action,key,name,description
upsert,n8n,n8n,Automação visual open-source
upsert,zapier,Zapier,Plataforma no-code popular
delete,plataforma-antiga,,,`;
        break;
      case 'categories':
        csvContent = `action,key,name,description
upsert,produtividade,Produtividade,Templates para produtividade
upsert,marketing,Marketing,Automação de marketing
delete,categoria-antiga,,,`;
        break;
      case 'tools':
        csvContent = `action,key,name,description
upsert,openai,OpenAI,Inteligência artificial
upsert,slack,Slack,Comunicação em equipe
delete,ferramenta-antiga,,,`;
        break;
      case 'agents':
        csvContent = `action,slug,name,description,gpt_link,category
upsert,assistente-ia,Assistente IA,GPT para automação,https://chat.openai.com/g/exemplo,assistente
delete,agente-antigo,,,,,`;
        break;
    }

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `exemplo-${activeSection}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success(`Exemplo CSV para ${section.title} baixado!`);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'insert':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'update':
        return <Download className="text-blue-500" size={16} />;
      case 'delete':
        return <Trash2 className="text-red-500" size={16} />;
      case 'error':
        return <XCircle className="text-red-500" size={16} />;
      default:
        return <AlertCircle className="text-gray-500" size={16} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'insert':
        return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'update':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'delete':
        return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'error':
        return 'text-red-400 bg-red-400/10 border-red-400/20';
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const clearAll = () => {
    setSelectedFile(null);
    setSheetUrl('');
    setPreviewData(null);
    setImportCompleted(false);
    setFinalReport(null);
  };

  const getSectionColor = (section, type = 'bg') => {
    const colors = {
      blue: type === 'bg' ? 'bg-blue-500/20 border-blue-400/30' : 'text-blue-400',
      green: type === 'bg' ? 'bg-green-500/20 border-green-400/30' : 'text-green-400',
      purple: type === 'bg' ? 'bg-purple-500/20 border-purple-400/30' : 'text-purple-400',
      orange: type === 'bg' ? 'bg-orange-500/20 border-orange-400/30' : 'text-orange-400',
      pink: type === 'bg' ? 'bg-pink-500/20 border-pink-400/30' : 'text-pink-400'
    };
    return colors[section.color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      {/* Header */}
      <div className="border-b border-white/10 bg-[#0a0a0b]/95 backdrop-blur-xl">
        <div className="container max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Importação de Templates</h1>
              <p className="text-white/60 mt-1">Área administrativa - Importar templates via CSV</p>
            </div>
            {(previewData || finalReport) && (
              <button
                onClick={clearAll}
                className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-colors"
              >
                Limpar
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="container max-w-7xl mx-auto px-6 py-8">
        {/* Input Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6">Selecionar Fonte de Dados</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-3">
                <Upload className="inline mr-2" size={16} />
                Upload de Arquivo CSV
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="flex items-center justify-center w-full p-6 border-2 border-dashed border-white/20 rounded-lg cursor-pointer hover:border-white/40 transition-colors"
                >
                  <div className="text-center">
                    <FileText className="mx-auto mb-2 text-white/60" size={24} />
                    <p className="text-white/80">
                      {selectedFile ? selectedFile.name : 'Clique para selecionar arquivo CSV'}
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Google Sheets URL */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-3">
                <Link className="inline mr-2" size={16} />
                URL do Google Sheets
              </label>
              <input
                type="url"
                value={sheetUrl}
                onChange={(e) => handleUrlChange(e.target.value)}
                placeholder="https://docs.google.com/spreadsheets/d/..."
                className="w-full p-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-400/50 text-white placeholder-white/40"
              />
              <p className="text-xs text-white/50 mt-1">
                Cole a URL do Google Sheets (deve ser público ou com permissão de visualização)
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={handleValidate}
              disabled={loading || (!selectedFile && !sheetUrl)}
              className="flex items-center px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Eye className="mr-2" size={16} />
              {loading ? 'Validando...' : 'Validar'}
            </button>
            
            <button
              onClick={handleImport}
              disabled={loading || (!selectedFile && !sheetUrl)}
              className="flex items-center px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="mr-2" size={16} />
              {loading ? 'Importando...' : 'Importar'}
            </button>
          </div>
        </div>

        {/* Import Sections */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Object.entries(sections).map(([key, section]) => {
            const Icon = section.icon;
            const isActive = activeSection === key;
            
            return (
              <div
                key={key}
                onClick={() => setActiveSection(key)}
                className={`relative cursor-pointer rounded-xl border p-6 transition-all hover:scale-105 ${
                  isActive 
                    ? `${getSectionColor(section, 'bg')} ring-2 ring-offset-2 ring-offset-[#0a0a0b] ${getSectionColor(section, 'text').replace('text-', 'ring-')}`
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center mb-4">
                  <Icon className={`mr-3 ${isActive ? getSectionColor(section, 'text') : 'text-white/60'}`} size={24} />
                  <h3 className={`font-semibold ${isActive ? getSectionColor(section, 'text') : 'text-white'}`}>
                    {section.title}
                  </h3>
                </div>
                
                <p className="text-white/60 text-sm mb-4">
                  {section.description}
                </p>

                <div className="flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveSection(key);
                      handleValidate();
                    }}
                    disabled={loading || (!selectedFile && !sheetUrl)}
                    className="flex-1 px-3 py-2 bg-white/10 hover:bg-white/20 border border-white/10 rounded text-xs transition-colors disabled:opacity-50"
                  >
                    Validar
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveSection(key);
                      downloadExampleCSV();
                    }}
                    className="px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-xs transition-colors"
                    title="Baixar CSV de exemplo"
                  >
                    CSV
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* CSV Specification */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">
            Especificação CSV - {sections[activeSection].title}
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-white/80 mb-3">Colunas Obrigatórias:</h4>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs mr-2">action</span>
                  <span className="text-white/60 text-sm">upsert ou delete</span>
                </div>
                <div className="flex items-center">
                  <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs mr-2">
                    {activeSection === 'templates' ? 'slug' : 'key'}
                  </span>
                  <span className="text-white/60 text-sm">Identificador único</span>
                </div>
                {activeSection === 'templates' && (
                  <div className="flex items-center">
                    <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs mr-2">platform</span>
                    <span className="text-white/60 text-sm">Plataforma (n8n, Make, Zapier)</span>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white/80 mb-3">Formato Especial:</h4>
              <div className="space-y-2">
                {activeSection === 'templates' && (
                  <>
                    <div className="flex items-center">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs mr-2">categories</span>
                      <span className="text-white/60 text-sm">valor1|valor2|valor3</span>
                    </div>
                    <div className="flex items-center">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs mr-2">tools</span>
                      <span className="text-white/60 text-sm">valor1|valor2|valor3</span>
                    </div>
                  </>
                )}
                <div className="flex items-center">
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs mr-2">UTF-8</span>
                  <span className="text-white/60 text-sm">Codificação obrigatória</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <button
              onClick={downloadExampleCSV}
              className="flex items-center px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded-lg transition-colors"
            >
              <Download className="mr-2" size={16} />
              Baixar Exemplo CSV - {sections[activeSection].title}
            </button>
          </div>
        </div>

        {/* Preview Results */}
        {previewData && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">Prévia da Importação</h3>
            
            {/* Summary */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-white">{previewData.total_rows}</div>
                <div className="text-xs text-white/60">Total</div>
              </div>
              <div className="bg-green-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-green-400">{previewData.insert_count}</div>
                <div className="text-xs text-green-400/80">Inserir</div>
              </div>
              <div className="bg-blue-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-400">{previewData.update_count}</div>
                <div className="text-xs text-blue-400/80">Atualizar</div>
              </div>
              <div className="bg-red-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-red-400">{previewData.delete_count}</div>
                <div className="text-xs text-red-400/80">Deletar</div>
              </div>
              <div className="bg-yellow-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-yellow-400">{previewData.error_count}</div>
                <div className="text-xs text-yellow-400/80">Erros</div>
              </div>
            </div>

            {/* Detailed rows */}
            <div className="max-h-96 overflow-y-auto">
              <div className="space-y-2">
                {previewData.rows.map((row, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(row.status)}`}
                  >
                    <div className="flex items-center">
                      {getStatusIcon(row.status)}
                      <div className="ml-3">
                        <div className="font-medium">{row.title || row.slug}</div>
                        <div className="text-sm opacity-80">Linha {row.line_number}: {row.action}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm">{row.message}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Final Report */}
        {finalReport && importCompleted && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Relatório da Importação</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-green-400">{finalReport.inserted}</div>
                <div className="text-xs text-green-400/80">Inseridos</div>
              </div>
              <div className="bg-blue-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-400">{finalReport.updated}</div>
                <div className="text-xs text-blue-400/80">Atualizados</div>
              </div>
              <div className="bg-red-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-red-400">{finalReport.deleted}</div>
                <div className="text-xs text-red-400/80">Deletados</div>
              </div>
              <div className="bg-yellow-500/10 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-yellow-400">{finalReport.errors.length}</div>
                <div className="text-xs text-yellow-400/80">Erros</div>
              </div>
            </div>

            {finalReport.errors.length > 0 && (
              <div>
                <h4 className="font-medium text-red-400 mb-2">Erros encontrados:</h4>
                <div className="max-h-40 overflow-y-auto">
                  <div className="space-y-1">
                    {finalReport.errors.map((error, index) => (
                      <div key={index} className="text-sm text-red-400/80 bg-red-400/5 p-2 rounded">
                        {error}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminImport;