package shared.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

// @Configuration
// @EnableTransactionManagement
// @EnableJpaRepositories(
//     basePackages = "repository.primary",
//     entityManagerFactoryRef = "primaryEntityManagerFactory",
//     transactionManagerRef = "primaryTransactionManager")
public class PrimaryRepositoryConfig {}