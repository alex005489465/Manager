package shared.util;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.stereotype.Component;

/** 批次號生成器 格式：BATCH_YYYYMMDD_001 */
@Component
public class BatchNumberGenerator {

  // 暫時使用內存計數器，實際應查詢資料庫
  private static final AtomicInteger dailyCounter = new AtomicInteger(0);
  private static String lastGeneratedDate = "";

  /**
   * 生成批次號
   *
   * @return 批次號字符串
   */
  public String generate() {
    String currentDate = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
    String datePrefix = "BATCH_" + currentDate;

    // 如果是新的一天，重置計數器
    if (!currentDate.equals(lastGeneratedDate)) {
      dailyCounter.set(0);
      lastGeneratedDate = currentDate;
    }

    // 遞增序號
    int sequence = dailyCounter.incrementAndGet();

    return datePrefix + "_" + String.format("%03d", sequence);
  }

  /**
   * 獲取當日序號（預留給資料庫實現）
   *
   * @param datePrefix 日期前綴
   * @return 下一個序號
   */
  private int getNextSequence(String datePrefix) {
    // TODO: 實現邏輯：查詢資料庫獲取當日最大序號+1
    // 例如：SELECT MAX(SUBSTRING(batch_number, -3)) FROM production_records
    //       WHERE batch_number LIKE 'BATCH_20250914_%'
    return dailyCounter.incrementAndGet();
  }
}
