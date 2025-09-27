# 資料分析目錄重構計劃

## 目前結構問題分析

### 現有結構
```
src/data-analysis/
├── config.py                 # 配置檔案
├── database_connector.py     # 資料庫連接
├── core_dataset_builder.py   # 核心資料集建立器
├── opportunity_analyzer.py   # 商機分析器
├── visualizer.py             # 視覺化模組
├── main.py                   # 主程式
└── output/                   # 輸出目錄
```

### 存在的問題
1. **平鋪結構**：所有 6 個模組都在同一層級
2. **職責混合**：不同層級的功能混在一起（配置、資料層、業務層、展示層）
3. **檔案過大**：部分模組行數較多（`visualizer.py` 413行、`opportunity_analyzer.py` 397行）
4. **缺乏模組化**：相關功能沒有適當分組
5. **不利於擴展**：新功能難以找到合適的放置位置

## 新架構設計

### 分層架構
```
src/data-analysis/
├── config/                    # 配置層
│   ├── __init__.py
│   ├── database.py           # 資料庫配置
│   ├── analysis.py           # 分析參數配置
│   └── visualization.py      # 視覺化配置
├── data/                     # 資料層
│   ├── __init__.py
│   ├── connectors/
│   │   ├── __init__.py
│   │   └── database_connector.py
│   └── builders/
│       ├── __init__.py
│       └── dataset_builder.py
├── analysis/                 # 分析層
│   ├── __init__.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base_analyzer.py
│   │   ├── opportunity_analyzer.py
│   │   └── business_analyzer.py
│   └── metrics/
│       ├── __init__.py
│       └── scoring.py
├── visualization/            # 視覺化層
│   ├── __init__.py
│   ├── charts/
│   │   ├── __init__.py
│   │   ├── base_chart.py
│   │   ├── ranking_charts.py
│   │   ├── matrix_charts.py
│   │   └── distribution_charts.py
│   └── renderers/
│       ├── __init__.py
│       └── chart_renderer.py
├── orchestration/           # 編排層
│   ├── __init__.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── analysis_workflow.py
│   └── reports/
│       ├── __init__.py
│       └── report_generator.py
├── utils/                   # 工具層
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
├── main.py                  # 入口點（簡化後）
└── output/                  # 輸出目錄（保持不變）
```

### 層級職責說明

#### 1. 配置層 (config/)
- **database.py**: 資料庫連接相關配置
- **analysis.py**: 分析參數和閾值配置
- **visualization.py**: 圖表樣式和輸出配置

