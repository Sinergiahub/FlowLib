import React, { useState } from 'react';
import { Upload, FileText, Link, Eye, Download, AlertCircle, CheckCircle, XCircle, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminImport = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [sheetUrl, setSheetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [importCompleted, setImportCompleted] = useState(false);
  const [finalReport, setFinalReport] = useState(null);

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

      const response = await fetch(`${API}/import/preview`, {
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

      const response = await fetch(`${API}/import/templates`, {
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'insert':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'update':
        return <Download2 className="text-blue-500" size={16} />;
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
                <FileText size={16} className="inline mr-2" />
                Upload de Arquivo CSV
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="csv-upload"
                />
                <label
                  htmlFor="csv-upload"
                  className="flex items-center justify-center w-full p-4 border-2 border-dashed border-white/20 rounded-lg cursor-pointer hover:border-white/30 transition-colors"
                >
                  <div className="text-center">
                    <Upload size={24} className="mx-auto mb-2 text-white/60" />
                    <p className="text-sm text-white/60">
                      {selectedFile ? selectedFile.name : 'Clique para selecionar arquivo CSV'}
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Google Sheets URL */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-3">
                <Link size={16} className="inline mr-2" />
                URL do Google Sheets
              </label>
              <input
                type="url"
                value={sheetUrl}
                onChange={(e) => handleUrlChange(e.target.value)}
                placeholder="https://docs.google.com/spreadsheets/d/..."
                className="w-full p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
              />
              <p className="text-xs text-white/50 mt-2">
                Cole a URL do Google Sheets (deve ser público ou com permissão de visualização)
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={handleValidate}
              disabled={loading || (!selectedFile && !sheetUrl)}
              className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed border border-white/20 rounded-lg transition-colors"
            >
              <Eye size={16} />
              {loading ? 'Validando...' : 'Validar'}
            </button>

            <button
              onClick={handleImport}
              disabled={loading || (!selectedFile && !sheetUrl) || !previewData}
              className="flex items-center gap-2 px-6 py-3 bg-[#ff6b35] hover:bg-[#e55a2b] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              <Download2 size={16} />
              {loading ? 'Importando...' : 'Importar'}
            </button>
          </div>
        </div>

        {/* Preview Results */}
        {previewData && !importCompleted && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-semibold mb-6">Prévia da Importação</h2>
            
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-white">{previewData.total_rows}</div>
                <div className="text-sm text-white/60">Total</div>
              </div>
              <div className="bg-green-400/10 border border-green-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-400">{previewData.insert_count}</div>
                <div className="text-sm text-green-400">Inserir</div>
              </div>
              <div className="bg-blue-400/10 border border-blue-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">{previewData.update_count}</div>
                <div className="text-sm text-blue-400">Atualizar</div>
              </div>
              <div className="bg-red-400/10 border border-red-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-400">{previewData.delete_count}</div>
                <div className="text-sm text-red-400">Deletar</div>
              </div>
              <div className="bg-yellow-400/10 border border-yellow-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">{previewData.error_count}</div>
                <div className="text-sm text-yellow-400">Erros</div>
              </div>
            </div>

            {/* Preview Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-3 text-white/80">#</th>
                    <th className="text-left p-3 text-white/80">Status</th>
                    <th className="text-left p-3 text-white/80">Slug</th>
                    <th className="text-left p-3 text-white/80">Título</th>
                    <th className="text-left p-3 text-white/80">Ação</th>
                    <th className="text-left p-3 text-white/80">Mensagem</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.rows.map((row, index) => (
                    <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                      <td className="p-3 text-white/60">{row.line_number}</td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(row.status)}
                          <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(row.status)}`}>
                            {row.status}
                          </span>
                        </div>
                      </td>
                      <td className="p-3 text-white/80 font-mono">{row.slug}</td>
                      <td className="p-3 text-white">{row.title}</td>
                      <td className="p-3 text-white/60">{row.action}</td>
                      <td className="p-3 text-white/60">{row.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Final Report */}
        {finalReport && importCompleted && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-6">Relatório de Importação</h2>
            
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-400/10 border border-green-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-400">{finalReport.inserted}</div>
                <div className="text-sm text-green-400">Inseridos</div>
              </div>
              <div className="bg-blue-400/10 border border-blue-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">{finalReport.updated}</div>
                <div className="text-sm text-blue-400">Atualizados</div>
              </div>
              <div className="bg-red-400/10 border border-red-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-400">{finalReport.deleted}</div>
                <div className="text-sm text-red-400">Deletados</div>
              </div>
              <div className="bg-yellow-400/10 border border-yellow-400/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">{finalReport.errors.length}</div>
                <div className="text-sm text-yellow-400">Erros</div>
              </div>
            </div>

            {/* Errors */}
            {finalReport.errors.length > 0 && (
              <div className="bg-red-400/10 border border-red-400/20 rounded-lg p-4">
                <h3 className="font-semibold text-red-400 mb-3">Erros Encontrados:</h3>
                <ul className="space-y-1">
                  {finalReport.errors.map((error, index) => (
                    <li key={index} className="text-sm text-red-400/80">• {error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminImport;