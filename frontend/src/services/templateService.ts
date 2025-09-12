import { Template, TemplateFilters, PaginatedResponse } from '../types';
import { mockTemplates, filterTemplates, getFeaturedTemplates, getTemplateBySlug } from '../lib/mockData';

class TemplateService {
  // Get templates with filters and pagination (mock)
  async getTemplates(
    filters: Partial<TemplateFilters> = {},
    page: number = 1,
    limit: number = 12
  ): Promise<PaginatedResponse<Template>> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const filtered = filterTemplates(filters);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedTemplates = filtered.slice(startIndex, endIndex);

    return {
      data: paginatedTemplates,
      pagination: {
        page,
        limit,
        total: filtered.length,
        totalPages: Math.ceil(filtered.length / limit)
      }
    };
  }

  // Get template by slug
  async getTemplateBySlug(slug: string): Promise<Template> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));

    const template = getTemplateBySlug(slug);
    if (!template) {
      throw new Error('Template não encontrado');
    }
    return template;
  }

  // Get featured templates
  async getFeaturedTemplates(limit: number = 6): Promise<Template[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return getFeaturedTemplates(limit);
  }

  // Toggle favorite (mock)
  async toggleFavorite(templateId: string): Promise<boolean> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const template = mockTemplates.find(t => t.id === templateId);
    if (template) {
      template.isFavorited = !template.isFavorited;
      return template.isFavorited;
    }
    throw new Error('Template não encontrado');
  }

  // Track download (mock)
  async trackDownload(templateId: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const template = mockTemplates.find(t => t.id === templateId);
    if (template) {
      template.downloadCount += 1;
    }
  }

  // Search suggestions (mock)
  async getSearchSuggestions(query: string): Promise<string[]> {
    if (!query || query.length < 2) return [];
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const suggestions = mockTemplates
      .filter(template => 
        template.title.toLowerCase().includes(query.toLowerCase()) ||
        template.shortDescription.toLowerCase().includes(query.toLowerCase())
      )
      .map(template => template.title)
      .slice(0, 5);
    
    return suggestions;
  }
}

export const templateService = new TemplateService();