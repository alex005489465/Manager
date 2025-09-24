package modules.fooditem.repository;

import modules.fooditem.entity.ExtractedFoodItem;
import modules.fooditem.entity.ExtractedFoodItem.DataCompleteness;
import modules.fooditem.entity.ExtractedFoodItem.RatingSentiment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface ExtractedFoodItemRepository extends JpaRepository<ExtractedFoodItem, Long> {

  // 基礎分頁查詢
  Page<ExtractedFoodItem> findAll(Pageable pageable);

  // 單一條件篩選
  Page<ExtractedFoodItem> findByRatingSentiment(RatingSentiment sentiment, Pageable pageable);

  Page<ExtractedFoodItem> findByDataCompleteness(DataCompleteness completeness, Pageable pageable);

  // 關鍵字搜尋
  Page<ExtractedFoodItem> findByDishNameContainingIgnoreCase(String dishName, Pageable pageable);

  Page<ExtractedFoodItem> findByVendorNameContainingIgnoreCase(String vendorName, Pageable pageable);

  // 組合條件查詢 - 使用 @Query 註解
  @Query(
      "SELECT f FROM ExtractedFoodItem f WHERE "
          + "(:ratingSentiment IS NULL OR f.ratingSentiment = :ratingSentiment) AND "
          + "(:dataCompleteness IS NULL OR f.dataCompleteness = :dataCompleteness) AND "
          + "(:dishName IS NULL OR LOWER(f.dishName) LIKE LOWER(CONCAT('%', :dishName, '%'))) AND "
          + "(:vendorName IS NULL OR LOWER(f.vendorName) LIKE LOWER(CONCAT('%', :vendorName, '%')))")
  Page<ExtractedFoodItem> findWithFilters(
      @Param("ratingSentiment") RatingSentiment ratingSentiment,
      @Param("dataCompleteness") DataCompleteness dataCompleteness,
      @Param("dishName") String dishName,
      @Param("vendorName") String vendorName,
      Pageable pageable);
}