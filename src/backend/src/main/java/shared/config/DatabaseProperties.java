package shared.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "spring.datasource")
public class DatabaseProperties {

  private DataSourceProperties primary = new DataSourceProperties();
  private DataSourceProperties reviews = new DataSourceProperties();

  @Data
  public static class DataSourceProperties {
    private String url;
    private String username;
    private String password;
    private String driverClassName;
  }

  public boolean isValidConnection(DataSourceProperties properties) {
    return properties.getUrl() != null
        && !properties.getUrl().isEmpty()
        && properties.getUsername() != null
        && !properties.getUsername().isEmpty()
        && properties.getPassword() != null
        && !properties.getPassword().isEmpty()
        && properties.getDriverClassName() != null
        && !properties.getDriverClassName().isEmpty();
  }

  public String getPrimaryDatabaseName() {
    if (primary.getUrl() != null) {
      String[] parts = primary.getUrl().split("/");
      if (parts.length > 0) {
        String dbPart = parts[parts.length - 1];
        return dbPart.split("\\?")[0];
      }
    }
    return "unknown";
  }

  public String getReviewsDatabaseName() {
    if (reviews.getUrl() != null) {
      String[] parts = reviews.getUrl().split("/");
      if (parts.length > 0) {
        String dbPart = parts[parts.length - 1];
        return dbPart.split("\\?")[0];
      }
    }
    return "unknown";
  }
}