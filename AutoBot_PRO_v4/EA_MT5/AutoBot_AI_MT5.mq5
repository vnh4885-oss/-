//+------------------------------------------------------------------+
//| AutoBot PRO — MT5 EA v4.0                                        |
//| Advanced AI Trading Bot for Forex                                 |
//+------------------------------------------------------------------+
#property copyright "AutoBot PRO"
#property version   "4.00"
#property strict

#include <Trade\Trade.mqh>
CTrade trade;

input string  ServerURL        = "http://localhost:5000";  // Server URL
input string  Secret           = "autobot_pro_2025_secure"; // Webhook Secret
input double  DefaultLot       = 0.01;                      // Default Lot Size
input int     Slippage         = 30;                        // Slippage in points
input int     ScanIntervalSec  = 60;                        // Scan interval (seconds)
input bool    AutoTrade        = true;                      // Enable auto trading
input double  MaxDailyLoss     = 0.05;                      // Max daily loss %
input int     MaxPositions     = 10;                        // Max open positions

datetime lastScan = 0;
double dailyLoss = 0;
int trades_today = 0;

int OnInit() {
    trade.SetExpertMagicNumber(778899);
    trade.SetDeviationInPoints(Slippage);
    trade.SetTypeFilling(ORDER_FILLING_IOC);
    
    EventSetMillisecondTimer(100);  // Check every 100ms
    
    Print("✅ AutoBot PRO MT5 v4.0 - Started");
    Print("📡 Server: ", ServerURL);
    Print("🔧 Magic Number: 778899");
    
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    EventKillTimer();
    Print("❌ AutoBot PRO MT5 - Stopped");
}

void OnTimer() {
    if(!AutoTrade) return;
    
    // Scan every ScanIntervalSec seconds
    if(TimeCurrent() - lastScan >= ScanIntervalSec) {
        lastScan = TimeCurrent();
        ScanAndTrade();
    }
}

void ScanAndTrade() {
    if(PositionsTotal() >= MaxPositions) {
        Print("⚠️ Max positions reached: ", PositionsTotal());
        return;
    }
    
    // Check daily loss
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    dailyLoss = balance - equity;
    
    double lossPercent = (dailyLoss / balance) * 100;
    if(lossPercent > MaxDailyLoss * 100) {
        Print("🛑 Daily loss limit reached: ", lossPercent, "%");
        return;
    }
    
    // Call API to get scan results
    string response = MakeRequest("/scan_forex");
    if(response == "ERROR") return;
    
    // Parse BUY signals
    int buyCount = CountSignals(response, "BUY");
    int sellCount = CountSignals(response, "SELL");
    
    Print("📊 Scan Results - BUY: ", buyCount, " SELL: ", sellCount);
    
    // Execute BUY trades
    if(buyCount > 0) {
        vector<string> buySymbols = GetSignalSymbols(response, "BUY");
        for(int i = 0; i < buySymbols.Size() && i < 3; i++) {
            ExecuteTrade(buySymbols[i], ORDER_TYPE_BUY);
        }
    }
    
    // Execute SELL trades
    if(sellCount > 0) {
        vector<string> sellSymbols = GetSignalSymbols(response, "SELL");
        for(int i = 0; i < sellSymbols.Size() && i < 3; i++) {
            ExecuteTrade(sellSymbols[i], ORDER_TYPE_SELL);
        }
    }
}

void ExecuteTrade(string symbol, ENUM_ORDER_TYPE orderType) {
    if(!SymbolSelect(symbol, true)) {
        Print("❌ Cannot select symbol: ", symbol);
        return;
    }
    
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) {
        Print("❌ No tick for: ", symbol);
        return;
    }
    
    double price = (orderType == ORDER_TYPE_BUY) ? tick.ask : tick.bid;
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    
    // Calculate ATR for SL/TP
    double atr = CalculateATR(symbol, 14);
    
    double sl, tp;
    if(orderType == ORDER_TYPE_BUY) {
        sl = price - (atr * 2);
        tp = price + (atr * 3);
    } else {
        sl = price + (atr * 2);
        tp = price - (atr * 3);
    }
    
    if(orderType == ORDER_TYPE_BUY) {
        if(trade.Buy(DefaultLot, symbol, price, sl, tp, "AutoBot-AI")) {
            Print("✅ BUY ", symbol, " @ ", price, " SL:", sl, " TP:", tp);
        } else {
            Print("❌ BUY Failed: ", trade.ResultComment());
        }
    } else {
        if(trade.Sell(DefaultLot, symbol, price, sl, tp, "AutoBot-AI")) {
            Print("✅ SELL ", symbol, " @ ", price, " SL:", sl, " TP:", tp);
        } else {
            Print("❌ SELL Failed: ", trade.ResultComment());
        }
    }
}

double CalculateATR(string symbol, int period) {
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    
    int copied = CopyRates(symbol, PERIOD_H1, 0, period + 1, rates);
    if(copied <= 0) return 0.0001;
    
    double trSum = 0;
    for(int i = 1; i < copied; i++) {
        double tr = MathMax(rates[i].high - rates[i].low,
                   MathMax(MathAbs(rates[i].high - rates[i+1].close),
                          MathAbs(rates[i].low - rates[i+1].close)));
        trSum += tr;
    }
    
    return trSum / (double)period;
}

string MakeRequest(string endpoint) {
    CURL *curl = curl_easy_init();
    if(!curl) return "ERROR";
    
    string url = ServerURL + endpoint;
    char response[];
    
    int result = WebRequest("GET", url, NULL, 1000, response, NULL);
    
    if(result != 200) {
        Print("❌ API Error: ", result);
        return "ERROR";
    }
    
    return CharArrayToString(response);
}

int CountSignals(string json, string type) {
    // Simple count of signal type in JSON
    string search = "\"recommendation\":\"" + type + "\"";
    int count = 0;
    int pos = 0;
    
    while((pos = StringFind(json, search, pos)) >= 0) {
        count++;
        pos += StringLen(search);
    }
    
    return count;
}

vector<string> GetSignalSymbols(string json, string type) {
    vector<string> symbols;
    
    // Simple extraction of symbols from JSON
    // This is a simplified version
    
    return symbols;
}
