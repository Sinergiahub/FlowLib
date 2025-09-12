import { AuthUser, LoginCredentials, RegisterCredentials } from '../types';

// Mock authentication service
class AuthService {
  private storageKey = 'automacaohub_auth';

  // Get current user from localStorage
  getCurrentUser(): AuthUser | null {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  // Login with email/password (mock)
  async login(credentials: LoginCredentials): Promise<AuthUser> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock validation
    if (credentials.email === 'admin@automacaohub.com' && credentials.password === 'admin123') {
      const user: AuthUser = {
        id: '1',
        email: credentials.email,
        displayName: 'Administrador',
        avatarUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
        role: 'admin'
      };
      localStorage.setItem(this.storageKey, JSON.stringify(user));
      return user;
    }

    if (credentials.email === 'user@test.com' && credentials.password === 'user123') {
      const user: AuthUser = {
        id: '2',
        email: credentials.email,
        displayName: 'Usuário Teste',
        avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
        role: 'user'
      };
      localStorage.setItem(this.storageKey, JSON.stringify(user));
      return user;
    }

    throw new Error('Credenciais inválidas');
  }

  // Register new user (mock)
  async register(credentials: RegisterCredentials): Promise<AuthUser> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1200));

    // Mock validation
    if (credentials.email === 'existing@test.com') {
      throw new Error('E-mail já cadastrado');
    }

    const user: AuthUser = {
      id: Math.random().toString(36).substr(2, 9),
      email: credentials.email,
      displayName: credentials.displayName,
      role: 'user'
    };

    localStorage.setItem(this.storageKey, JSON.stringify(user));
    return user;
  }

  // Logout
  async logout(): Promise<void> {
    localStorage.removeItem(this.storageKey);
  }

  // Google OAuth (placeholder - will be implemented with Supabase)
  async loginWithGoogle(): Promise<AuthUser> {
    throw new Error('Login com Google não configurado. Configure as variáveis de ambiente.');
  }

  // Password reset (mock)
  async resetPassword(email: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Mock - in real app would send email
  }
}

export const authService = new AuthService();