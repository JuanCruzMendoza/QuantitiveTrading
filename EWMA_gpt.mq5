//+------------------------------------------------------------------+
//| EWMAC Trading Strategy for MT5                                   |
//| Uses two EWMA (16, 64) and adjusts position size with a          |
//| volatility target. Position sizing is computed as follows:       |
//| 1. Annualised cash vol target = TargetVol * Account Balance       |
//| 2. Daily cash vol = annualised cash vol target / sqrt(256)          |
//| 3. Price volatility (%) = (price std dev / current price) * 100       |
//| 4. Block value = current price * 0.01                              |
//| 5. Instrument value vol = block value * price volatility (%)         |
//| 6. Volatility scalar = daily cash vol target / instrument value vol    |
//| 7. Position = forecast * volatility scalar / 10                     |
//|                                                                  |
//| Only LONG positions are allowed. If forecast <= 0, any open         |
//| positions are closed and no new trade is opened.                   |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>

CTrade trade;

// --- Strategy Parameters ---
input int FastEMA = 16;
input int SlowEMA = 64;
input int VolPeriod = 25;            // Lookback period for price volatility
input double ForecastScalar = 3.75;
input double TargetVol = 0.15;       // Annualised volatility target (15%)
input ENUM_TIMEFRAMES Timeframe = PERIOD_D1;

//+------------------------------------------------------------------+
//| Compute Exponential Weighted Moving Average (EWMA)               |
//+------------------------------------------------------------------+
double ComputeEWMA(int period, int shift) {
   int handle = iMA(Symbol(), Timeframe, period, 0, MODE_EMA, PRICE_CLOSE);
   if(handle == INVALID_HANDLE)
      return 0;
   double buffer[1];
   if(CopyBuffer(handle, 0, shift, 1, buffer) != 1) {
      IndicatorRelease(handle);
      return 0;
   }
   IndicatorRelease(handle);
   return buffer[0];
}

//+------------------------------------------------------------------+
//| Compute Price Standard Deviation (Volatility Measure)            |
//+------------------------------------------------------------------+
double ComputePriceStdDev() {
   int handle = iStdDev(Symbol(), Timeframe, VolPeriod, 0, MODE_SMA, PRICE_CLOSE);
   if(handle == INVALID_HANDLE)
      return 0;
   double buffer[1];
   if(CopyBuffer(handle, 0, 0, 1, buffer) != 1) {
      IndicatorRelease(handle);
      return 0;
   }
   IndicatorRelease(handle);
   return buffer[0];
}

//+------------------------------------------------------------------+
//| Compute Forecast Signal                                          |
//+------------------------------------------------------------------+
double ComputeForecast() {
   double fastEWMA = ComputeEWMA(FastEMA, 0);
   double slowEWMA = ComputeEWMA(SlowEMA, 0);
   double priceStdDev = ComputePriceStdDev();
   
   Print("Fast EWMA: ", fastEWMA, " | Slow EWMA: ", slowEWMA, " | Price StdDev: ", priceStdDev);
   
   if(priceStdDev == 0)
      return 0;
   
   double forecast = ((fastEWMA - slowEWMA) / priceStdDev) * ForecastScalar;
   forecast = MathMax(-20, MathMin(20, forecast)); // Clamp forecast to [-20, +20]
   
   Print("Computed Forecast: ", forecast);
   
   return forecast;
}

//+------------------------------------------------------------------+
//| Compute Position Based on Volatility Targeting                   |
//+------------------------------------------------------------------+
double ComputePosition(double forecast) {
   // Trading capital
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   
   // 1. Annualised cash volatility target = TargetVol * balance
   double annualised_cash_vol_target = TargetVol * balance;
   
   // 2. Daily cash volatility = annualised cash vol target / sqrt(256)
   double daily_cash_vol_target = annualised_cash_vol_target / MathSqrt(256);
   
   // 3. Current price of the instrument
   double currentPrice = iClose(Symbol(), Timeframe, 0);
   if(currentPrice == 0)
      return 0;
   
   // 4. Price volatility in percentage = (priceStdDev / currentPrice) * 100
   double priceStdDev = ComputePriceStdDev();
   double price_volatility_pct = (priceStdDev / currentPrice) * 100;
   
   // 5. Block value: price of a block (ex: a share) * 0.01 (1%)
   double block_value = currentPrice * 0.01;
   
   // 6. Instrument value volatility = block value * price volatility (%)
   double instrument_value_vol = block_value * price_volatility_pct;
   
   // 7. Volatility scalar = daily cash volatility target / instrument value volatility
   double volatility_scalar = 0;
   if(instrument_value_vol != 0)
      volatility_scalar = daily_cash_vol_target / instrument_value_vol;
   
   // 8. Position (in blocks) = forecast * volatility scalar / 10
   // Use absolute value for volume; direction is given by the sign of forecast.
   double position = MathAbs(forecast * volatility_scalar / 10.0);
   
   Print("Balance: ", balance,
         " | Annualised Cash Vol Target: ", annualised_cash_vol_target,
         " | Daily Cash Vol Target: ", daily_cash_vol_target,
         " | Price Volatility (%): ", price_volatility_pct,
         " | Block Value: ", block_value,
         " | Instrument Value Vol: ", instrument_value_vol,
         " | Volatility Scalar: ", volatility_scalar,
         " | Final Position (blocks): ", position);
   
   return NormalizeDouble(position, 2);
}

//+------------------------------------------------------------------+
//| Execute Trades (Only LONG positions; adjust only if target is    |
//| more than 10% different from current long position)             |
//+------------------------------------------------------------------+
void ExecuteTrades() {
   // Adjust only once per week
   static datetime lastTradeTime = 0;
   if(TimeCurrent() - lastTradeTime < 7 * 86400)
      return;
   
   double forecast = ComputeForecast();
   
   // Only proceed if forecast is positive
   if(forecast <= 0) {
      // If forecast is not positive, close any existing positions
      if(PositionSelect(Symbol())) {
         Print("Forecast non-positive; closing any open positions.");
         trade.PositionClose(Symbol());
      }
      lastTradeTime = TimeCurrent();
      return;
   }
   
   double targetPosition = ComputePosition(forecast);
   
   Print("Forecast: ", forecast, " | Target Position (blocks): ", targetPosition);
   
   // Get current long position, if any.
   double currentVolume = 0;
   if(PositionSelect(Symbol())) {
      int posType = (int)PositionGetInteger(POSITION_TYPE);
      // Only consider long positions
      if(posType == POSITION_TYPE_BUY) {
         currentVolume = PositionGetDouble(POSITION_VOLUME);
      }
      else {
         // If a short position exists, close it.
         Print("Existing short position detected; closing it.");
         trade.PositionClose(Symbol());
         currentVolume = 0;
      }
   }
   
   // If there is an existing long position, check the difference.
   if(currentVolume > 0) {
      double diff = MathAbs(targetPosition - currentVolume);
      if(diff < 0.1 * currentVolume) {
         Print("Target position is within 10% of current long position; no modification.");
         lastTradeTime = TimeCurrent();
         return;
      }
   }
   
   // Close any existing long position before re-opening.
   if(PositionSelect(Symbol()))
      trade.PositionClose(Symbol());
   
   Print("Opening LONG position with volume: ", targetPosition);
   trade.Buy(targetPosition, Symbol());
   lastTradeTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| OnTick Function                                                  |
//+------------------------------------------------------------------+
void OnTick() {
   ExecuteTrades();
}
