# ================================
# Manager 後端 API - 生產級 Docker 鏡像
# 多階段構建，優化快取與安全性
# ================================

# ==================== BUILD STAGE ====================
FROM maven:3.9.11-eclipse-temurin-21 AS builder

# 設定工作目錄
WORKDIR /build

# 複製 Maven 配置檔案（優化 Docker 快取）
COPY src/backend/pom.xml ./pom.xml

# 下載依賴（這一層會被快取，除非 pom.xml 改變）
RUN mvn dependency:go-offline -B

# 複製原始碼
COPY src/backend/src ./src

# 執行測試並構建應用
RUN mvn clean package -DskipTests=false -B

# ==================== RUNTIME STAGE ====================
FROM eclipse-temurin:21-jre-alpine AS runtime

# 安裝必要的系統工具
RUN apk --no-cache add curl dumb-init

# 建立非 root 用戶提升安全性
RUN addgroup -g 1000 manager && \
    adduser -D -s /bin/sh -u 1000 -G manager manager

# 設定工作目錄
WORKDIR /app

# 複製 JAR 檔案從 builder stage
COPY --from=builder /build/target/*.jar app.jar

# 建立日誌目錄
RUN mkdir -p /app/logs && chown -R manager:manager /app

# 切換到非 root 用戶
USER manager

# JVM 調優參數（適用於容器環境）
ENV JAVA_OPTS="-server \
    -Xmx1g \
    -Xms512m \
    -XX:+UseG1GC \
    -XX:G1HeapRegionSize=16m \
    -XX:+UseStringDeduplication \
    -XX:+OptimizeStringConcat \
    -Djava.awt.headless=true \
    -Djava.security.egd=file:/dev/./urandom \
    -Dspring.profiles.active=prod"

# 應用配置
ENV SERVER_PORT=8080
ENV MANAGEMENT_SERVER_PORT=8081

# 暴露端口
EXPOSE 8080 8081

# 健康檢查（使用 Spring Boot Actuator）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/actuator/health || exit 1

# 使用 dumb-init 作為 PID 1，處理訊號和殭屍程序
ENTRYPOINT ["dumb-init", "--"]

# 啟動應用程式
CMD ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]