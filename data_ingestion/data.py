import requests
from datetime import datetime, timezone
import time

def grab_data():
    """
    Matt
    Grabs all trades made today using kalshi API. 
    Future implementation: args to the function to request specific markets, times, and how many trades in total

    ticker = ID of trading market
    count_fp = number of shares in this transaction
    created_time = exact millisecond the trade was executed
    taker_side: In finance, a "Maker" puts an order on the board and waits. A "Taker" aggressively buys whatever is available right now. This field tells you which side the aggressive trader was betting on. In this case, the person initiating the trade bought "No" contracts.
    no_price_dollars & yes_price_dollars: no% and yes%, should add to one. dollar amount for the side better took
    trade_id: a unique identifier 
    """

    curr_time = datetime.now(timezone.utc) #grab current time
    start_of_day = curr_time.replace(hour=0, minute=0, second=0, microsecond=0) #roll back clock to midnight
    min_time = int(start_of_day.timestamp()) #start at midnight
    max_time = int(curr_time.timestamp()) #to now

    url = "https://api.elections.kalshi.com/trade-api/v2/markets/trades"

    params = {
        "limit": 100, #100 trades
        "min_ts": min_time, #start time
        "max_ts": max_time #end time
    }

    headers = {"accept": "application/json"}
    print("grabbing all trades on kalshi today")

    response = requests.get(url, headers=headers, params=params) #wait for response
    if response.status_code == 200:
        data = response.json()
        trades = data.get("trades", [])
        if trades: 
            print(trades[0])
    else:
        print(f"error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    grab_data()