package controller;

import jakarta.validation.Valid;
import modules.fooditem.dto.FoodItemDTO;
import modules.fooditem.dto.FoodItemQueryRequest;
import modules.fooditem.dto.PagedResponse;
import modules.fooditem.service.ExtractedFoodItemService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import shared.dto.ApiResponse;

@RestController
@RequestMapping("/api")
public class FoodItemController {

  @Autowired private ExtractedFoodItemService foodItemService;

  @GetMapping("/food-items")
  public ApiResponse<PagedResponse<FoodItemDTO>> queryFoodItems(
      @Valid @ModelAttribute FoodItemQueryRequest request) {

    try {
      PagedResponse<FoodItemDTO> result = foodItemService.queryFoodItems(request);
      return ApiResponse.success(result);
    } catch (Exception e) {
      return ApiResponse.error("1003", "系統內部錯誤");
    }
  }
}