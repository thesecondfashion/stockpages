#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import streamlit as st

st.title('Viewer')

tickers = ('AAPL','NVDA','MSFT','TSLA','AMD','AMZN','GOOG','TSM','PFE','BABA','WMT')
dropdown = st.multiselect('Pick a stock to view',tickers)

start=st.date_input('Start',value=pd.to_datetime('2023-01-01'))
end=st.date_input('End',value=pd.to_datetime('today'))

def relativeret(df):
    rel=df.pct_change()
    cumret=(1+rel).cumprod()-1
    cumret=cumret.fillna(0)
    return cumret

if len(dropdown)>0:
    #df=yf.download(dropdown,start,end)['Adj Close']
    df=relativeret(yf.download(dropdown,start,end)['Adj Close'])
    st.line_chart(df)
