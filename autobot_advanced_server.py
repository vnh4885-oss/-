# ═══════════════════════════════════════════════════════════════════════════
# AutoBot PRO — Advanced AI Trading Engine v4.0
# الذكاء الاصطناعي المتقدم لتداول الفوركس على كل الفريمات
# SMC + Harmonics + Classic Technical Analysis
# ═══════════════════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import json
import time
from collections import deque
import logging

# ── إعداد السجلات ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  الإعدادات الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

CONFIG = {
    'WEBHOOK_SECRET': 'autobot_pro_2025_secure',
    'FOREX_PAIRS': [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD',
        'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY', 'NZDJPY', 'CADJPY',
        'EURCAD', 'GBPCAD', 'AUDCAD', 'NZDCAD', 'EURNZD', 'GBPNZD',
        'AUDNZD', 'EURAUD', 'GBPAUD', 'EURAUD'
    ],
    'US_INDICES': ['XAUUSD', 'DXY', 'VIX'],
    'TIMEFRAMES': [1, 3, 5, 15, 30, 60, 240, 1440],  # M1, M3, M5, M15, M30, H1, H4, D1
    'MAX_POSITIONS': 10,
    'RISK_PER_TRADE': 0.02,  # 2% من الرصيد
    'MAX_DAILY_LOSS': 0.05,  # 5% خسارة يومية قصوى
    'MIN_SPREAD': 0.0,
    'MAX_SPREAD': 50,  # نقاط
    'MIN_EQUITY': 100,  # حد أدنى
}

# ═══════════════════════════════════════════════════════════════════════════
#  التحليل الفني المتقدم — SMC + Harmonics + Classic
# ═══════════════════════════════════════════════════════════════════════════

class TechnicalAnalyzer:
    """محلل فني متقدم - SMC, Harmonics, EMA, RSI, MACD, BB"""
    
    def __init__(self):
        self.cache = {}
    
    # ── المتوسطات المتحركة ──
    @staticmethod
    def ema(data, period=20):
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def sma(data, period=20):
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    # ── القوة النسبية ──
    @staticmethod
    def rsi(data, period=14):
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    # ── MACD ──
    @staticmethod
    def macd(data, fast=12, slow=26, signal=9):
        """MACD Indicator"""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    # ── Bollinger Bands ──
    @staticmethod
    def bollinger_bands(data, period=20, std_dev=2):
        """Bollinger Bands"""
        sma_val = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma_val + (std_dev * std)
        lower = sma_val - (std_dev * std)
        return upper, sma_val, lower
    
    # ── SMC - Smart Money Concepts ──
    @staticmethod
    def find_supply_demand(high, low, close, period=10):
        """
        تحديد مستويات العرض والطلب — SMC
        العرض: قمم مرتفعة متتالية
        الطلب: قيعان منخفضة متتالية
        """
        supply_zones = []
        demand_zones = []
        
        for i in range(period, len(high) - period):
            # تحديد القمم
            if all(high.iloc[i] >= high.iloc[i-j] for j in range(1, period+1)) and \
               all(high.iloc[i] >= high.iloc[i+j] for j in range(1, period+1)):
                supply_zones.append({
                    'price': high.iloc[i],
                    'index': i,
                    'strength': len(supply_zones) % 3 + 1
                })
            
            # تحديد القيعان
            if all(low.iloc[i] <= low.iloc[i-j] for j in range(1, period+1)) and \
               all(low.iloc[i] <= low.iloc[i+j] for j in range(1, period+1)):
                demand_zones.append({
                    'price': low.iloc[i],
                    'index': i,
                    'strength': len(demand_zones) % 3 + 1
                })
        
        return supply_zones, demand_zones
    
    # ── Harmonic Patterns ──
    @staticmethod
    def detect_harmonic_patterns(high, low, close, lookback=100):
        """
        كشف الأنماط التوافقية (Fibonacci Retracement)
        - AB=CD
        - Butterfly
        - Gartley
        """
        patterns = []
        
        if len(close) < lookback:
            return patterns
        
        # Fibonacci Levels
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        
        # بحث بسيط عن الانعكاسات
        for i in range(20, len(close) - 5):
            # قمة متتالية
            if close.iloc[i] > close.iloc[i-1] and close.iloc[i] > close.iloc[i+1]:
                # ابحث عن قاع بعده
                valley_idx = close.iloc[i+1:i+20].idxmin() if i+20 <= len(close) else None
                if valley_idx is not None:
                    valley_price = close.iloc[valley_idx]
                    peak_price = close.iloc[i]
                    retracement = (peak_price - valley_price) / peak_price
                    
                    if any(abs(retracement - fib) < 0.05 for fib in fib_levels):
                        patterns.append({
                            'type': 'Harmonic_Retracement',
                            'level': round(retracement, 3),
                            'index': i,
                            'confidence': 0.7
                        })
        
        return patterns
    
    # ── Trend Analysis ──
    @staticmethod
    def detect_trend(close, period=20):
        """
        كشف الاتجاه
        1 = صاعد، -1 = هابط، 0 = جانبي
        """
        ema_short = close.ewm(span=5).mean()
        ema_long = close.ewm(span=20).mean()
        
        current_price = close.iloc[-1]
        ema_s = ema_short.iloc[-1]
        ema_l = ema_long.iloc[-1]
        
        if ema_s > ema_l and current_price > ema_s:
            return 1, 'BULLISH'
        elif ema_s < ema_l and current_price < ema_s:
            return -1, 'BEARISH'
        else:
            return 0, 'RANGING'
    
    # ── Momentum ──
    @staticmethod
    def momentum(close, period=10):
        """قوة الحركة"""
        return close - close.shift(period)
    
    # ── Volume Analysis (إذا توفرت البيانات) ──
    @staticmethod
    def volume_sma(volume, period=20):
        """متوسط الحجم"""
        return volume.rolling(window=period).mean()

