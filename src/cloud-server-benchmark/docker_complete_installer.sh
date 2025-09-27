#!/bin/bash

# Docker 和 Docker Compose 完整一鍵安裝腳本
# 包含安裝、配置、權限設置和測試
# 支持 Ubuntu/Debian, CentOS/RHEL/Fedora, Amazon Linux

set -e  # 遇到錯誤時立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 輸出函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${CYAN}${BOLD}=== $1 ===${NC}\n"
}

# 顯示開始界面
show_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                  Docker 一鍵安裝腳本                          ║
║              Docker + Docker Compose 完整安裝                 ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${BLUE}功能特性：${NC}"
    echo "  ✓ 自動檢測操作系統"
    echo "  ✓ 安裝最新版 Docker 和 Docker Compose"
    echo "  ✓ 配置用戶權限 (免 sudo 使用)"
    echo "  ✓ 系統服務配置"
    echo "  ✓ 完整功能測試"
    echo "  ✓ 支持多種 Linux 發行版"
    echo
}

# 檢查是否為 root 用戶
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此腳本需要 root 權限運行"
        log_info "請使用 sudo 運行: sudo $0"
        exit 1
    fi
}

# 檢測操作系統
detect_os() {
    log_step "檢測系統環境"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        OS_NAME=$PRETTY_NAME
    else
        log_error "無法檢測操作系統"
        exit 1
    fi
    
    log_info "檢測到操作系統: $OS_NAME"
    log_info "系統架構: $(uname -m)"
}

# 更新系統包
update_system() {
    log_step "更新系統包"
    
    case $OS in
        ubuntu|debian)
            log_info "更新 APT 包索引..."
            apt-get update -y
            apt-get install -y ca-certificates curl gnupg lsb-release
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                log_info "使用 DNF 更新系統..."
                dnf update -y
                dnf install -y ca-certificates curl gnupg
            else
                log_info "使用 YUM 更新系統..."
                yum update -y
                yum install -y ca-certificates curl
            fi
            ;;
        amzn)
            log_info "更新 Amazon Linux..."
            yum update -y
            # Amazon Linux 已有 curl-minimal，跳過 curl 安裝避免衝突
            yum install -y ca-certificates 2>/dev/null || true
            ;;
        *)
            log_warning "未知的操作系統，嘗試通用安裝方式"
            ;;
    esac
    
    log_success "系統更新完成"
}

# 卸載舊版本 Docker
remove_old_docker() {
    log_step "清理舊版本 Docker"
    
    case $OS in
        ubuntu|debian)
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            ;;
        centos|rhel|fedora|amzn)
            if command -v dnf &> /dev/null; then
                dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine 2>/dev/null || true
            else
                yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine 2>/dev/null || true
            fi
            ;;
    esac
    
    log_success "舊版本清理完成"
}

# 安裝 Docker
install_docker() {
    log_step "安裝 Docker Engine"
    
    case $OS in
        ubuntu|debian)
            log_info "配置 Docker APT 倉庫..."
            # 添加 Docker 的官方 GPG 密鑰
            install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            chmod a+r /etc/apt/keyrings/docker.gpg
            
            # 添加 Docker 倉庫
            echo "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # 安裝 Docker Engine
            log_info "安裝 Docker Engine..."
            apt-get update -y
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        centos|rhel)
            log_info "配置 Docker YUM 倉庫..."
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            
            log_info "安裝 Docker Engine..."
            yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        fedora)
            log_info "配置 Docker DNF 倉庫..."
            dnf install -y dnf-plugins-core
            dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            
            log_info "安裝 Docker Engine..."
            dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        amzn)
            log_info "使用 Amazon Linux 包管理器安裝 Docker..."
            # Amazon Linux 使用系統包
            if amazon-linux-extras list | grep -q docker 2>/dev/null; then
                amazon-linux-extras install docker -y
            else
                yum install -y docker
            fi
            ;;
            
        *)
            log_error "不支持的操作系統: $OS"
            exit 1
            ;;
    esac
    
    log_success "Docker Engine 安裝完成"
}

# 安裝 Docker Compose 獨立版本
install_docker_compose() {
    log_step "安裝 Docker Compose 獨立版本"
    
    # 獲取最新版本號
    log_info "獲取 Docker Compose 最新版本..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
    
    # 如果無法獲取版本，使用備用版本
    if [ -z "$DOCKER_COMPOSE_VERSION" ]; then
        DOCKER_COMPOSE_VERSION="v2.24.1"
        log_warning "無法獲取最新版本，使用備用版本: $DOCKER_COMPOSE_VERSION"
    else
        log_info "檢測到最新版本: $DOCKER_COMPOSE_VERSION"
    fi
    
    # 下載並安裝 Docker Compose
    log_info "下載 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # 創建軟連接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_success "Docker Compose 獨立版本安裝完成"
}

