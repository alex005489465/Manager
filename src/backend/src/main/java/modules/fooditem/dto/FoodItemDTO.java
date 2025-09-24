package modules.fooditem.dto;

import lombok.Data;
import modules.fooditem.entity.ExtractedFoodItem;

@Data
public class FoodItemDTO {

  private String dishName;

  private String vendorName;

  private String description;

  private String price;

  private String ratingSentiment;

  private String dataCompleteness;

  public static FoodItemDTO fromEntity(ExtractedFoodItem entity) {
    FoodItemDTO dto = new FoodItemDTO();
    dto.setDishName(entity.getDishName());
    dto.setVendorName(entity.getVendorName());
    dto.setDescription(entity.getDescription());
    dto.setPrice(entity.getPrice());
    dto.setRatingSentiment(
        entity.getRatingSentiment() != null ? entity.getRatingSentiment().name() : null);
    dto.setDataCompleteness(
        entity.getDataCompleteness() != null ? entity.getDataCompleteness().name() : null);
    return dto;
  }
}