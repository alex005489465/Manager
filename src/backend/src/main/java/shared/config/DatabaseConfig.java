package shared.config;

import jakarta.persistence.EntityManagerFactory;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
public class DatabaseConfig {

  // @Primary
  // @Bean(name = "primaryDataSource")
  // @ConfigurationProperties(prefix = "spring.datasource.primary")
  // public DataSource primaryDataSource() {
  //   return DataSourceBuilder.create().build();
  // }

  @Primary
  @Bean(name = "dataSource")
  @ConfigurationProperties(prefix = "spring.datasource.reviews")
  public DataSource reviewsDataSource() {
    return DataSourceBuilder.create().build();
  }

  // @Primary
  // @Bean(name = "primaryEntityManagerFactory")
  // public LocalContainerEntityManagerFactoryBean primaryEntityManagerFactory(
  //     @Qualifier("primaryDataSource") DataSource dataSource) {
  //
  //   LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
  //   em.setDataSource(dataSource);
  //
  //   HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
  //   em.setJpaVendorAdapter(vendorAdapter);
  //   em.setJpaPropertyMap(getJpaProperties());
  //
  //   return em;
  // }

  @Primary
  @Bean(name = "entityManagerFactory")
  public LocalContainerEntityManagerFactoryBean reviewsEntityManagerFactory(
      @Qualifier("dataSource") DataSource dataSource) {

    LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
    em.setDataSource(dataSource);
    em.setPackagesToScan("modules.fooditem.entity");

    HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
    em.setJpaVendorAdapter(vendorAdapter);
    em.setJpaPropertyMap(getJpaProperties());

    return em;
  }

  // @Primary
  // @Bean(name = "primaryTransactionManager")
  // public PlatformTransactionManager primaryTransactionManager(
  //     @Qualifier("primaryEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
  //   return new JpaTransactionManager(entityManagerFactory);
  // }

  @Primary
  @Bean(name = "transactionManager")
  public PlatformTransactionManager reviewsTransactionManager(
      @Qualifier("entityManagerFactory") EntityManagerFactory entityManagerFactory) {
    return new JpaTransactionManager(entityManagerFactory);
  }

  private Map<String, Object> getJpaProperties() {
    Map<String, Object> properties = new HashMap<>();
    properties.put("hibernate.dialect", "org.hibernate.dialect.MySQLDialect");
    properties.put("hibernate.hbm2ddl.auto", "none");
    properties.put("hibernate.show_sql", "true");
    properties.put("hibernate.format_sql", "false");
    return properties;
  }
}