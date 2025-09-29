FROM php:7.4-fpm-alpine

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

# 安裝 PSR 擴展（Phalcon 依賴）
RUN pecl install psr-1.2.0 \
    && docker-php-ext-enable psr

# 安裝 Phalcon 擴展
RUN pecl install phalcon-4.1.2 \
    && echo "extension=phalcon.so" > /usr/local/etc/php/conf.d/docker-php-ext-phalcon.ini

# 安裝 Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# 設定工作目錄
WORKDIR /app

# 先複製所有應用程式文件
COPY . .

# 安裝 PHP 依賴
RUN composer install --no-dev --optimize-autoloader --no-interaction

# 創建日誌目錄
RUN mkdir -p /app/logs && \
    chown -R www-data:www-data /app/logs && \
    chmod -R 755 /app/logs

# 健康檢查 - 檢查 PHP-FPM 進程是否運行
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD pgrep php-fpm >/dev/null || exit 1

EXPOSE 9000

CMD ["php-fpm"]