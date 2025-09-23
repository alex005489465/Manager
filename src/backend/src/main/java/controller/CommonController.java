package controller;

import java.time.Instant;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import shared.dto.ApiResponse;

/** 普通控制器 - 提供系統基礎API端點 */
@RestController
@Slf4j
public class CommonController {

  /**
   * 根端點 - 返回應用基本資訊
   *
   * @return 應用基本資訊
   */
  @GetMapping("/")
  public ResponseEntity<ApiResponse<Map<String, Object>>> root() {
    log.info("訪問根端點");

    Map<String, Object> data =
        Map.of(
            "app", "Manager 系統",
            "version", "0.1.0",
            "status", "running");

    return ResponseEntity.ok(ApiResponse.success(data, "Manager 系統運行中"));
  }

  /**
   * 健康檢查端點
   *
   * @return 服務健康狀態
   */
  @GetMapping("/health")
  public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
    log.info("訪問健康檢查端點");

    Map<String, Object> data = Map.of("status", "UP", "timestamp", Instant.now().toString());

    return ResponseEntity.ok(ApiResponse.success(data, "服務健康"));
  }

  /**
   * API健康檢查端點
   *
   * @return API服務健康狀態
   */
  @GetMapping("/api/health")
  public ResponseEntity<ApiResponse<Map<String, Object>>> apiHealth() {
    log.info("訪問API健康檢查端點");

    Map<String, Object> data =
        Map.of(
            "status", "UP",
            "timestamp", Instant.now().toString(),
            "api_version", "0.1.0");

    return ResponseEntity.ok(ApiResponse.success(data, "API服務健康"));
  }
}
