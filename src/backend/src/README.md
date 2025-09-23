# 程式碼架構說明

## 📁 程式碼結構

```
src/
├── main/java/
│   ├── Application.java              # Spring Boot啟動類
│   ├── shared/                       # 共用組件
│   │   ├── dto/
│   │   │   └── ApiResponse.java      # 統一API回應格式
│   │   ├── exception/
│   │   │   ├── BusinessException.java      # 業務異常
│   │   │   └── GlobalExceptionHandler.java # 全域異常處理
│   │   ├── controller/
│   │   │   └── RootController.java    # 根路徑控制器（系統端點）
│   │   ├── config/                   # 配置類目錄
│   │   └── util/                     # 工具類目錄
│   └── [moduleA]/                    # 功能模組A（待設計文件）
│       ├── controller/               # API控制器層
│       ├── service/                  # 業務邏輯層  
│       ├── repository/               # 資料存取層
│       ├── entity/                   # 實體模型
│       └── dto/                      # 資料傳輸物件
│           ├── request/              # 請求物件
│           └── response/             # 回應物件
├── main/resources/
│   ├── application.yml               # 主配置檔案
│   ├── application-dev.yml           # 開發環境配置
│   ├── application-test.yml          # 測試環境配置
│   └── application-prod.yml          # 生產環境配置
├── test/java/
│   └── shared/
│       └── RootControllerTest.java    # 根路徑控制器測試
└── test/resources/
    ├── schema.sql                    # 測試資料表結構
    └── test-data/
        └── cleanup.sql               # 測試資料清理
```

## 🏗 架構設計原則

### 功能導向分層架構
每個業務功能模組包含完整的三層架構：
- **Controller層** - 處理HTTP請求，僅使用GET和POST方法
- **Service層** - 實現業務邏輯，包含所有驗證規則
- **Repository層** - 資料存取，使用Spring Data JPA

### 共用組件說明

#### ApiResponse<T>
```java
// 統一的API回應格式
ApiResponse.success(data)                    // 成功回應
ApiResponse.success(data, "操作成功")         // 成功回應附訊息
ApiResponse.error("ERROR_CODE", "錯誤訊息")   // 錯誤回應
```

#### BusinessException
```java
// 業務異常，所有業務錯誤都使用此異常
throw new BusinessException("VALIDATION_FAILED", "參數驗證失敗");
```

#### GlobalExceptionHandler
- 自動攔截所有異常
- 統一回傳HTTP 200狀態碼
- 按照設計文件格式化錯誤回應

## 📋 新增功能模組步驟

### 1. 建立模組目錄結構
```bash
mkdir -p src/main/java/[模組名]/controller
mkdir -p src/main/java/[模組名]/service  
mkdir -p src/main/java/[模組名]/repository
mkdir -p src/main/java/[模組名]/entity
mkdir -p src/main/java/[模組名]/dto/request
mkdir -p src/main/java/[模組名]/dto/response
```

### 2. 實現各層組件

#### Controller範例
```java
@RestController
@RequestMapping("/api/[模組名]")
@RequiredArgsConstructor
@Slf4j
public class [模組名]Controller {
    
    private final [模組名]Service service;
    
    @PostMapping("/create") // @Spec: api-design.md:xx
    public ResponseEntity<ApiResponse<[Entity]>> create(@RequestBody @Valid CreateRequest request) {
        [Entity] result = service.create(request);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
}
```

#### Service範例
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class [模組名]Service {
    
    private final [模組名]Repository repository;
    
    public [Entity] create(CreateRequest request) {
        log.info("創建{}開始: {}", "[功能名]", request.getName()); // @Spec: user-flow.md:xx
        
        // 業務邏輯實現 @Spec: user-flow.md:xx
        [Entity] entity = [Entity].builder()
            .name(request.getName()) // @Spec: model-validation.md:xx
            .build();
            
        [Entity] saved = repository.save(entity);
        log.info("創建{}成功: id={}", "[功能名]", saved.getId());
        
        return saved;
    }
}
```

#### Entity範例
```java
@Entity
@Table(name = "[table_name]") // @Spec: database-design.md:xx
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class [Entity] {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id; // @Spec: model-validation.md:xx
    
    @Column(nullable = false)
    @NotBlank(message = "名稱不能為空") // @Spec: model-validation.md:xx
    @Size(min = 1, max = 100) // @Spec: model-validation.md:xx
    private String name;
}
```

### 3. 建立測試類別

#### 整合測試範例
```java
@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:application-test.yml")
@Sql(scripts = "/test-data/cleanup.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
class [模組名]ControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void create_shouldReturnSuccess() throws Exception {
        // @Spec: api-design.md:xx - API測試案例
        mockMvc.perform(post("/api/[模組名]/create")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"測試名稱\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.name").value("測試名稱"));
    }
}
```

## ⚠️ 重要約束

### @Spec標註要求
所有關鍵實現都必須標註對應的設計文件來源：
```java
// @Spec: [文件名稱]:[行號] - [具體內容描述]
private String name; // @Spec: model-validation.md:24-26 - 名稱欄位定義與驗證規則
```

### HTTP方法限制
- **GET** - 僅用於查詢操作
- **POST** - 用於所有變更操作
- **禁用** - PUT、DELETE、PATCH等REST方法

### 異常處理約束
- 所有異常都使用BusinessException
- HTTP狀態碼統一為200
- 錯誤訊息使用設計文件中的精確用詞

### 測試要求
- 整體覆蓋率≥80%，業務邏輯≥90%
- 規範驗證驅動測試
- 測試案例要對應設計文件規範

---

**注意：** 實際的功能模組應該根據收到的設計文件進行建立，上述範例僅供架構參考。