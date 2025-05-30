# Auto-Trade

An automated trading system that integrates with Futu OpenD API and TradingView alerts.

## Overview

This project provides an automated trading solution that connects TradingView alerts with Futu trading platform, allowing for automated execution of trading strategies.

## Prerequisites

- [Futu OpenD](https://openapi.futunn.com/futu-api-doc/opend/opend-cmd.html)
- Python 3.6+
- Node.js
- Node-RED

## Installation

### 1. Install Futu OpenD

Follow the installation steps in [Futu OpenD documentation](https://openapi.futunn.com/futu-api-doc/opend/opend-cmd.html).

### 2. Configure Futu OpenD

After installation, navigate to the installation directory and edit the `FutuOpenD.xml` file:

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
```

Only change the parts within `{{ }}`.

### 3. Install Python

Follow the steps in [Futu API Python Environment Setup](https://openapi.futunn.com/futu-api-doc/quick/env.html):

1. Start the Python installer, and tick the "Add python.exe to PATH" checkbox
2. Keep the default options for the rest of the installation
3. After installation, open a command prompt and run:
   - Windows: `python -V`
   - Linux & Mac: `python3 -V`
   - Also check pip with: `pip --version`

### 4. Install Required Python Libraries

```bash
pip install futu-api flask
```

### 5. Install Node.js

1. Download Node.js from [nodejs.org](https://nodejs.org/en)
2. Follow all default installation steps
3. After installation, open a command prompt and verify installation with:
   ```bash
   node -v
   npm -v
   ```

### 6. Install Node-RED

1. Install Node-RED globally:
   ```bash
   # For Windows (run as Administrator)
   npm install -g --unsafe-perm node-red
   
   # For Linux/Mac
   sudo npm install -g --unsafe-perm node-red
   ```
2. Verify installation with:
   ```bash
   node-red --help
   ```

## Starting the Program

1. Launch Futu OpenD by running `FutuOpenD.exe` to start the OpenD server
2. Unzip the auto-trade project (if not already done)
3. Configure Trading Environment:

Before starting, edit futu/config.py to set:

```python
# Trading password (required for real market orders)
FUTU_TRADE_PWD = "your_trading_password"

# Trading environment (choose one)
FUTU_ENV = TrdEnv.SIMULATE  # Paper trading environment
# FUTU_ENV = TrdEnv.REAL     # Real trading environment
Set FUTU_TRADE_PWD to your actual trading password

Choose between TrdEnv.SIMULATE (paper trading) or TrdEnv.REAL (live trading)
```

4. Run `startup.bat` to start the Python and Node-RED servers
5. Access Node-RED at [http://localhost:5001](http://localhost:5001)
   - You can customize your alerts by modifying the flow connections in Node-RED

## Important Configuration Notes
__FUTU_TRADE_PWD__: This is different from your login password. It's the password you use to confirm trades in the Futu app.

Trading Environment:

__TrdEnv.SIMULATE__: All orders are simulated (no real money involved)

__TrdEnv.REAL__: Orders will be executed with real money

Always test your strategies in simulation mode before switching to real trading.

## TradingView Integration

Configure TradingView alerts to send webhooks to your server endpoint. The format of the alert should match what your Node-RED flow expects.

## Configuration

You can modify the configuration settings in the `futu/config.py` file to adjust trading parameters.

## Q&A

If you have any questions, please contact the developer.

## License

This project is proprietary software.