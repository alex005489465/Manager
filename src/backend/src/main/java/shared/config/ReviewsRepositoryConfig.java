package shared.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
    basePackages = "modules.fooditem.repository",
    entityManagerFactoryRef = "reviewsEntityManagerFactory",
    transactionManagerRef = "reviewsTransactionManager")
public class ReviewsRepositoryConfig {}