package modules.fooditem.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Data;

@Data
public class FoodItemQueryRequest {

  @Min(value = 1, message = "頁碼必須大於0")
  private Integer page = 1;

  @Min(value = 1, message = "每頁數量必須大於0")
  @Max(value = 100, message = "每頁數量不能超過100")
  private Integer pageSize = 20;

  private String ratingSentiment;

  private String dataCompleteness;

  private String dishName;

  private String vendorName;
}