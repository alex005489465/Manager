import React from 'react';
import { Card, Row, Col, Input, Select, Space, Button } from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';
import { SearchFilters, RatingSentiment, DataCompleteness } from '../../types/foodItems';

const { Search } = Input;
const { Option } = Select;

interface SearchBarProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onSearch: () => void;
  loading?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  filters,
  onFiltersChange,
  onSearch,
  loading = false
}) => {
  const handleDishNameChange = (value: string) => {
    onFiltersChange({
      ...filters,
      dishName: value || undefined,
      page: 1 // 重置到第一頁
    });
  };

  const handleVendorNameChange = (value: string) => {
    onFiltersChange({
      ...filters,
      vendorName: value || undefined,
      page: 1
    });
  };

  const handleRatingSentimentChange = (value: RatingSentiment | undefined) => {
    onFiltersChange({
      ...filters,
      ratingSentiment: value,
      page: 1
    });
  };

  const handleDataCompletenessChange = (value: DataCompleteness | undefined) => {
    onFiltersChange({
      ...filters,
      dataCompleteness: value,
      page: 1
    });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      page: 1,
      pageSize: filters.pageSize || 20
    });
    onSearch();
  };

  const hasFilters = filters.dishName || filters.vendorName ||
                    filters.ratingSentiment || filters.dataCompleteness;

  return (
    <Card
      title="搜尋與篩選"
      style={{ marginBottom: 16 }}
      extra={
        <Space>
          {hasFilters && (
            <Button
              icon={<ClearOutlined />}
              onClick={handleClearFilters}
              disabled={loading}
            >
              清除篩選
            </Button>
          )}
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={onSearch}
            loading={loading}
          >
            搜尋
          </Button>
        </Space>
      }
    >
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>料理名稱</div>
            <Search
              placeholder="輸入料理名稱"
              value={filters.dishName || ''}
              onChange={(e) => handleDishNameChange(e.target.value)}
              onSearch={onSearch}
              disabled={loading}
              allowClear
            />
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>店家名稱</div>
            <Search
              placeholder="輸入店家名稱"
              value={filters.vendorName || ''}
              onChange={(e) => handleVendorNameChange(e.target.value)}
              onSearch={onSearch}
              disabled={loading}
              allowClear
            />
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>評價情感</div>
            <Select
              placeholder="選擇評價情感"
              value={filters.ratingSentiment}
              onChange={handleRatingSentimentChange}
              style={{ width: '100%' }}
              disabled={loading}
              allowClear
            >
              <Option value="positive">正面評價</Option>
              <Option value="negative">負面評價</Option>
              <Option value="neutral">中性評價</Option>
            </Select>
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>資料完整度</div>
            <Select
              placeholder="選擇資料完整度"
              value={filters.dataCompleteness}
              onChange={handleDataCompletenessChange}
              style={{ width: '100%' }}
              disabled={loading}
              allowClear
            >
              <Option value="complete">完整資料</Option>
              <Option value="partial">部分資料</Option>
              <Option value="minimal">最少資料</Option>
            </Select>
          </div>
        </Col>
      </Row>
    </Card>
  );
};