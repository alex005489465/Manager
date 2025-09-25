import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type ThemeMode = 'light' | 'dark' | 'auto';
export type ActiveTheme = 'light' | 'dark';

interface ThemeContextType {
  themeMode: ThemeMode;
  activeTheme: ActiveTheme;
  setThemeMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [themeMode, setThemeModeState] = useState<ThemeMode>('auto');
  const [activeTheme, setActiveTheme] = useState<ActiveTheme>('light');

  // 檢測瀏覽器預設主題
  const getSystemTheme = (): ActiveTheme => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  };

  // 從 localStorage 讀取用戶偏好
  const getStoredTheme = (): ThemeMode => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme-preference');
      if (stored && ['light', 'dark', 'auto'].includes(stored)) {
        return stored as ThemeMode;
      }
    }
    return 'auto';
  };

  // 計算當前應該使用的主題
  const calculateActiveTheme = (mode: ThemeMode): ActiveTheme => {
    if (mode === 'auto') {
      return getSystemTheme();
    }
    return mode;
  };

  // 設置主題模式
  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode);
    setActiveTheme(calculateActiveTheme(mode));

    if (typeof window !== 'undefined') {
      localStorage.setItem('theme-preference', mode);
    }
  };

  // 切換主題（在 light/dark 之間切換，不包括 auto）
  const toggleTheme = () => {
    const newMode: ThemeMode = activeTheme === 'light' ? 'dark' : 'light';
    setThemeMode(newMode);
  };

  // 監聽系統主題變更
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      if (themeMode === 'auto') {
        setActiveTheme(e.matches ? 'dark' : 'light');
      }
    };

    // 使用現代的方法監聽變更
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleSystemThemeChange);
      return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
    } else {
      // 兼容舊版瀏覽器
      mediaQuery.addListener(handleSystemThemeChange);
      return () => mediaQuery.removeListener(handleSystemThemeChange);
    }
  }, [themeMode]);

  // 初始化主題
  useEffect(() => {
    const storedTheme = getStoredTheme();
    setThemeModeState(storedTheme);
    setActiveTheme(calculateActiveTheme(storedTheme));
  }, []);

  const value: ThemeContextType = {
    themeMode,
    activeTheme,
    setThemeMode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};