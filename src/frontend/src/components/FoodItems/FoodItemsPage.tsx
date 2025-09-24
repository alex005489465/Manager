import React, { useState, useEffect, useCallback } from 'react';
import { Layout, message, Typography, Space } from 'antd';
import { SearchBar } from './SearchBar';
import { FoodItemsTable } from './FoodItemsTable';
import { SearchFilters, FoodItem, PaginationInfo } from '../../types/foodItems';
import { foodItemsApi } from '../../services/foodItemsApi';

const { Content, Header } = Layout;
const { Title } = Typography;

export const FoodItemsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [foodItems, setFoodItems] = useState<FoodItem[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    pageSize: 20,
    totalElements: 0,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false
  });
  const [filters, setFilters] = useState<SearchFilters>({
    page: 1,
    pageSize: 20
  });


  const fetchFoodItems = useCallback(async (searchFilters: SearchFilters) => {
    setLoading(true);
    // 清空舊資料，確保不會顯示陳舊資料
    setFoodItems([]);
    setPagination(prev => ({ ...prev, totalElements: 0 }));

    try {
      const response = await foodItemsApi.getFoodItems(searchFilters);

      if (response.success) {
        setFoodItems(response.data.content);
        setPagination({
          page: response.data.page,
          pageSize: response.data.pageSize,
          totalElements: response.data.totalElements,
          totalPages: response.data.totalPages,
          hasNext: response.data.hasNext,
          hasPrevious: response.data.hasPrevious
        });
      } else {
        message.error(response.message || '獲取數據失敗');
        setFoodItems([]);
        setPagination(prev => ({ ...prev, totalElements: 0 }));
      }
    } catch (error) {
      console.error('Failed to fetch food items:', error);
      message.error('網路請求失敗，請稍後再試');
      setFoodItems([]);
      setPagination(prev => ({ ...prev, totalElements: 0 }));
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = useCallback(() => {
    fetchFoodItems(filters);
  }, [filters, fetchFoodItems]);

  const handleFiltersChange = useCallback((newFilters: SearchFilters) => {
    setFilters(newFilters);
    // 簡化邏輯：所有篩選條件變更都立即搜尋
    fetchFoodItems(newFilters);
  }, [fetchFoodItems]);

  const handlePaginationChange = useCallback((page: number, pageSize: number) => {
    const newFilters = {
      ...filters,
      page,
      pageSize
    };
    setFilters(newFilters);
    fetchFoodItems(newFilters);
  }, [filters, fetchFoodItems]);

  // 初始載入數據
  useEffect(() => {
    fetchFoodItems(filters);
  }, [fetchFoodItems]);

  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Header style={{
        backgroundColor: '#fff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        padding: '0 24px'
      }}>
        <Space align="center" style={{ height: '100%' }}>
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
            食物項目管理系統
          </Title>
        </Space>
      </Header>

      <Content style={{ padding: '24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <SearchBar
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onSearch={handleSearch}
            loading={loading}
          />

          <FoodItemsTable
            data={foodItems}
            pagination={pagination}
            loading={loading}
            onPaginationChange={handlePaginationChange}
          />
        </div>
      </Content>
    </Layout>
  );
};