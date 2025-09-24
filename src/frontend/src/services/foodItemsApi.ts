import { SearchFilters, FoodItemsResponse } from '../types/foodItems';

const API_BASE_URL = '';

class FoodItemsApi {
  private async fetchJson<T>(url: string): Promise<T> {
    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private buildQueryParams(filters: SearchFilters): string {
    const params = new URLSearchParams();

    if (filters.page) params.append('page', filters.page.toString());
    if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());
    if (filters.ratingSentiment) params.append('ratingSentiment', filters.ratingSentiment);
    if (filters.dataCompleteness) params.append('dataCompleteness', filters.dataCompleteness);
    if (filters.dishName?.trim()) params.append('dishName', filters.dishName.trim());
    if (filters.vendorName?.trim()) params.append('vendorName', filters.vendorName.trim());

    return params.toString();
  }

  async getFoodItems(filters: SearchFilters = {}): Promise<FoodItemsResponse> {
    const queryParams = this.buildQueryParams(filters);
    const url = `${API_BASE_URL}/api/food-items${queryParams ? `?${queryParams}` : ''}`;

    return this.fetchJson<FoodItemsResponse>(url);
  }

}

export const foodItemsApi = new FoodItemsApi();