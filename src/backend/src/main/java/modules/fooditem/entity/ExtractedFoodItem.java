package modules.fooditem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@Entity
@Table(name = "extracted_food_items")
public class ExtractedFoodItem {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "review_id", nullable = false)
  private Long reviewId;

  @Column(name = "dish_name", length = 100)
  private String dishName;

  @Column(name = "vendor_name", length = 100)
  private String vendorName;

  @Column(name = "description", columnDefinition = "TEXT")
  private String description;

  @Column(name = "price", length = 50)
  private String price;

  @Enumerated(EnumType.STRING)
  @Column(name = "rating_sentiment")
  private RatingSentiment ratingSentiment;

  @Enumerated(EnumType.STRING)
  @Column(name = "data_completeness")
  private DataCompleteness dataCompleteness;

  @Column(name = "extracted_at")
  private LocalDateTime extractedAt;

  public enum RatingSentiment {
    positive, negative, neutral
  }

  public enum DataCompleteness {
    complete, partial, minimal
  }
}