# 配置 Docker 服務和優化
configure_docker() {
    log_step "配置 Docker 服務"
    
    # 啟動並設置開機自啟
    log_info "啟動 Docker 服務..."
    systemctl start docker
    systemctl enable docker
    
    # 創建 Docker 配置目錄
    mkdir -p /etc/docker
    
    # 優化 Docker 配置
    log_info "優化 Docker 配置..."
    cat > /etc/docker/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "live-restore": true
}
EOF
    
    # 重啟 Docker 以應用配置
    systemctl restart docker
    
    log_success "Docker 服務配置完成"
}

# 設置用戶權限
setup_user_permissions() {
    log_step "設置用戶權限"
    
    # 獲取實際用戶名
    if [ ! -z "$SUDO_USER" ]; then
        USERNAME=$SUDO_USER
    else
        USERNAME=$(logname 2>/dev/null || whoami)
    fi
    
    log_info "為用戶 $USERNAME 設置 Docker 權限..."
    
    # 確保 docker 組存在
    if ! getent group docker > /dev/null 2>&1; then
        groupadd docker
        log_info "已創建 docker 組"
    fi
    
    # 將用戶添加到 docker 組
    usermod -aG docker $USERNAME
    
    # 修改 docker socket 權限
    chown root:docker /var/run/docker.sock
    chmod 666 /var/run/docker.sock  # 臨時設置為可讀寫
    
    log_success "用戶 $USERNAME 已添加到 docker 組"
    log_warning "權限已設置，用戶可以不用 sudo 運行 Docker"
}

# 驗證安裝
verify_installation() {
    log_step "驗證安裝"
    
    # 檢查 Docker 版本
    log_info "檢查 Docker 版本..."
    if DOCKER_VERSION=$(docker --version 2>/dev/null); then
        log_success "Docker 安裝成功: $DOCKER_VERSION"
    else
        log_error "Docker 安裝失敗"
        return 1
    fi
    
    # 檢查 Docker Compose Plugin 版本
    if COMPOSE_PLUGIN_VERSION=$(docker compose version 2>/dev/null); then
        log_success "Docker Compose Plugin: $COMPOSE_PLUGIN_VERSION"
    else
        log_info "Docker Compose Plugin 未安裝 (可選)"
    fi
    
    # 檢查 Docker Compose 獨立版本
    if COMPOSE_VERSION=$(docker-compose --version 2>/dev/null); then
        log_success "Docker Compose 獨立版本: $COMPOSE_VERSION"
    else
        log_warning "Docker Compose 獨立版本安裝失敗"
    fi
    
    # 檢查 Docker 服務狀態
    if systemctl is-active --quiet docker; then
        log_success "Docker 服務正在運行"
    else
        log_error "Docker 服務未運行"
        return 1
    fi
    
    # 運行測試容器
    log_info "運行功能測試..."
    if docker run --rm hello-world > /dev/null 2>&1; then
        log_success "Docker 功能測試通過"
    else
        log_warning "Docker 功能測試失敗 (可能是權限問題)"
    fi
    
    return 0
}

