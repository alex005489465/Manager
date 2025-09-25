import React from 'react';
import { ConfigProvider } from 'antd';
import zhTW from 'antd/locale/zh_TW';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { getThemeConfig } from './contexts/themeConfig';
import { FoodItemsPage } from './components/FoodItems';

// 內部應用組件，需要在 ThemeProvider 內部使用
const AppContent: React.FC = () => {
  const { activeTheme } = useTheme();

  return (
    <ConfigProvider
      locale={zhTW}
      theme={getThemeConfig(activeTheme)}
    >
      <FoodItemsPage />
    </ConfigProvider>
  );
};

// 主應用組件
function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;