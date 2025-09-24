package modules.fooditem.service;

import modules.fooditem.dto.FoodItemDTO;
import modules.fooditem.dto.FoodItemQueryRequest;
import modules.fooditem.dto.PagedResponse;
import modules.fooditem.entity.ExtractedFoodItem;
import modules.fooditem.entity.ExtractedFoodItem.DataCompleteness;
import modules.fooditem.entity.ExtractedFoodItem.RatingSentiment;
import modules.fooditem.repository.ExtractedFoodItemRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class ExtractedFoodItemService {

  @Autowired private ExtractedFoodItemRepository repository;

  public PagedResponse<FoodItemDTO> queryFoodItems(FoodItemQueryRequest request) {
    // 建立分頁參數 (轉換為 0-based)
    Pageable pageable = PageRequest.of(request.getPage() - 1, request.getPageSize());

    // 解析查詢參數
    RatingSentiment ratingSentiment = parseRatingSentiment(request.getRatingSentiment());
    DataCompleteness dataCompleteness = parseDataCompleteness(request.getDataCompleteness());
    String dishName = StringUtils.hasText(request.getDishName()) ? request.getDishName() : null;
    String vendorName = StringUtils.hasText(request.getVendorName()) ? request.getVendorName() : null;

    // 執行查詢
    Page<ExtractedFoodItem> entityPage =
        repository.findWithFilters(ratingSentiment, dataCompleteness, dishName, vendorName, pageable);

    // 轉換實體為 DTO
    Page<FoodItemDTO> dtoPage = entityPage.map(FoodItemDTO::fromEntity);

    // 轉換為分頁回應格式
    return PagedResponse.fromPage(dtoPage);
  }

  private RatingSentiment parseRatingSentiment(String sentiment) {
    if (!StringUtils.hasText(sentiment)) {
      return null;
    }
    try {
      return RatingSentiment.valueOf(sentiment.toLowerCase());
    } catch (IllegalArgumentException e) {
      return null; // 無效值時返回 null，讓查詢忽略此條件
    }
  }

  private DataCompleteness parseDataCompleteness(String completeness) {
    if (!StringUtils.hasText(completeness)) {
      return null;
    }
    try {
      return DataCompleteness.valueOf(completeness.toLowerCase());
    } catch (IllegalArgumentException e) {
      return null; // 無效值時返回 null，讓查詢忽略此條件
    }
  }
}