# 食物項目API介面規格

## API端點

### 查詢食物項目
- **方法**: `GET`
- **路徑**: `/api/food-items`
- **描述**: 分頁查詢食物項目，支援條件篩選和關鍵字搜尋

## 請求參數

### Query Parameters
| 參數名稱 | 型別 | 必填 | 預設值 | 說明 |
|---------|------|-----|--------|------|
| `page` | Integer | 否 | 1 | 頁碼（1-based） |
| `pageSize` | Integer | 否 | 20 | 每頁數量（1-100） |
| `ratingSentiment` | String | 否 | - | 評價情感篩選：positive/negative/neutral |
| `dataCompleteness` | String | 否 | - | 資料完整度篩選：complete/partial/minimal |
| `dishName` | String | 否 | - | 料理名稱關鍵字搜尋 |
| `vendorName` | String | 否 | - | 店家名稱關鍵字搜尋 |

### 請求範例
```
GET /api/food-items?page=1&pageSize=10&ratingSentiment=positive&dishName=臭豆腐
```

## 回應格式

### 成功回應結構
```json
{
  "success": true,
  "code": "1000",
  "message": "成功",
  "data": {
    "content": [
      {
        "dishName": "臭豆腐",
        "vendorName": "326臭臭鍋",
        "description": "香辣好吃的臭豆腐",
        "price": "60元",
        "ratingSentiment": "positive",
        "dataCompleteness": "complete"
      }
    ],
    "page": 1,
    "pageSize": 10,
    "totalElements": 50,
    "totalPages": 5,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

### 資料項目結構
| 欄位名稱 | 型別 | 說明 |
|---------|------|------|
| `dishName` | String | 料理名稱 |
| `vendorName` | String | 店家攤位名稱 |
| `description` | String | 口味食材體驗描述 |
| `price` | String | 價格資訊 |
| `ratingSentiment` | String | 評價情感傾向（positive/negative/neutral） |
| `dataCompleteness` | String | 資料完整度（complete/partial/minimal） |

### 分頁資訊結構
| 欄位名稱 | 型別 | 說明 |
|---------|------|------|
| `content` | Array | 當前頁資料陣列 |
| `page` | Integer | 當前頁碼（1-based） |
| `pageSize` | Integer | 每頁數量 |
| `totalElements` | Long | 總資料筆數 |
| `totalPages` | Integer | 總頁數 |
| `hasNext` | Boolean | 是否有下一頁 |
| `hasPrevious` | Boolean | 是否有上一頁 |

## 錯誤回應

### 錯誤格式
```json
{
  "success": false,
  "code": "1001",
  "message": "錯誤描述",
  "data": null
}
```

### 錯誤碼定義
| 錯誤碼 | HTTP狀態 | 說明 |
|-------|----------|------|
| `1001` | 200 | 參數驗證失敗（包含分頁參數超出範圍、篩選條件值無效等） |
| `1002` | 200 | 資料庫查詢失敗 |
| `1003` | 200 | 系統內部錯誤 |

### 錯誤回應範例
```json
{
  "success": false,
  "code": "1001",
  "message": "分頁大小必須在1-100之間",
  "data": null
}
```

## HTTP狀態碼
- **200 OK**: 所有回應（包含錯誤）統一使用200狀態碼
- 業務狀態透過回應body中的`success`和`code`欄位判斷

## 注意事項
1. 所有時間格式使用ISO 8601標準
2. 關鍵字搜尋使用模糊匹配（LIKE %keyword%）
3. 篩選條件支援單選，不支援多選（例如：ratingSentiment只能選擇positive或negative或neutral其中一個，不能同時選擇多個）
4. 分頁從1開始計算
5. 空值欄位在JSON回應中會顯示為null