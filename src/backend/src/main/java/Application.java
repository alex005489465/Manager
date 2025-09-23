import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Manager System - Manager 系統 純Web API應用程式啟動類
 *
 * <p>專案特性: - 純Web API專案，不含視圖或靜態資源 - 禁用REST規範，僅使用GET和POST方法 - 功能導向分層架構 - 設計文件驅動開發
 */
@SpringBootApplication
@ComponentScan(basePackages = {"shared", "modules", "controller"})
@EnableJpaRepositories(basePackages = "modules")
@EntityScan(basePackages = "modules")
public class Application {

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
