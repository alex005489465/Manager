package shared.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** 統一API回應格式 - 符合設計文件規範 { success, code, message, data } */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

  /** 操作是否成功 */
  private boolean success;

  /** 回應代碼 */
  private String code;

  /** 回應訊息 */
  private String message;

  /** 回應資料 */
  private T data;

  /**
   * 建立成功回應
   *
   * @param data 回應資料
   * @return 成功的API回應
   */
  public static <T> ApiResponse<T> success(T data) {
    return ApiResponse.<T>builder()
        .success(true)
        .code("SUCCESS")
        .message("操作成功")
        .data(data)
        .build();
  }

  /**
   * 建立成功回應附自定義訊息
   *
   * @param data 回應資料
   * @param message 成功訊息
   * @return 成功的API回應
   */
  public static <T> ApiResponse<T> success(T data, String message) {
    return ApiResponse.<T>builder()
        .success(true)
        .code("SUCCESS")
        .message(message)
        .data(data)
        .build();
  }

  /**
   * 建立錯誤回應
   *
   * @param code 錯誤代碼
   * @param message 錯誤訊息
   * @return 錯誤的API回應
   */
  public static <T> ApiResponse<T> error(String code, String message) {
    return ApiResponse.<T>builder().success(false).code(code).message(message).data(null).build();
  }
}
