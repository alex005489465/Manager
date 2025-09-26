import { ThemeConfig } from 'antd';
import { ActiveTheme } from './ThemeContext';

// 明亮主題配置（使用 Ant Design 預設）
const lightTheme: ThemeConfig = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    colorBgBase: '#ffffff',
    colorTextBase: '#000000',
    borderRadius: 6,
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      bodyBg: '#f5f5f5',
    },
    Card: {
      colorBgContainer: '#ffffff',
    },
    Table: {
      headerBg: '#fafafa',
      rowHoverBg: '#f5f5f5',
    }
  }
};

// 暗黑主題配置
const darkTheme: ThemeConfig = {
  algorithm: undefined, // 不使用內建算法，手動配置
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',

    // 背景色配置
    colorBgBase: '#141414',         // 基礎背景
    colorBgContainer: '#1f1f1f',    // 容器背景
    colorBgElevated: '#262626',     // 懸浮元素背景
    colorBgLayout: '#000000',       // Layout 背景
    colorBgSpotlight: '#424242',    // 聚光燈背景
    colorBgBlur: 'rgba(255, 255, 255, 0.04)',

    // 文字色配置
    colorTextBase: '#ffffff',       // 基礎文字
    colorText: 'rgba(255, 255, 255, 0.88)',      // 主文字
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',  // 次要文字
    colorTextTertiary: 'rgba(255, 255, 255, 0.45)',   // 三級文字
    colorTextQuaternary: 'rgba(255, 255, 255, 0.25)', // 四級文字

    // 邊框色配置
    colorBorder: 'rgba(255, 255, 255, 0.15)',
    colorBorderSecondary: 'rgba(255, 255, 255, 0.06)',

    // 填充色配置
    colorFill: 'rgba(255, 255, 255, 0.04)',
    colorFillSecondary: 'rgba(255, 255, 255, 0.06)',
    colorFillTertiary: 'rgba(255, 255, 255, 0.08)',
    colorFillQuaternary: 'rgba(255, 255, 255, 0.12)',

    borderRadius: 6,
  },
  components: {
    Layout: {
      headerBg: '#1f1f1f',
      bodyBg: '#141414',
      footerBg: '#1f1f1f',
      triggerBg: '#1f1f1f',
      triggerColor: 'rgba(255, 255, 255, 0.65)',
    },
    Card: {
      colorBgContainer: '#1f1f1f',
      colorBorderSecondary: 'rgba(255, 255, 255, 0.15)',
    },
    Table: {
      headerBg: '#262626',
      rowHoverBg: 'rgba(255, 255, 255, 0.04)',
      bodySortBg: '#262626',
      headerSortActiveBg: '#303030',
      headerSortHoverBg: '#303030',
      fixedHeaderSortActiveBg: '#303030',
    },
    Input: {
      colorBgContainer: '#262626',
      colorBorder: 'rgba(255, 255, 255, 0.15)',
      colorBgContainerDisabled: 'rgba(255, 255, 255, 0.08)',
    },
    Select: {
      colorBgContainer: '#262626',
      colorBgElevated: '#262626',
      optionSelectedBg: 'rgba(24, 144, 255, 0.2)',
    },
    Button: {
      primaryShadow: '0 2px 4px rgba(24, 144, 255, 0.2)',
      defaultShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    },
    Message: {
      colorBgElevated: '#262626',
    },
    Notification: {
      colorBgElevated: '#262626',
    },
    Tooltip: {
      colorBgSpotlight: '#434343',
    },
    Popover: {
      colorBgElevated: '#262626',
    },
    Modal: {
      contentBg: '#262626',
      headerBg: '#262626',
    },
    Drawer: {
      colorBgElevated: '#262626',
    },
    Tag: {
      defaultBg: 'rgba(255, 255, 255, 0.08)',
      defaultColor: 'rgba(255, 255, 255, 0.65)',
    }
  }
};

export const getThemeConfig = (activeTheme: ActiveTheme): ThemeConfig => {
  return activeTheme === 'dark' ? darkTheme : lightTheme;
};