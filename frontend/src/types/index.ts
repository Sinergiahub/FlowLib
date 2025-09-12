// Template Types
export interface Template {
  id: string;
  title: string;
  slug: string;
  description: string;
  shortDescription: string;
  platform: Platform;
  author: string;
  authorAvatar?: string;
  previewUrl?: string;
  tutorialUrl?: string;
  fileUrl?: string;
  status: TemplateStatus;
  downloadCount: number;
  rating: number;
  ratingCount: number;
  createdAt: string;
  updatedAt: string;
  categories: Category[];
  tools: Tool[];
  isFavorited?: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  color?: string;
}

export interface Tool {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  color?: string;
}

export type Platform = 'n8n' | 'Make' | 'Zapier' | 'Voiceflow' | 'RelevanceAI' | 'Other';

export type TemplateStatus = 'draft' | 'published' | 'archived';

// User Types
export interface User {
  id: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  role: UserRole;
  createdAt: string;
}

export type UserRole = 'user' | 'pro' | 'admin';

// Auth Types
export interface AuthUser {
  id: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  role: UserRole;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  displayName: string;
}

// Filter Types
export interface TemplateFilters {
  platforms: Platform[];
  categories: string[];
  tools: string[];
  search: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system';

// Component Props Types
export interface PageProps {
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}