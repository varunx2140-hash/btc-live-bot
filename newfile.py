import pandas as pd

# CSV file load (tumhara storage path)
data = pd.read_csv("/storage/emulated/0/New Folder/btc5m.csv")

# Binance dataset columns rename
data.columns = [
"open_time",
"open",
"high",
"low",
"close",
"volume",
"close_time",
"qav",
"num_trades",
"taker_base",
"taker_quote",
"ignore"
]

# EMA 20 calculate
data["ema20"] = data["close"].ewm(span=20).mean()

wins = 0
loss = 0

for i in range(20, len(data)-3):

    c1 = data.iloc[i]
    c2 = data.iloc[i+1]
    c3 = data.iloc[i+2]

    # BUY CONDITION
    if (
        c1["close"] > c1["ema20"]
        and c2["close"] > c2["open"]
        and c3["close"] > c3["open"]
    ):

        entry = c3["close"]
        sl = c1["low"]
        tp = entry + (entry-sl)*3

        for j in range(i+3, len(data)):

            high = data.iloc[j]["high"]
            low = data.iloc[j]["low"]

            if low <= sl:
                loss += 1
                break

            if high >= tp:
                wins += 1
                break


    # SELL CONDITION
    if (
        c1["close"] < c1["ema20"]
        and c2["close"] < c2["open"]
        and c3["close"] < c3["open"]
    ):

        entry = c3["close"]
        sl = c1["high"]
        tp = entry - (sl-entry)*3

        for j in range(i+3, len(data)):

            high = data.iloc[j]["high"]
            low = data.iloc[j]["low"]

            if high >= sl:
                loss += 1
                break

            if low <= tp:
                wins += 1
                break


total = wins + loss

print("Total Trades:", total)
print("Wins:", wins)
print("Loss:", loss)

if total > 0:
    print("Win Rate:", (wins/total)*100)