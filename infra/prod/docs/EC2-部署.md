# AWS EC2 部署流程

## AWS Web UI 建立 EC2 實例

### 1. 登入 AWS 控制台
- 進入 AWS Management Console
- 切換到 **亞太 (孟買) ap-south-1** 區域
- 原因：比台北/東京便宜約一半成本

### 2. 啟動 EC2 實例
1. **EC2 Dashboard** → **啟動執行個體**

2. **選擇 AMI**
   - **Amazon Linux 2023** (隨需)
   - 預設使用者：`ec2-user`

3. **實例類型**
   - **t4g.medium (2 vCPU, 4 GiB 記憶體)**
   - ⚠️ **重要**：必須選 4GB 記憶體，2GB 實例裝 VS Code SSH Server 會 OOM 崩潰

4. **金鑰對設定**
   - 建立新金鑰對：`manager-key`
   - 下載 `manager-key.pem` 並妥善保存

5. **網路設定**
   - 建立新的安全群組
   - 規則：SSH (22) - 來源：我的 IP

6. **設定儲存**
   - **16 GiB** gp3 儲存

7. **啟動實例**

### 3. 取得連線資訊
- **公有 IPv4 DNS**：`ec2-xxx-xxx-xxx-xxx.ap-south-1.compute.amazonaws.com`
- **公有 IPv4 位址**：`xxx.xxx.xxx.xxx`

## VS Code SSH 設定

### 1. 金鑰檔案處理
```bash
# 將下載的金鑰移至 SSH 目錄
move manager-key.pem %USERPROFILE%\.ssh\
```

### 2. SSH Config 設定
**位置**：`%USERPROFILE%\.ssh\config` (Windows)

**設定內容**：
```
Host manager-ec2
    HostName ec2-xxx-xxx-xxx-xxx.ap-south-1.compute.amazonaws.com
    User ec2-user
    Port 22
    IdentityFile ~/.ssh/manager-key.pem
```

### 3. VS Code Remote-SSH 擴展
1. **安裝擴展**：Remote - SSH
2. **連線步驟**：
   - `Ctrl+Shift+P` → `Remote-SSH: Connect to Host...`
   - 選擇 `manager-ec2`
   - 在新視窗開啟遠程服務器

### 4. 驗證連線
```bash
# SSH 指令驗證 (可選)
ssh -i ~/.ssh/manager-key.pem ec2-user@<EC2-Public-DNS>
```

## Docker 環境安裝

連線成功後，在遠程終端執行：

```bash
# 更新系統
sudo yum update -y

# 安裝 Docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登入使群組生效
exit
```

## 記憶體規格說明

**為什麼選 4GB 記憶體？**
- VS Code SSH Server 需要額外記憶體
- 2GB 實例 (t4g.small) 會因記憶體不足而 OOM 崩潰
- t4g.medium (4GB) 是穩定運行的最小規格

---

**區域**: ap-south-1 (孟買)
**實例**: t4g.medium (2C4G)
**成本優勢**: 比東京/台北便宜約 50%