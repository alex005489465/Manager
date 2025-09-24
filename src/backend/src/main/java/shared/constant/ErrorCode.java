package shared.constant;

/** 錯誤碼定義 - 符合設計文件規範 */
public enum ErrorCode {
  SUCCESS("1000", "成功"),
  VALIDATION_ERROR("1001", "參數驗證失敗"),
  DATABASE_ERROR("1002", "資料庫查詢失敗"),
  SYSTEM_ERROR("1003", "系統內部錯誤");

  private final String code;
  private final String message;

  ErrorCode(String code, String message) {
    this.code = code;
    this.message = message;
  }

  public String getCode() {
    return code;
  }

  public String getMessage() {
    return message;
  }
}