# ═══════════════════════════════════════════════════════════════════════════
#  محرك الذكاء الاصطناعي للتداول
# ═══════════════════════════════════════════════════════════════════════════

class AITradingEngine:
    """محرك التداول الذكي - يجمع كل التحليلات ويتخذ قرارات"""
    
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.signals_cache = deque(maxlen=1000)
        self.last_analysis = {}
    
    def analyze_symbol(self, symbol, bars_dict):
        """
        تحليل شامل لرمز واحد على كل الفريمات
        bars_dict: قاموس يحتوي على بيانات الأسعار لكل فريم زمني
        """
        analysis_result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'signals': [],
            'recommendation': 'HOLD',
            'confidence': 0,
            'reasons': []
        }
        
        # تحليل كل فريم زمني
        timeframe_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        
        for timeframe, bars in bars_dict.items():
            if bars is None or len(bars) < 50:
                continue
            
            try:
                df = pd.DataFrame(bars)
                close = df['close']
                high = df['high']
                low = df['low']
                
                # التحليلات المختلفة
                
                # 1. تحليل الاتجاه
                trend, trend_name = self.analyzer.detect_trend(close)
                
                # 2. RSI
                rsi_val = self.analyzer.rsi(close, 14)
                rsi_last = rsi_val.iloc[-1]
                
                # 3. MACD
                macd_line, signal_line, histogram = self.analyzer.macd(close)
                macd_signal = 'BULL' if histogram.iloc[-1] > 0 else 'BEAR'
                
                # 4. Bollinger Bands
                upper_bb, mid_bb, lower_bb = self.analyzer.bollinger_bands(close, 20, 2)
                bb_signal = 'OVERBOUGHT' if close.iloc[-1] > upper_bb.iloc[-1] else \
                           'OVERSOLD' if close.iloc[-1] < lower_bb.iloc[-1] else 'NEUTRAL'
                
                # 5. SMC - Supply & Demand
                supply, demand = self.analyzer.find_supply_demand(high, low, close, 10)
                
                # 6. Harmonic Patterns
                harmonics = self.analyzer.detect_harmonic_patterns(high, low, close, 100)
                
                # 7. Momentum
                momentum_val = self.analyzer.momentum(close, 10)
                momentum_trend = 'POSITIVE' if momentum_val.iloc[-1] > 0 else 'NEGATIVE'
                
                # ⚙️ منطق التصويت (Voting System)
                frame_signal = self._vote_signal(
                    trend, rsi_last, macd_signal, bb_signal, 
                    momentum_trend, demand, supply
                )
                
                timeframe_votes[frame_signal] += 1
                
                # تخزين التحليل
                analysis_result['signals'].append({
                    'timeframe': f'{timeframe}m',
                    'trend': trend_name,
                    'rsi': round(rsi_last, 2),
                    'macd': macd_signal,
                    'bb_signal': bb_signal,
                    'momentum': momentum_trend,
                    'signal': frame_signal,
                    'confidence': self._calculate_confidence(
                        trend, rsi_last, macd_signal, bb_signal
                    )
                })
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol} on {timeframe}m: {e}")
        
        # تحديد التوصية النهائية
        if timeframe_votes['BUY'] > timeframe_votes['SELL'] and timeframe_votes['BUY'] > 0:
            analysis_result['recommendation'] = 'BUY'
            analysis_result['confidence'] = timeframe_votes['BUY'] / sum(timeframe_votes.values())
            analysis_result['reasons'].append(f"Buy votes: {timeframe_votes['BUY']}")
        elif timeframe_votes['SELL'] > timeframe_votes['BUY'] and timeframe_votes['SELL'] > 0:
            analysis_result['recommendation'] = 'SELL'
            analysis_result['confidence'] = timeframe_votes['SELL'] / sum(timeframe_votes.values())
            analysis_result['reasons'].append(f"Sell votes: {timeframe_votes['SELL']}")
        else:
            analysis_result['recommendation'] = 'HOLD'
            analysis_result['confidence'] = 0
        
        self.last_analysis[symbol] = analysis_result
        return analysis_result
    
    @staticmethod
    def _vote_signal(trend, rsi, macd_sig, bb_sig, momentum, demand, supply):
        """منطق التصويت لتحديد الإشارة"""
        buy_score = 0
        sell_score = 0
        
        # الاتجاه (أهم عامل)
        if trend == 1:  # صاعد
            buy_score += 2
        elif trend == -1:  # هابط
            sell_score += 2
        
        # RSI
        if rsi < 30:
            buy_score += 1
        elif rsi > 70:
            sell_score += 1
        
        # MACD
        if macd_sig == 'BULL':
            buy_score += 1
        else:
            sell_score += 1
        
        # Bollinger Bands
        if bb_sig == 'OVERSOLD':
            buy_score += 1
        elif bb_sig == 'OVERBOUGHT':
            sell_score += 1
        
        # Momentum
        if momentum == 'POSITIVE':
            buy_score += 1
        else:
            sell_score += 1
        
        # SMC - Demand/Supply
        if len(demand) > len(supply):
            buy_score += 1
        elif len(supply) > len(demand):
            sell_score += 1
        
        # التصويت النهائي
        if buy_score > sell_score:
            return 'BUY'
        elif sell_score > buy_score:
            return 'SELL'
        else:
            return 'HOLD'
    
    @staticmethod
    def _calculate_confidence(trend, rsi, macd_sig, bb_sig):
        """حساب مستوى الثقة"""
        confidence = 0.5  # أساس
        
        if trend == 1 and macd_sig == 'BULL':
            confidence += 0.25
        if trend == -1 and macd_sig == 'BEAR':
            confidence += 0.25
        if 30 < rsi < 70:
            confidence += 0.1
        
        return min(confidence, 0.95)

