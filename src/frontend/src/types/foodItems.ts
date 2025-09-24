export type RatingSentiment = 'positive' | 'negative' | 'neutral';
export type DataCompleteness = 'complete' | 'partial' | 'minimal';

export interface FoodItem {
  dishName: string;
  vendorName: string;
  description: string;
  price: string;
  ratingSentiment: RatingSentiment;
  dataCompleteness: DataCompleteness;
}

export interface PaginationInfo {
  page: number;
  pageSize: number;
  totalElements: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface FoodItemsResponse {
  success: boolean;
  code: string;
  message: string;
  data: {
    content: FoodItem[];
  } & PaginationInfo;
}

export interface SearchFilters {
  page?: number;
  pageSize?: number;
  ratingSentiment?: RatingSentiment;
  dataCompleteness?: DataCompleteness;
  dishName?: string;
  vendorName?: string;
}

export interface ApiError {
  success: false;
  code: string;
  message: string;
  data: null;
}