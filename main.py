import streamlit as st
import pandas as pd 
import tweepy
import numpy as np
#from wordcloud import WordCloud, STOPWORDS
from fetch_tweets import *
#import nltk
#from nltk.corpus import stopwords
#nltk.download('stopwords')
#from nltk.tokenize import word_tokenize
import itertools
import matplotlib.pyplot as plt
import seaborn as sns


btc_prices = pd.read_csv("btc_prices.zip", index_col = [0])
btc_prices.close = btc_prices.close.astype(float)
btc_prices.high = btc_prices.high.astype(float)
btc_prices.low = btc_prices.low.astype(float)
btc_prices.open = btc_prices.open.astype(float)

st.title('Tweets keywords analysis')

input = st.text_input('Write username')
df = get_tweets(input)

#st.dataframe(df.head())
st.write(f"got {len(df)} tweets pulled")
def filter_keywords(a,b):
    text = []
    dt = []
    for i in range(len(df)):
        if (a in df.tweet.iloc[i].lower())or (b in df.tweet.iloc[i].lower()):# or (c in df.tweet[i].lower()):
            text.append(df.tweet.iloc[i])
            dt.append(df.date.iloc[i])

    filtered_tweets = {"date":dt, 
                  "tweet":text}
    ft = pd.DataFrame(filtered_tweets)
    print(f"found {len(ft)} tweets containing {a} or {b}")
    return ft

def tokenize_words(filter_key):
    ls = []
    for i in range(len(filter_key)):
        text_tokens = word_tokenize(filter_key.tweet[i].lower())

        tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]

        ls.append(tokens_without_sw)
    list2d = ls
    merged = list(itertools.chain(*list2d))
    return merged

def prepare_heatmap(filter_key):
    flt = filter_key.resample("h").count()
    flt["hours"] = flt.index.hour
    flt["weekdays"] = flt.index.weekday
    days = pd.DataFrame(flt['weekdays'].unique())
    heatmap_pt = pd.pivot_table(flt, values='tweet', 
         index=['hours'], 
         columns='weekdays')
    return heatmap_pt

def backtest(filter_key,btc_prices,tps,spl ):
    profit = []
    dates = []
    for i in range(len(filter_key)): 
        try:
            init = btc_prices.loc[str(filter_key.iloc[i].date)].close
            ft = btc_prices.loc[str(filter_key.iloc[i].date):]
            tp = init * tps
            sp = init * spl
            last_btc_price = btc_prices.close[-1]
            print(str(filter_key.iloc[i].date))
    
            for j in ft.close:
                if j > tp: 
                    profit.append((j - init)/init)
                    dates.append(str(filter_key.iloc[i].date))
                    print((j - init)/init,"take profit")
                    #print(j.index)
                    break
                if j < sp: 
                    profit.append((j - init)/init)
                    dates.append(str(filter_key.iloc[i].date))
                    print((j - init)/init,"stop loss")
                    #print(j.index)
                    break
        except: 
            pass
    
    profits = pd.DataFrame(profit)
    profits = profits
    profits.index = dates[::-1]
    return profits.cumsum()

def returns_time(dts,dts20,btc_prices,filter_key):
    returns = []
    dt = []
    tweets = []
    buys = []
    sells = []
    for i in range(len(dts)):
        try:
            init = btc_prices.loc[str(dts[i])].close
            end = btc_prices.loc[str(dts20[i])].close
            returns.append((end - init)/init)
            dt.append(dts[i])
            tweets.append(filter_key.tweet[i])
            buys.append(init)
            sells.append(end)
        except: 
            pass
        
    returns_date = {"date":dt, 
                   "buy_price":buys,
                   "sell_price":sells,
                   "returns":returns,
                   "tweets":tweets}
    
    return pd.DataFrame(returns_date)
    
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

val1 = st.text_input('keyword 1').lower()
val2 = st.text_input('keyword 2').lower()

if val1 and val2:
    st.write(f'Got all inputs: {[val1, val2]}')
    filter_key = filter_keywords(val1,val2)
    filter_key.date = pd.to_datetime(filter_key.date)
    filter_key = filter_key.set_index("date")
    #st.dataframe(filter_key)
    st.write(f'{val1} and {val2} where {len(filter_key)} mentioned')
    
    #st.write("set after how long should sell in minutes")
    #number = st.number_input('Insert time to sell after purchase in minutes')
    number = int(st.text_input('minutes to sell after buy'))

    filter = filter_key.copy()
    filter = filter.reset_index()
    filter = filter[::-1].reset_index(drop = True)
    st.dataframe(filter)

    filter.date = filter.date.dt.ceil("min")
    st.dataframe(filter)
    filter_plus20 = filter.date + pd.Timedelta(f"{number}min")
    st.dataframe(filter_plus20)
    init = btc_prices.loc[str(filter.date[0][:-6])].close
    st.write(f"init balance {init}")
    df = returns_time(filter.date,filter_plus20,btc_prices,filter)
    st.dataframe(df)
    csv = convert_df(df)

    st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='returns.csv',
    mime='text/csv',
)

    st.write(f"Total profits {round(df.returns.sum(),4)} % if long on all tweets and selling after {number} minutes")
    st.line_chart(df.set_index("date")[["returns"]].cumsum())

    #st.title("Backtest")
    #takeprofit = st.number_input('take profits',value=1.02)
    #stoploss = st.number_input('stop loss',value=0.98)
    #bt = backtest(filter,btc_prices,takeprofit,stoploss)
    #st.write(f"number of orders {len(bt)} and total profits {bt.iloc[-1].values[0]}%")

    #st.line_chart(bt)
    heatmap_prep = prepare_heatmap(filter_key) 
    st.write("Tweets time by hours of the week and days")
        #lt = ["Monday","Tuesday","Wednesday","Thursday","Friday","Sathurday","Sunday"]
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_prep, ax=ax,cmap='YlGnBu')
    st.write(fig)

        
    
        


else:
    pass