# ═══════════════════════════════════════════════════════════════════════════
#  نظام إدارة المخاطر
# ═══════════════════════════════════════════════════════════════════════════

class RiskManager:
    """إدارة المخاطر والأموال"""
    
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0
        self.daily_trades = 0
        self.session_start = datetime.now()
    
    def calculate_position_size(self, account_balance, entry_price, stop_loss_price):
        """
        حساب حجم اللوت بناءً على المخاطرة المسموحة
        Risk = 2% من الرصيد
        """
        risk_amount = account_balance * self.config['RISK_PER_TRADE']
        price_distance = abs(entry_price - stop_loss_price)
        
        if price_distance == 0:
            return 0.01  # حد أدنى
        
        position_size = risk_amount / price_distance
        return round(position_size, 2)
    
    def can_open_trade(self, account_balance, daily_loss, open_positions):
        """التحقق من إمكانية فتح صفقة جديدة"""
        # تحقق من عدد الصفقات المفتوحة
        if open_positions >= self.config['MAX_POSITIONS']:
            logger.warning(f"Max positions reached: {open_positions}")
            return False, "Max positions exceeded"
        
        # تحقق من الخسارة اليومية
        loss_ratio = daily_loss / account_balance if account_balance > 0 else 0
        if loss_ratio > self.config['MAX_DAILY_LOSS']:
            logger.warning(f"Daily loss limit exceeded: {loss_ratio:.2%}")
            return False, "Daily loss limit exceeded"
        
        return True, "OK"
    
    def calculate_sl_tp(self, entry_price, atr_value, direction='BUY'):
        """
        حساب الـ Stop Loss و Take Profit
        بناءً على ATR (Average True Range)
        """
        if direction == 'BUY':
            stop_loss = entry_price - (atr_value * 2)
            take_profit = entry_price + (atr_value * 3)
        else:  # SELL
            stop_loss = entry_price + (atr_value * 2)
            take_profit = entry_price - (atr_value * 3)
        
        return stop_loss, take_profit

