package shared.exception;

import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import shared.constant.ErrorCode;
import shared.dto.ApiResponse;

/** 全域異常處理器 @Spec: 待設計文件 - 錯誤回應格式標準 */
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

  /**
   * 業務異常處理 @Spec: 待設計文件 - 業務錯誤回應格式
   *
   * @param e 業務異常
   * @return 錯誤回應，HTTP狀態碼統一為200
   */
  @ExceptionHandler(BusinessException.class)
  public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
    log.warn("業務異常: code={}, message={}", e.getCode(), e.getMessage());

    return ResponseEntity.ok(ApiResponse.error(e.getCode(), e.getMessage()));
  }

  /**
   * 參數驗證異常處理 @Spec: 待設計文件 - 驗證錯誤回應格式
   *
   * @param e 參數驗證異常
   * @return 驗證錯誤回應
   */
  @ExceptionHandler(MethodArgumentNotValidException.class)
  public ResponseEntity<ApiResponse<Void>> handleValidationException(
      MethodArgumentNotValidException e) {
    String errorMessage =
        e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));

    log.warn("參數驗證失敗: {}", errorMessage);

    return ResponseEntity.ok(ApiResponse.error(ErrorCode.VALIDATION_ERROR.getCode(), errorMessage));
  }

  /**
   * 系統異常處理 @Spec: 待設計文件 - 系統錯誤回應格式
   *
   * @param e 系統異常
   * @return 系統錯誤回應
   */
  @ExceptionHandler(Exception.class)
  public ResponseEntity<ApiResponse<Void>> handleSystemException(Exception e) {
    log.error("系統異常", e);

    return ResponseEntity.ok(ApiResponse.error(ErrorCode.SYSTEM_ERROR.getCode(), "系統內部錯誤"));
  }
}