#### 2. 資料層 (data/)
- **connectors/**: 資料來源連接器
  - `database_connector.py`: MySQL 資料庫連接管理
- **builders/**: 資料集建立器
  - `dataset_builder.py`: 核心資料集建立邏輯

#### 3. 分析層 (analysis/)
- **analyzers/**: 各種分析器
  - `base_analyzer.py`: 基礎分析器抽象類別
  - `opportunity_analyzer.py`: 商機分析專用
  - `business_analyzer.py`: 商業標的統一分析
- **metrics/**: 評分和指標計算
  - `scoring.py`: 商機評分算法

#### 4. 視覺化層 (visualization/)
- **charts/**: 圖表生成器
  - `base_chart.py`: 基礎圖表類別
  - `ranking_charts.py`: 排行榜圖表
  - `matrix_charts.py`: 矩陣圖表
  - `distribution_charts.py`: 分布圖表
- **renderers/**: 渲染器
  - `chart_renderer.py`: 圖表渲染和儲存

#### 5. 編排層 (orchestration/)
- **workflows/**: 工作流程
  - `analysis_workflow.py`: 分析流程編排
- **reports/**: 報告生成
  - `report_generator.py`: 摘要報告生成

#### 6. 工具層 (utils/)
- **validators.py**: 資料驗證工具
- **helpers.py**: 共用輔助函數

## 重構步驟

### 階段 1: 準備工作
1. **創建目錄結構**
   ```bash
   mkdir -p config data/connectors data/builders analysis/analyzers analysis/metrics
   mkdir -p visualization/charts visualization/renderers orchestration/workflows orchestration/reports utils
   ```

2. **創建 __init__.py 檔案**
   - 在每個目錄中建立適當的 `__init__.py`
   - 設定模組匯入路徑

### 階段 2: 配置層重構
1. **拆分 config.py**
   ```python
   # config/database.py
   DATABASE_CONFIG = {...}

   # config/analysis.py
   ANALYSIS_CONFIG = {...}

   # config/visualization.py
   CHART_CONFIG = {...}
   ```

### 階段 3: 資料層重構
1. **移動資料庫連接器**
   - `database_connector.py` → `data/connectors/database_connector.py`

2. **重構資料集建立器**
   - `core_dataset_builder.py` → `data/builders/dataset_builder.py`
   - 重新命名類別為 `DatasetBuilder`

### 階段 4: 分析層重構
1. **創建基礎分析器**
   ```python
   # analysis/analyzers/base_analyzer.py
   class BaseAnalyzer:
       def __init__(self, dataset):
           self.dataset = dataset

       def validate_data(self):
           pass

       def generate_stats(self):
           pass
   ```

2. **重構商機分析器**
   - 將大型 `opportunity_analyzer.py` 拆分
   - 提取共用邏輯到基礎類別

### 階段 5: 視覺化層重構
1. **拆分視覺化器**
   ```python
   # visualization/charts/base_chart.py
   class BaseChart:
       def __init__(self, output_dir):
           self.output_dir = output_dir

       def save_chart(self, filename):
           pass
   ```

2. **專門圖表類別**
   - `ranking_charts.py`: 排行榜圖表
   - `matrix_charts.py`: 散布圖和矩陣圖
   - `distribution_charts.py`: 分布直方圖

### 階段 6: 編排層重構
1. **工作流程編排**
   ```python
   # orchestration/workflows/analysis_workflow.py
   class AnalysisWorkflow:
       def __init__(self):
           self.steps = []

       def run_complete_analysis(self):
           pass
   ```

2. **簡化主程式**
   - `main.py` 只保留入口邏輯
   - 主要業務邏輯移到工作流程

### 階段 7: 測試和驗證
1. **更新匯入路徑**
2. **執行功能測試**
3. **驗證輸出一致性**
4. **效能測試**

## 重構效益

### 1. 架構清晰度
- **分層明確**: 每層專注特定職責
- **職責分離**: 配置、資料、分析、視覺化各司其職
- **依賴關係清楚**: 上層依賴下層，避免循環依賴

### 2. 可維護性提升
- **小模組**: 每個檔案職責單一，容易理解
- **低耦合**: 模組間依賴最小化
- **高內聚**: 相關功能組織在一起

### 3. 擴展性增強
- **新功能容易加入**: 每層都有明確的擴展點
- **支援多種資料來源**: 連接器架構易於擴展
- **支援多種分析**: 分析器架構支援新的分析類型

### 4. 重用性提升
- **基礎類別**: 提供共用功能
- **模組化設計**: 組件可獨立使用
- **標準化介面**: 一致的API設計

### 5. 測試性改善
- **單元測試**: 小模組易於測試
- **模擬測試**: 依賴注入支援模擬
- **整合測試**: 分層架構便於整合測試

## 風險評估與對策

### 1. 重構風險
- **功能破壞**: 可能影響現有功能
- **對策**: 階段性重構，每階段都進行完整測試

### 2. 匯入路徑複雜化
- **風險**: 新的目錄結構可能讓匯入變複雜
- **對策**: 在 `__init__.py` 中提供簡化的匯入路徑

### 3. 學習曲線
- **風險**: 團隊需要時間適應新架構
- **對策**: 提供清楚的文件和範例

## 實施時程

### 週 1: 準備階段
- 創建目錄結構
- 建立 `__init__.py` 檔案
- 設定基礎匯入路徑

### 週 2: 配置和資料層
- 重構配置層
- 移動資料層模組
- 測試資料連接功能

### 週 3: 分析層
- 創建基礎分析器
- 重構商機分析器
- 測試分析功能

### 週 4: 視覺化和編排層
- 拆分視覺化模組
- 創建工作流程編排
- 整合測試

### 週 5: 測試和優化
- 完整功能測試
- 效能優化
- 文件更新

## 後續維護建議

1. **編碼規範**: 建立明確的編碼規範
2. **代碼審查**: 確保新代碼符合架構原則
3. **定期重構**: 持續優化和改進
4. **監控效能**: 確保重構不影響效能
5. **文件維護**: 保持文件與代碼同步

---

*本文件記錄了資料分析目錄的完整重構計劃，旨在提升代碼品質和架構清晰度。*