package shared.exception;

public class ValidationException extends BusinessException {

  public ValidationException(String code, String message) {
    super(code, message);
  }

  public ValidationException(String code, String message, Throwable cause) {
    super(code, message, cause);
  }
}
