# 雲伺服器性能測試專案概覽

## 🎯 專案目標

測試不同型號的雲伺服器性能，使用三個相同型號的EC2進行：
- **資料庫MySQL性能測試** - 使用sysbench
- **框架性能測試** - 使用k6

## 🖥️ 測試環境

### EC2實例配置
- **實例型號：** c6g.xlarge (4C8G ARM Graviton2)
- **實例數量：** 3台
- **實例名稱：** bench-1, bench-2, test
- **作業系統：** Amazon Linux 2023-6.1
- **費用：** 0.0852 USD/hour

詳細規格請參考：[ec2-specs.md](./ec2-specs.md)

## 📋 測試模組概覽

### 1. MySQL + sysbench 測試
- **狀態：** 計劃完成
- **位置：** `mysql-sysbench/`
- **測試內容：** 三層次性能測試 (CPU/記憶體/磁碟)
- **實例分配：**
  - bench-1: 三個MySQL 5.6容器
  - test: sysbench測試容器
- **測試時間：** 約2小時

### 2. k6 框架測試
- **狀態：** 待規劃
- **位置：** `k6-framework/`
- **測試內容：** 待討論

### 3. 系統監控
- **狀態：** 待規劃
- **位置：** `monitoring/`
- **監控內容：** 待討論

## 📁 專案檔案結構

```
cloud-server-benchmark/
├── docs/                           # 文件資料夾
│   ├── project-overview.md         # 專案概覽 (本文件)
│   ├── ec2-specs.md                # EC2規格文件
│   ├── mysql-sysbench-test-plan.md # MySQL測試計劃
│   ├── k6-framework-test-plan.md   # k6框架測試計劃
│   └── monitoring-plan.md          # 系統監控計劃
├── mysql-sysbench/                 # MySQL測試專用資料夾
│   ├── docker/
│   │   ├── bench-1/
│   │   │   ├── docker-compose.yml  # 三個MySQL容器配置
│   │   │   └── mysql-config/       # 各容器的my.cnf配置
│   │   └── test/
│   │       └── docker-compose.yml  # sysbench容器配置
│   ├── scripts/
│   │   └── three-tier-test.sh      # MySQL三層次測試腳本
│   └── results/                    # MySQL測試結果目錄
├── k6-framework/                   # 框架性能測試
│   ├── scripts/
│   └── results/
└── monitoring/                     # 系統監控相關
    ├── scripts/
    └── dashboards/
```

## 💰 成本估算

### MySQL測試
- **3台EC2實例：** 0.2556 USD/hour
- **測試時間：** 2小時
- **預估成本：** ~0.51 USD

---

**建立日期：** 2025-09-27
**最後更新：** 2025-09-27