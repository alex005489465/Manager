import React from 'react';
import { ConfigProvider } from 'antd';
import zhTW from 'antd/locale/zh_TW';

function App() {
  return (
    <ConfigProvider locale={zhTW}>
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#333',
            marginBottom: '1rem'
          }}>
            React + TypeScript + Ant Design 基礎框架
          </h1>
          <p style={{
            fontSize: '1.2rem',
            color: '#666'
          }}>
            框架已就緒，可以開始開發新功能
          </p>
        </div>
      </div>
    </ConfigProvider>
  );
}

export default App;