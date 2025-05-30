# 自動交易系統

一個集成富途OpenD API和TradingView警報的自動化交易系統。

## 概述

該項目提供了一個自動化交易解決方案，連接TradingView警報與富途交易平台，實現交易策略的自動執行。

## 前提條件

- [富途OpenD](https://openapi.futunn.com/futu-api-doc/opend/opend-cmd.html)
- Python 3.6+
- Node.js
- Node-RED

## 安裝

### 1. 安裝富途OpenD

按照[富途OpenD文檔](https://openapi.futunn.com/futu-api-doc/opend/opend-cmd.html)中的安裝步驟進行操作。

### 2. 配置富途OpenD

安裝後，導航到安裝目錄並編輯`FutuOpenD.xml`文件：

```xml
<futu_opend>
    <!-- Basic parameters -->
    <!-- Listening address. 127.0.0.1 by default -->
    <ip>127.0.0.1</ip>
    <!-- API interface protocol listening port -->
    <api_port>11111</api_port>
    <!-- Login account -->
    <login_account>{{ Your Futu ID }}</login_account>
    <!-- Login password, 32-bit MD5 encrypted hexadecimal --> 
    <!-- <login_pwd_md5>6e55f158a827b1a1c4321a245aaaad88</login_pwd_md5> -->
    <!-- Plain text of login password. When cypher text exists, the cypher text will be used. --> 
    <login_pwd>{{ Your Password }}</login_pwd>
    <!-- FutuOpenD language. en: English, chs: Simplified Chinese -->
    <lang>en</lang> <!-- Use English to avoid encoding issues -->
   <!-- Rest with no changes -->
```

只更改`{{ }}`內的部分。

### 3. 安裝Python

按照[富途API Python環境設置](https://openapi.futunn.com/futu-api-doc/quick/env.html)中的步驟操作：

1. 啟動Python安裝程序，勾選"Add python.exe to PATH"複選框
2. 保持安裝過程中的默認選項
3. 安裝完成後，打開命令提示符並運行：
   - Windows: `python -V`
   - Linux & Mac: `python3 -V`
   - 同時檢查pip: `pip --version`

### 4. 安裝所需的Python庫

```bash
pip install futu-api flask
```

### 5. 安裝Node.js

1. 從[nodejs.org](https://nodejs.org/en)下載Node.js
2. 按照所有默認安裝步驟進行操作
3. 安裝完成後，打開命令提示符並驗證安裝：
   ```bash
   node -v
   npm -v
   ```

### 6. 安裝Node-RED

1. 全局安裝Node-RED：
   ```bash
   # Windows（以管理員身份運行）
   npm install -g --unsafe-perm node-red
   
   # Linux/Mac
   sudo npm install -g --unsafe-perm node-red
   ```
2. 驗證安裝：
   ```bash
   node-red --help
   ```

## 啟動程序

1. 運行`FutuOpenD.exe`啟動OpenD服務器
2. 解壓auto-trade項目（如果尚未解壓）
3. 配置交易環境：

在啟動前，編輯futu/config.py設置：

```python
# 交易密碼（實盤交易必需）
FUTU_TRADE_PWD = "你的交易密碼"

# 交易環境（選擇一個）
FUTU_ENV = TrdEnv.SIMULATE  # 模擬交易環境
# FUTU_ENV = TrdEnv.REAL     # 實盤交易環境
將FUTU_TRADE_PWD設置為你的實際交易密碼

選擇TrdEnv.SIMULATE（模擬交易）或TrdEnv.REAL（實盤交易）
```

4. 運行`startup.bat`啟動Python和Node-RED服務器
5. 訪問[http://localhost:5001](http://localhost:5001)進入Node-RED
   - 你可以通過修改Node-RED中的流連接來自定義你想接收的警報

## 重要配置說明
__FUTU_TRADE_PWD__：這與你的登錄密碼不同。它是你在富途應用中確認交易時使用的密碼。

交易環境：

__TrdEnv.SIMULATE__：所有訂單都是模擬的（不涉及真實資金）

__TrdEnv.REAL__：訂單將使用真實資金執行

在切換到實盤交易前，始終在模擬模式下測試你的策略。

## TradingView集成

配置TradingView警報以發送webhook到你的服務器端點。警報格式應與你的Node-RED流程所期望的格式匹配。

## 配置

你可以修改`futu/config.py`文件中的配置設置來調整交易參數。

### 配置參數詳解

以下是配置檔案中各參數的詳細說明：

- **FUTU_OPEN_D_HOST** = '127.0.0.1'  
  富途OpenD服務器的主機地址。默認為本地地址，如果OpenD運行在其他機器上，需要修改為對應IP。

- **FUTU_OPEN_D_PORT** = 11111  
  富途OpenD服務器的連接埠。需要與FutuOpenD.xml中設置的api_port一致。

- **FUTU_TRADE_PWD** = '你的交易密碼'  
  交易密碼，用於執行實盤交易時的驗證。這是你在富途APP中確認交易時使用的密碼，而非登錄密碼。

- **FUTU_ENV** = TrdEnv.REAL / TrdEnv.SIMULATE  
  交易環境設置。TrdEnv.SIMULATE為模擬交易環境（不使用真實資金），TrdEnv.REAL為實盤交易環境（使用真實資金）。

- **DEFAULT_TRADING_CURRENCY** = "USD"  
  默認交易貨幣。可設置為"USD"（美元）、"HKD"（港幣）等，取決於你交易的市場。

- **SHARES_ORDER_PERCENTAGE_PER_STOCK** = 0.25  
  每筆股票訂單的資金比例。例如，設置為0.25表示每筆訂單將使用賬戶可用資金的25%。

- **OPTION_MAX_PER_TYPE** = 3  
  每種期權類型（看漲/看跌）的最大數量限制。系統會根據目標價格選擇最接近的期權。

- **OPTION_CALL_INDEX** = 2  
  看漲期權的選擇索引。較小的值會選擇更接近目標價格的期權，較大的值會選擇更遠的期權 (0為最小, **OPTION_MAX_PER_TYPE**-1為最大)。

- **OPTION_PUT_INDEX** = 2  
  看跌期權的選擇索引。較小的值會選擇更接近目標價格的期權，較大的值會選擇更遠的期權 (0為最小, **OPTION_MAX_PER_TYPE**-1為最大)。

- **OPTION_QTY_PER_ORDER** = 1  
  每筆期權訂單的合約數量。

- **ALLOW_MULTIPLE_ORDER_PER_DIRECTION** = False  
  是否允許在同一方向（買入/賣出）下多個訂單。設置為False時，系統會檢查是否已有相同方向的未完成訂單。

- **API_QUEUE_DELAY** = 2  
  API請求隊列的延遲時間（秒）。

### 建議配置

初次使用時，建議保持以下設置：
1. 將FUTU_ENV設置為TrdEnv.SIMULATE進行模擬交易測試
2. 保持較低的SHARES_ORDER_PERCENTAGE_PER_STOCK值（如0.1）以限制每筆訂單的資金使用
3. 設置ALLOW_MULTIPLE_ORDER_PER_DIRECTION = False以避免重複下單

在確認系統正常運行並熟悉操作後，再根據需要調整這些參數。

## 問答

如有任何問題，請聯繫開發者。

## 許可

該項目為專有軟件。