# ═══════════════════════════════════════════════════════════════════════════
#  المسح التلقائي لأزواج الفوركس
# ═══════════════════════════════════════════════════════════════════════════

class ForexScanner:
    """ماسح الفوركس - يفحص كل الأزواج تلقائياً"""
    
    def __init__(self, ai_engine, config):
        self.ai_engine = ai_engine
        self.config = config
        self.scanning = False
    
    def scan_all_symbols(self):
        """فحص جميع أزواج الفوركس والمؤشرات"""
        results = {
            'buy_signals': [],
            'sell_signals': [],
            'hold_signals': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if not self._init_mt5():
            return results
        
        all_symbols = self.config['FOREX_PAIRS'] + self.config['US_INDICES']
        
        for symbol in all_symbols:
            try:
                bars_dict = self._fetch_all_timeframes(symbol)
                if not bars_dict:
                    continue
                
                analysis = self.ai_engine.analyze_symbol(symbol, bars_dict)
                
                if analysis['recommendation'] == 'BUY':
                    results['buy_signals'].append(analysis)
                elif analysis['recommendation'] == 'SELL':
                    results['sell_signals'].append(analysis)
                else:
                    results['hold_signals'].append(analysis)
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        mt5.shutdown()
        return results
    
    def _init_mt5(self):
        """تهيئة MetaTrader"""
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        return True
    
    def _fetch_all_timeframes(self, symbol, bars_count=200):
        """جلب بيانات الأسعار لكل الفريمات الزمنية"""
        bars_dict = {}
        
        # تحويل أسماء الفريمات إلى MT5 constants
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            3: mt5.TIMEFRAME_M3,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
            240: mt5.TIMEFRAME_H4,
            1440: mt5.TIMEFRAME_D1,
        }
        
        for minutes, timeframe in timeframe_map.items():
            try:
                bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars_count)
                if bars is not None:
                    bars_dict[minutes] = self._convert_bars_to_dict(bars)
            except Exception as e:
                logger.debug(f"Error fetching {symbol} {minutes}m: {e}")
        
        return bars_dict
    
    @staticmethod
    def _convert_bars_to_dict(bars):
        """تحويل بيانات الأسعار إلى قاموس"""
        return [
            {
                'time': bar[0],
                'open': bar[1],
                'high': bar[2],
                'low': bar[3],
                'close': bar[4],
                'volume': bar[5]
            }
            for bar in bars
        ]

# ═══════════════════════════════════════════════════════════════════════════
#  نقاط النهاية (Endpoints)
# ═══════════════════════════════════════════════════════════════════════════

# تهيئة الكائنات
analyzer = TechnicalAnalyzer()
ai_engine = AITradingEngine()
risk_manager = RiskManager(CONFIG)
scanner = ForexScanner(ai_engine, CONFIG)