# 創建使用說明文件
create_documentation() {
    log_step "創建使用說明"
    
    USERNAME=${SUDO_USER:-$(logname 2>/dev/null || whoami)}
    
    cat > /home/$USERNAME/Docker_Quick_Guide.md << 'EOF'
# Docker 快速使用指南

## 🚀 安裝完成

恭喜！Docker 和 Docker Compose 已成功安裝並配置完成。

## 📋 基本命令

### Docker 基礎命令
```bash
# 查看版本
docker --version

# 運行測試容器
docker run hello-world

# 查看運行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看本地鏡像
docker images

# 搜索鏡像
docker search nginx

# 拉取鏡像
docker pull nginx

# 運行容器 (後台運行)
docker run -d --name my-nginx -p 8080:80 nginx

# 查看容器日志
docker logs my-nginx

# 進入容器
docker exec -it my-nginx /bin/bash

# 停止容器
docker stop my-nginx

# 移除容器
docker rm my-nginx

# 移除鏡像
docker rmi nginx
```

### Docker Compose 命令
```bash
# 查看版本
docker-compose --version

# 啟動服務 (需要 docker-compose.yml)
docker-compose up -d

# 停止服務
docker-compose down

# 查看服務日志
docker-compose logs

# 查看服務狀態
docker-compose ps

# 重新構建並啟動
docker-compose up --build -d
```

## 🔧 系統管理

### Docker 服務管理
```bash
# 啟動 Docker 服務
sudo systemctl start docker

# 停止 Docker 服務
sudo systemctl stop docker

# 重啟 Docker 服務
sudo systemctl restart docker

# 查看服務狀態
sudo systemctl status docker

# 開機自啟動
sudo systemctl enable docker
```

### 清理資源
```bash
# 清理未使用的容器
docker container prune

# 清理未使用的鏡像
docker image prune

# 清理未使用的網絡
docker network prune

# 清理所有未使用資源
docker system prune -a
```

## 📝 快速示例

### 1. 運行 Nginx Web 服務器
```bash
docker run -d --name web-server -p 8080:80 nginx
# 訪問 http://localhost:8080
```

### 2. 運行 MySQL 數據庫
```bash
docker run -d --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=mypassword \
  -e MYSQL_DATABASE=testdb \
  -p 3306:3306 mysql:8.0
```

### 3. 創建 Docker Compose 項目
```bash
# 創建項目目錄
mkdir my-app && cd my-app

# 創建 docker-compose.yml
cat > docker-compose.yml << 'YAML'
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
YAML

# 創建網頁內容
mkdir html
echo "<h1>Hello Docker Compose!</h1>" > html/index.html

# 啟動服務
docker-compose up -d

# 查看狀態
docker-compose ps
```

## 🛠️ 故障排除

### 權限問題
如果遇到權限錯誤：
```bash
# 檢查用戶是否在 docker 組
groups $USER

# 如果不在，重新登錄或運行：
newgrp docker

# 或者重新啟動會話
```

### 服務問題
```bash
# 檢查 Docker 服務狀態
sudo systemctl status docker

# 查看 Docker 日志
sudo journalctl -u docker.service

# 重啟 Docker 服務
sudo systemctl restart docker
```

## 📚 學習資源

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/) - 官方鏡像倉庫

---
**安裝時間**: $(date)
**腳本版本**: 2.0 一鍵安裝版本
EOF

    chown $USERNAME:$USERNAME /home/$USERNAME/Docker_Quick_Guide.md
    log_success "使用說明已創建: /home/$USERNAME/Docker_Quick_Guide.md"
}

# 顯示完成信息
show_completion() {
    USERNAME=${SUDO_USER:-$(logname 2>/dev/null || whoami)}
    
    echo
    echo -e "${GREEN}${BOLD}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🎉 安裝完成！                             ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${CYAN}📦 已安裝組件：${NC}"
    docker --version 2>/dev/null | sed 's/^/  ✓ /'
    docker-compose --version 2>/dev/null | sed 's/^/  ✓ /'
    
    echo
    echo -e "${CYAN}🔧 系統配置：${NC}"
    echo "  ✓ Docker 服務已啟動並設置開機自啟"
    echo "  ✓ 用戶 $USERNAME 已添加到 docker 組"
    echo "  ✓ 可以不使用 sudo 運行 Docker 命令"
    echo "  ✓ Docker daemon 已優化配置"
    
    echo
    echo -e "${CYAN}🚀 快速測試：${NC}"
    echo -e "  ${YELLOW}docker run hello-world${NC}        # 測試 Docker"
    echo -e "  ${YELLOW}docker-compose --version${NC}      # 測試 Docker Compose"
    echo -e "  ${YELLOW}docker ps${NC}                     # 查看運行容器"
    
    echo
    echo -e "${CYAN}📖 使用說明：${NC}"
    echo "  📄 詳細說明文件: /home/$USERNAME/Docker_Quick_Guide.md"
    
    echo
    echo -e "${GREEN}Docker 和 Docker Compose 已準備就緒，開始您的容器化之旅吧！${NC}"
    echo
}

# 主函數
main() {
    show_banner
    
    # 檢查權限
    check_root
    
    # 系統檢測和準備
    detect_os
    update_system
    remove_old_docker
    
    # 安裝 Docker 和 Docker Compose
    install_docker
    install_docker_compose
    
    # 配置和權限設置
    configure_docker
    setup_user_permissions
    
    # 驗證安裝
    if verify_installation; then
        log_success "所有組件安裝驗證通過"
    else
        log_error "部分組件可能存在問題，請檢查上述錯誤信息"
    fi
    
    # 創建文檔和完成信息
    create_documentation
    show_completion
}

# 運行主函數
main "$@"