import React from 'react';
import { ConfigProvider } from 'antd';
import zhTW from 'antd/locale/zh_TW';
import { FoodItemsPage } from './components/FoodItems';

function App() {
  return (
    <ConfigProvider locale={zhTW}>
      <FoodItemsPage />
    </ConfigProvider>
  );
}

export default App;