@app.route('/ping', methods=['GET'])
def ping():
    """اختبار الاتصال"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0",
        "engine": "AI Trading Engine"
    })

@app.route('/scan_forex', methods=['GET'])
def scan_forex():
    """
    فحص جميع أزواج الفوركس والحصول على الإشارات
    """
    try:
        results = scanner.scan_all_symbols()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/<symbol>', methods=['GET'])
def analyze_symbol(symbol):
    """
    تحليل رمز معين على كل الفريمات
    """
    try:
        if not scanner._init_mt5():
            return jsonify({"error": "MT5 not available"}), 503
        
        bars_dict = scanner._fetch_all_timeframes(symbol, 200)
        if not bars_dict:
            mt5.shutdown()
            return jsonify({"error": f"Symbol {symbol} not found"}), 404
        
        analysis = ai_engine.analyze_symbol(symbol, bars_dict)
        mt5.shutdown()
        
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/recommendation', methods=['POST'])
def get_recommendation():
    """
    احصل على توصية للدخول والخروج (TP/SL)
    """
    try:
        data = request.get_json()
        secret = data.get('secret')
        
        if secret != CONFIG['WEBHOOK_SECRET']:
            return jsonify({"error": "Unauthorized"}), 401
        
        symbol = data.get('symbol', 'EURUSD').upper()
        
        if not scanner._init_mt5():
            return jsonify({"error": "MT5 not available"}), 503
        
        # جلب التحليل
        bars_dict = scanner._fetch_all_timeframes(symbol, 200)
        analysis = ai_engine.analyze_symbol(symbol, bars_dict)
        
        # جلب السعر الحالي
        tick = mt5.symbol_info_tick(symbol)
        current_price = tick.ask if tick else 0
        
        # حساب SL/TP بناءً على ATR
        df_h1 = pd.DataFrame(bars_dict.get(60, []))
        if len(df_h1) > 0:
            high_low = df_h1['high'] - df_h1['low']
            atr = high_low.rolling(14).mean().iloc[-1]
        else:
            atr = current_price * 0.01  # 1% كقيمة افتراضية
        
        # تحديد نقاط الدخول والخروج
        if analysis['recommendation'] == 'BUY':
            entry = current_price
            stop_loss = current_price - (atr * 2)
            take_profit = current_price + (atr * 3)
        elif analysis['recommendation'] == 'SELL':
            entry = current_price
            stop_loss = current_price + (atr * 2)
            take_profit = current_price - (atr * 3)
        else:
            mt5.shutdown()
            return jsonify({
                "recommendation": "HOLD",
                "confidence": 0,
                "reason": "No clear signal"
            })
        
        mt5.shutdown()
        
        return jsonify({
            "symbol": symbol,
            "recommendation": analysis['recommendation'],
            "confidence": round(analysis['confidence'], 2),
            "entry_price": round(entry, 5),
            "stop_loss": round(stop_loss, 5),
            "take_profit": round(take_profit, 5),
            "risk_reward_ratio": round(abs((take_profit - entry) / (entry - stop_loss)), 2) if entry != stop_loss else 0,
            "analysis_details": analysis
        })
    
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/auto_trade', methods=['POST'])
def auto_trade():
    """
    تنفيذ صفقة تلقائية بناءً على التحليل
    """
    try:
        data = request.get_json()
        secret = data.get('secret')
        
        if secret != CONFIG['WEBHOOK_SECRET']:
            return jsonify({"error": "Unauthorized"}), 401
        
        if not scanner._init_mt5():
            return jsonify({"error": "MT5 not available"}), 503
        
        # جلب بيانات الحساب
        account = mt5.account_info()
        if not account:
            mt5.shutdown()
            return jsonify({"error": "Account info not available"}), 500
        
        # المسح والفحص
        results = scanner.scan_all_symbols()
        
        executed_trades = {
            'buy': [],
            'sell': [],
            'failed': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # تنفيذ إشارات الشراء
        for signal in results['buy_signals'][:5]:  # حد أقصى 5 صفقات في المسح
            symbol = signal['symbol']
            if signal['confidence'] > 0.6:  # ثقة أعلى من 60%
                result = _execute_trade(symbol, 'BUY', account.balance, account.equity)
                executed_trades['buy'].append(result)
        
        # تنفيذ إشارات البيع
        for signal in results['sell_signals'][:5]:
            symbol = signal['symbol']
            if signal['confidence'] > 0.6:
                result = _execute_trade(symbol, 'SELL', account.balance, account.equity)
                executed_trades['sell'].append(result)
        
        mt5.shutdown()
        return jsonify(executed_trades)
    
    except Exception as e:
        logger.error(f"Auto trade error: {e}")
        return jsonify({"error": str(e)}), 500

def _execute_trade(symbol, direction, balance, equity):
    """تنفيذ صفقة واحدة"""
    try:
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {"symbol": symbol, "status": "failed", "reason": "No tick data"}
        
        # حساب حجم اللوت
        entry_price = tick.ask if direction == 'BUY' else tick.bid
        stop_loss = entry_price * 0.98 if direction == 'BUY' else entry_price * 1.02
        
        position_size = risk_manager.calculate_position_size(balance, entry_price, stop_loss)
        
        # إنشاء الطلب
        order_type = mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL
        
        request_data = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position_size,
            "type": order_type,
            "price": entry_price,
            "sl": stop_loss,
            "tp": entry_price + (entry_price - stop_loss) * 2,
            "deviation": 30,
            "magic": 778899,
            "comment": "AutoBot-AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request_data)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {
                "symbol": symbol,
                "direction": direction,
                "status": "success",
                "ticket": result.order,
                "price": result.price,
                "volume": result.volume
            }
        else:
            return {
                "symbol": symbol,
                "status": "failed",
                "reason": f"Retcode: {result.retcode}",
                "comment": result.comment
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "status": "failed",
            "reason": str(e)
        }

# ═══════════════════════════════════════════════════════════════════════════
#  تشغيل السيرفر
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("  AutoBot PRO — Advanced AI Trading Engine v4.0")
    logger.info("  Forex Scanner + SMC + Harmonics + Classic Analysis")
    logger.info("  http://0.0.0.0:5000")
    logger.info("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
