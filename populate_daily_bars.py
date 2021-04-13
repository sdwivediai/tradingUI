import sqlite3, config
import tulipy, numpy
import pandas as pd
from ib_insync import *
from datetime import date, datetime, timedelta

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)


connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
current_date = date.today().isoformat()

cursor.execute("""
    SELECT * FROM stock where exchange == 'NASDAQ'
""")

rows = cursor.fetchall()


for row in rows:
    print(f"processing symbol {row['symbol']}")
    
    stock = Stock(row['symbol'], 'ISLAND', 'USD')
    stock_id = row['id']
    bars = ib.reqHistoricalData(
    stock, endDateTime='', durationStr='3 M',
    barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True, keepUpToDate=False)

    daily_bars = util.df(bars)
    daily_bars.set_index('date', inplace=True)
    
    for index, row in daily_bars.iterrows():
        cursor.execute("""
            INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, index, row['open'], row['high'], row['low'], row['close'], row['volume']))
        
    connection.commit()

ib.disconnect()