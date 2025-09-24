import React from 'react';
import { Table, Tag, Card, Pagination, Typography, Tooltip } from 'antd';
import { ColumnsType } from 'antd/es/table';
import { FoodItem, PaginationInfo, RatingSentiment, DataCompleteness } from '../../types/foodItems';

const { Paragraph } = Typography;

interface FoodItemsTableProps {
  data: FoodItem[];
  pagination: PaginationInfo;
  loading?: boolean;
  onPaginationChange: (page: number, pageSize: number) => void;
}

export const FoodItemsTable: React.FC<FoodItemsTableProps> = ({
  data,
  pagination,
  loading = false,
  onPaginationChange
}) => {
  const getSentimentColor = (sentiment: RatingSentiment): string => {
    switch (sentiment) {
      case 'positive': return 'green';
      case 'negative': return 'red';
      case 'neutral': return 'default';
      default: return 'default';
    }
  };

  const getSentimentText = (sentiment: RatingSentiment): string => {
    switch (sentiment) {
      case 'positive': return '正面評價';
      case 'negative': return '負面評價';
      case 'neutral': return '中性評價';
      default: return '未知';
    }
  };

  const getCompletenessColor = (completeness: DataCompleteness): string => {
    switch (completeness) {
      case 'complete': return 'blue';
      case 'partial': return 'orange';
      case 'minimal': return 'volcano';
      default: return 'default';
    }
  };

  const getCompletenessText = (completeness: DataCompleteness): string => {
    switch (completeness) {
      case 'complete': return '完整資料';
      case 'partial': return '部分資料';
      case 'minimal': return '最少資料';
      default: return '未知';
    }
  };

  const columns: ColumnsType<FoodItem> = [
    {
      title: '料理名稱',
      dataIndex: 'dishName',
      key: 'dishName',
      width: 150,
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <span style={{ fontWeight: 500 }}>{text}</span>
        </Tooltip>
      )
    },
    {
      title: '店家名稱',
      dataIndex: 'vendorName',
      key: 'vendorName',
      width: 150,
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          {text}
        </Tooltip>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 300,
      render: (text: string) => (
        <Paragraph
          ellipsis={{
            rows: 2,
            expandable: true,
            symbol: '展開'
          }}
          style={{ margin: 0 }}
        >
          {text}
        </Paragraph>
      )
    },
    {
      title: '價格',
      dataIndex: 'price',
      key: 'price',
      width: 80,
      align: 'right',
      render: (text: string) => (
        <span style={{ fontWeight: 500, color: '#ff4d4f' }}>{text}</span>
      )
    },
    {
      title: '評價情感',
      dataIndex: 'ratingSentiment',
      key: 'ratingSentiment',
      width: 100,
      align: 'center',
      render: (sentiment: RatingSentiment) => (
        <Tag color={getSentimentColor(sentiment)}>
          {getSentimentText(sentiment)}
        </Tag>
      )
    },
    {
      title: '資料完整度',
      dataIndex: 'dataCompleteness',
      key: 'dataCompleteness',
      width: 100,
      align: 'center',
      render: (completeness: DataCompleteness) => (
        <Tag color={getCompletenessColor(completeness)}>
          {getCompletenessText(completeness)}
        </Tag>
      )
    }
  ];

  return (
    <Card
      title="食物項目列表"
      extra={
        pagination.totalElements > 0 && (
          <Pagination
            current={pagination.page}
            total={pagination.totalElements}
            pageSize={pagination.pageSize}
            onChange={onPaginationChange}
            onShowSizeChange={onPaginationChange}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
            }
            pageSizeOptions={['10', '20', '50', '100']}
            disabled={loading}
            size="small"
          />
        )
      }
    >
      <Table<FoodItem>
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={false}
        rowKey={(record) => `${record.dishName}-${record.vendorName}`}
        scroll={{ x: 880 }}
        size="small"
      />

      {pagination.totalElements === 0 && !loading && (
        <div style={{
          textAlign: 'center',
          padding: '48px 0',
          color: '#999'
        }}>
          暫無資料
        </div>
      )}
    </Card>
  );
};