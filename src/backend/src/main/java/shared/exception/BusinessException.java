package shared.exception;

import lombok.Getter;

/** 業務異常基類 @Spec: 待設計文件 - 錯誤碼定義標準 */
@Getter
public class BusinessException extends RuntimeException {

  /** 錯誤代碼 */
  private final String code;

  /**
   * 建構業務異常
   *
   * @param code 錯誤代碼 (應對應設計文件中的錯誤碼定義)
   * @param message 錯誤訊息 (應使用設計文件中的精確用詞)
   */
  public BusinessException(String code, String message) {
    super(message);
    this.code = code;
  }

  /**
   * 建構業務異常含原因
   *
   * @param code 錯誤代碼
   * @param message 錯誤訊息
   * @param cause 原始異常
   */
  public BusinessException(String code, String message, Throwable cause) {
    super(message, cause);
    this.code = code;
  }
}
