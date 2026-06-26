# 🚀 AutoBot PRO v4.0 - Advanced AI Trading Engine

**نظام تداول ذكي متقدم للفوركس على كل الفريمات**

## 📋 محتويات المجلد

```
AutoBot_PRO_v4/
├── README.md (هذا الملف)
├── requirements.txt (المتطلبات)
├── SERVER/
│   └── autobot_advanced_server.py (سيرفر Python الرئيسي)
├── EA_MT5/
│   └── AutoBot_AI_MT5.mq5 (المستشار الخبير للـ MT5)
├── CONFIG/
│   └── settings.json (إعدادات التداول)
└── DOCS/
    ├── التثبيت.txt
    ├── التكوين.txt
    └── الاستخدام.txt
```

---

## ⚡ المميزات الرئيسية

✅ **AI متقدم** - تحليل ذكي على جميع الفريمات (M1, M3, M5, M15, M30, H1, H4, D1)  
✅ **SMC + Harmonics** - تحديد مستويات العرض والطلب والأنماط التوافقية  
✅ **Classic Analysis** - EMA, RSI, MACD, Bollinger Bands  
✅ **إدارة مخاطر** - حساب حجم اللوت التلقائي + TP/SL دقيق  
✅ **ماسح فوركس** - فحص 20+ أزواج تلقائياً  
✅ **تنفيذ آلي** - فتح صفقات بناءً على الإشارات  

---

## 🔧 التثبيت السريع

### 1️⃣ **تثبيت Python والمكتبات**

```bash
# تثبيت Python 3.9+
# من: https://www.python.org/downloads/

# نسخ المجلد إلى حاسوبك
cd AutoBot_PRO_v4/SERVER

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 2️⃣ **تشغيل السيرفر**

```bash
python autobot_advanced_server.py
```

ستظهر الرسالة:
```
======================================================================
  AutoBot PRO — Advanced AI Trading Engine v4.0
  http://0.0.0.0:5000
======================================================================
```

### 3️⃣ **تثبيت EA على MT5**

- انسخ ملف `AutoBot_AI_MT5.mq5` إلى:
  ```
  C:\Users\[اسمك]\AppData\Roaming\MetaQuotes\Terminal\[TerminalID]\MQL5\Experts
  ```
- افتح MT5 وافتح الـ MetaEditor (F11)
- اضغط Compile على الملف
- اسحب EA على أي رسم بياني

---

## 📊 API النقاط

### 1. اختبار الاتصال
```
GET http://localhost:5000/ping
```

### 2. فحص جميع الأزواج
```
GET http://localhost:5000/scan_forex
```

**الرد:**
```json
{
  "buy_signals": [...],
  "sell_signals": [...],
  "hold_signals": [...]
}
```

### 3. تحليل زوج معين
```
GET http://localhost:5000/analyze/EURUSD
```

### 4. احصل على توصية (Entry + TP + SL)
```
POST http://localhost:5000/recommendation
Content-Type: application/json

{
  "secret": "autobot_pro_2025_secure",
  "symbol": "GBPUSD"
}
```

**الرد:**
```json
{
  "symbol": "GBPUSD",
  "recommendation": "BUY",
  "confidence": 0.75,
  "entry_price": 1.27450,
  "stop_loss": 1.27200,
  "take_profit": 1.28000,
  "risk_reward_ratio": 3.0
}
```

### 5. تنفيذ صفقات تلقائية
```
POST http://localhost:5000/auto_trade
Content-Type: application/json

{
  "secret": "autobot_pro_2025_secure"
}
```

---

## ⚙️ الإعدادات الرئيسية

في `SERVER/autobot_advanced_server.py`:

```python
CONFIG = {
    'WEBHOOK_SECRET': 'autobot_pro_2025_secure',  # غيّره!
    'FOREX_PAIRS': [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', ...
    ],
    'MAX_POSITIONS': 10,           # أقصى صفقات مفتوحة
    'RISK_PER_TRADE': 0.02,        # 2% من الرصيد
    'MAX_DAILY_LOSS': 0.05,        # 5% خسارة يومية قصوى
    'MAX_SPREAD': 50,              # نقاط
}
```

---

## 📱 التحليلات المتقدمة

### 🔍 SMC (Smart Money Concepts)
- تحديد مستويات العرض والطلب
- اكتشاف أماكن تراكم الأموال الذكية

### 🎯 Harmonic Patterns
- Fibonacci Retracement
- AB=CD Patterns
- Gartley و Butterfly

### 📈 Classic Indicators
- **EMA (Exponential Moving Average)** - الاتجاه
- **RSI (Relative Strength Index)** - الزخم
- **MACD** - التقاطعات
- **Bollinger Bands** - المستويات الحدية
- **Momentum** - قوة الحركة

### 🗳️ Voting System
كل مؤشر يصوت (BUY/SELL/HOLD) والقرار النهائي بناءً على الأغلبية

---

## 🎮 نموذج الاستخدام

### السيناريو 1: تداول يدوي مع AI
1. افتح السيرفر
2. اطلب توصية: `/recommendation?symbol=EURUSD`
3. ادخل يدوياً بالمستويات المقترحة

### السيناريو 2: تداول آلي بنسبة 100%
1. افتح السيرفر
2. ركب EA على MT5
3. شغّل EA وسيفتح صفقات تلقائياً

---

## ⚠️ تحذيرات مهمة

🔴 **لا تستخدم على حساب حقيقي مباشرة!**

1. **ابدأ بـ Demo أولاً** - أسبوع كامل على حساب تجريبي
2. **راقب الأداء** - سجل كل الصفقات والنتائج
3. **عدّل الإعدادات** - لا تثق بالأرقام الافتراضية
4. **استخدم حد أدنى** - ابدأ بـ 0.01 لوت فقط

---

## 📞 الدعم

- **مشكلة في الاتصال؟** تأكد من تشغيل MT5 والسيرفر
- **لا توجد إشارات؟** تحقق من وجود بيانات أسعار كافية
- **خطأ في التنفيذ؟** اقرأ السجلات (logs)

---

## 📄 الملفات المهمة

| الملف | الوصف |
|------|--------|
| `autobot_advanced_server.py` | السيرفر الرئيسي (Python) |
| `AutoBot_AI_MT5.mq5` | EA الخبير (MQL5) |
| `settings.json` | الإعدادات المحفوظة |

---

**إصدار 4.0 | آخر تحديث: 2025**
