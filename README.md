import requests
import pandas as pd
import time
import os

# =====================
# RESET STATE (IMPORTANT)
# =====================
active_trade = False
position = None
entry = 0
sl = 0
tp = 0

total_trades = 0
wins = 0
loss = 0
last_signal = "NONE"


# =====================
# DATA FETCH
# =====================
def get_data():
    url = "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit=200"
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","ct","q","n","tb","tq","i"
    ])

    df = df[["o","h","l","c"]].astype(float)
    return df


# =====================
# FIXED SAR (0.002, 0.002, 0.02)
# =====================
def sar(df):
    high = df["h"].values
    low = df["l"].values

    af_start = 0.002
    af_step = 0.002
    af_max = 0.02

    sar = [low[0]]
    ep = high[0]
    af = af_start
    uptrend = True

    for i in range(1, len(df)):
        prev_sar = sar[-1]

        if uptrend:
            val = prev_sar + af * (ep - prev_sar)
            val = min(val, low[i-1])

            if low[i] < val:
                uptrend = False
                sar.append(ep)
                ep = low[i]
                af = af_start
            else:
                sar.append(val)
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + af_step, af_max)

        else:
            val = prev_sar + af * (ep - prev_sar)
            val = max(val, high[i-1])

            if high[i] > val:
                uptrend = True
                sar.append(ep)
                ep = high[i]
                af = af_start
            else:
                sar.append(val)
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + af_step, af_max)

    df["sar"] = sar
    return df


# =====================
# STRATEGY
# =====================
def calc(df):
    df["ema69_high"] = df["h"].ewm(span=69).mean()
    df["ema69_low"] = df["l"].ewm(span=69).mean()

    df = sar(df)

    c = df.iloc[-1]
    price = c["c"]

    signal = "NONE"

    if price > c["ema69_high"] and c["sar"] < price:
        signal = "BUY"

    elif price < c["ema69_low"] and c["sar"] > price:
        signal = "SELL"

    return c, price, signal


# =====================
# CENTER UI
# =====================
def center(text, width=40):
    return str(text).center(width)


# =====================
# MAIN LOOP
# =====================
os.system("clear")
print(center("BTC LIVE BOT STARTED"))

while True:
    try:
        df = get_data()

        if len(df) < 50:
            continue

        c, price, signal = calc(df)

        # =====================
        # ENTRY (ONLY 1 TRADE)
        # =====================
        if not active_trade and signal != "NONE" and signal != last_signal:

            entry = price
            position = signal
            last_signal = signal

            sl = c["ema69_low"] if signal == "BUY" else c["ema69_high"]

            risk = abs(entry - sl)

            tp = entry + (risk * 3) if signal == "BUY" else entry - (risk * 3)

            active_trade = True
            total_trades += 1

        # =====================
        # EXIT LOGIC
        # =====================
        if active_trade:
            if position == "BUY":
                if price <= sl:
                    loss += 1
                    active_trade = False

                elif price >= tp:
                    wins += 1
                    active_trade = False

            elif position == "SELL":
                if price >= sl:
                    loss += 1
                    active_trade = False

                elif price <= tp:
                    wins += 1
                    active_trade = False


        # =====================
        # WIN RATE
        # =====================
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0


        # =====================
        # SCREEN REFRESH
        # =====================
        os.system("clear")


        # =====================
        # TERMINAL VIEW
        # =====================
        print(center("BTC LIVE BOT"))
        print(center("----------------------"))

        print(center(f"PRICE : {price:.2f}"))
        print(center(f"EMA 69 HIGH : {c['ema69_high']:.2f}"))
        print(center(f"EMA 69 LOW  : {c['ema69_low']:.2f}"))
        print(center(f"SAR : {c['sar']:.2f}"))

        print(center("----------------------"))

        if active_trade:
            print(center("ACTIVE TRADE : YES"))
            print(center(f"POSITION : {position}"))
            print(center(f"ENTRY : {entry:.2f}"))
            print(center(f"SL : {sl:.2f}"))
            print(center(f"TP : {tp:.2f}"))
        else:
            print(center("ACTIVE TRADE : NO"))

        print(center("----------------------"))

        print(center(f"TOTAL : {total_trades}"))
        print(center(f"WIN : {wins}"))
        print(center(f"LOSS : {loss}"))
        print(center(f"WIN RATE : {win_rate:.2f}%"))

        time.sleep(10)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
