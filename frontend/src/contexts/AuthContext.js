import React, { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const AuthContext = createContext();

// Mock auth service for now - will be replaced with Supabase
const mockAuthService = {
  getCurrentUser: () => {
    const stored = localStorage.getItem('flowlib-user');
    return stored ? JSON.parse(stored) : null;
  },
  
  login: async (email, password) => {
    // Mock login
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock admin user
    if (email === 'admin@flowlib.com') {
      const user = {
        id: 'admin-1',
        email: 'admin@flowlib.com',
        name: 'Administrador',
        role: 'admin',
        avatarUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'
      };
      localStorage.setItem('flowlib-user', JSON.stringify(user));
      return user;
    }
    
    // Mock buyer user
    if (email === 'buyer@test.com') {
      const user = {
        id: 'buyer-1',
        email: 'buyer@test.com',
        name: 'Comprador Teste',
        role: 'buyer',
        avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face'
      };
      localStorage.setItem('flowlib-user', JSON.stringify(user));
      return user;
    }
    
    // Mock registered user
    const user = {
      id: 'user-1',
      email: email,
      name: 'Usuário Registrado',
      role: 'registered',
      avatarUrl: 'https://images.unsplash.com/photo-1494790108755-2616b332e234?w=100&h=100&fit=crop&crop=face'
    };
    localStorage.setItem('flowlib-user', JSON.stringify(user));
    return user;
  },
  
  loginWithGoogle: async () => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    const user = {
      id: 'google-1',
      email: 'user@gmail.com',
      name: 'Usuário Google',
      role: 'registered',
      avatarUrl: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop&crop=face'
    };
    localStorage.setItem('flowlib-user', JSON.stringify(user));
    return user;
  },
  
  sendMagicLink: async (email) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    toast.success('Link mágico enviado para seu e-mail!');
  },
  
  logout: async () => {
    localStorage.removeItem('flowlib-user');
  }
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentUser = mockAuthService.getCurrentUser();
    setUser(currentUser);
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      const user = await mockAuthService.login(email, password);
      setUser(user);
      toast.success(`Bem-vindo, ${user.name}!`);
      return user;
    } catch (error) {
      toast.error('Erro ao fazer login');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      const user = await mockAuthService.loginWithGoogle();
      setUser(user);
      toast.success(`Bem-vindo, ${user.name}!`);
      return user;
    } catch (error) {
      toast.error('Erro no login com Google');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const sendMagicLink = async (email) => {
    try {
      await mockAuthService.sendMagicLink(email);
    } catch (error) {
      toast.error('Erro ao enviar link mágico');
      throw error;
    }
  };

  const logout = async () => {
    try {
      await mockAuthService.logout();
      setUser(null);
      toast.success('Logout realizado com sucesso');
    } catch (error) {
      toast.error('Erro ao fazer logout');
    }
  };

  const canDownload = () => {
    return user && (user.role === 'buyer' || user.role === 'admin');
  };

  const canAccessAdmin = () => {
    return user && user.role === 'admin';
  };

  const isAuthenticated = () => {
    return !!user;
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      loginWithGoogle,
      sendMagicLink,
      logout,
      canDownload,
      canAccessAdmin,
      isAuthenticated
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}