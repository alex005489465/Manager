import React from 'react';
import { Button, Dropdown, Tooltip, Space } from 'antd';
import type { MenuProps } from 'antd';
import {
  SunOutlined,
  MoonOutlined,
  DesktopOutlined,
  DownOutlined
} from '@ant-design/icons';
import { useTheme, ThemeMode } from '../contexts/ThemeContext';

interface ThemeToggleProps {
  showText?: boolean;
  size?: 'large' | 'middle' | 'small';
  type?: 'default' | 'primary' | 'dashed' | 'link' | 'text';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  showText = false,
  size = 'middle',
  type = 'text'
}) => {
  const { themeMode, activeTheme, setThemeMode } = useTheme();

  // 獲取當前主題的圖示和文字
  const getThemeInfo = () => {
    switch (themeMode) {
      case 'light':
        return {
          icon: <SunOutlined />,
          text: '明亮模式',
          tooltip: '當前: 明亮模式'
        };
      case 'dark':
        return {
          icon: <MoonOutlined />,
          text: '暗黑模式',
          tooltip: '當前: 暗黑模式'
        };
      case 'auto':
        return {
          icon: <DesktopOutlined />,
          text: `跟隨系統 (${activeTheme === 'dark' ? '暗' : '亮'})`,
          tooltip: `當前: 跟隨系統 (${activeTheme === 'dark' ? '暗黑' : '明亮'})`
        };
      default:
        return {
          icon: <SunOutlined />,
          text: '明亮模式',
          tooltip: '當前: 明亮模式'
        };
    }
  };

  const currentTheme = getThemeInfo();

  // 下拉選單項目
  const menuItems: MenuProps['items'] = [
    {
      key: 'light',
      icon: <SunOutlined />,
      label: '明亮模式',
      onClick: () => setThemeMode('light'),
    },
    {
      key: 'dark',
      icon: <MoonOutlined />,
      label: '暗黑模式',
      onClick: () => setThemeMode('dark'),
    },
    {
      type: 'divider',
    },
    {
      key: 'auto',
      icon: <DesktopOutlined />,
      label: '跟隨系統',
      onClick: () => setThemeMode('auto'),
    },
  ];

  const buttonContent = (
    <Space size={4}>
      {currentTheme.icon}
      {showText && <span>{currentTheme.text}</span>}
      <DownOutlined style={{ fontSize: '10px' }} />
    </Space>
  );

  return (
    <Tooltip title={currentTheme.tooltip} placement="bottom">
      <Dropdown
        menu={{ items: menuItems, selectedKeys: [themeMode] }}
        placement="bottomRight"
        arrow
        trigger={['click']}
      >
        <Button
          type={type}
          size={size}
          style={{
            display: 'flex',
            alignItems: 'center',
            transition: 'all 0.3s ease'
          }}
        >
          {buttonContent}
        </Button>
      </Dropdown>
    </Tooltip>
  );
};