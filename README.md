# 📈 Saham Calculator

Saham Calculator is a professional-grade web application for stock investment analysis and calculation, tailored for the Indonesian market. Built with Streamlit, it provides a comprehensive suite of tools to help investors make data-driven decisions efficiently.

## 🚀 Key Features

### 1. Stock Scraper
- Retrieve real-time stock data from Yahoo Finance
- Display key financial metrics: price, PBV, PER, DER, ROE, and dividend
- Calculate the optimal number of lots based on your available capital

### 2. Stock Transaction Calculator
- Calculate profit/loss for stock trades
- Support for multiple platforms: IPOT, Stockbit, BNI Bions, and custom fee settings
- Automatic calculation of buy/sell fees
- Dividend and dividend yield calculation
- Customizable transaction parameters

### 3. Compound Interest Calculator
- Simulate compound interest growth for investments
- Support for recurring monthly investments
- Detailed results per month and per year

### 4. ARA/ARB Price Calculator
- Calculate ARA (Auto Reject Above) and ARB (Auto Reject Below) price limits
- Support for both main and acceleration boards
- Follows IDX price fraction and board rules

### 5. Warrant Profit Calculator
- Calculate profit/loss from warrant trading
- Support for platform-specific and custom fee structures
- Flexible lot and price input

## 🛠️ Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Yuukinaesa/Saham.git
    cd Saham
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    streamlit run Saham.py
    ```

4. Open your browser and go to `http://localhost:8501`

## 📋 System Requirements

- Python 3.8 or higher
- Streamlit
- Pandas
- yfinance
- scipy

---

### Website: [saham.arfan.biz.id](https://saham.arfan.biz.id)

---