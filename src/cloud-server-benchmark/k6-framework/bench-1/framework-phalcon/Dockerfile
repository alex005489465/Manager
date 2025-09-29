FROM php:8.3-fpm-alpine

# 安裝系統依賴
RUN apk add --no-cache \
    curl \
    wget \
    zip \
    unzip \
    git \
    linux-headers \
    autoconf \
    gcc \
    g++ \
    make \
    zlib-dev \
    libpng-dev \
    mysql-client

# 安裝 PHP 擴展
RUN docker-php-ext-install \
    pdo \
    pdo_mysql \
    opcache

# 安裝 Phalcon 擴展
RUN pecl install phalcon-5.8.0 \
    && docker-php-ext-enable phalcon

# 安裝 Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# 設定工作目錄
WORKDIR /app

# 複製配置文件
COPY php.ini /usr/local/etc/php/php.ini
COPY php-fpm.conf /usr/local/etc/php-fpm.d/www.conf

# 複製應用程式文件
COPY composer.json composer.lock* ./
RUN composer install --no-dev --optimize-autoloader --no-interaction

COPY . .

# 創建日誌目錄
RUN mkdir -p /app/logs && \
    chown -R www-data:www-data /app/logs && \
    chmod -R 755 /app/logs

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

EXPOSE 9000

CMD ["php-fpm"]