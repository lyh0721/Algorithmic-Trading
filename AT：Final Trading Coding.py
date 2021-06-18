#!/usr/bin/env python
# coding: utf-8

# In[165]:


import pandas as pd
import numpy as np


# In[166]:


pd.read_excel("BTC-USD.xlsx").head()


# In[167]:


BTC = pd.read_excel("BTC-USD.xlsx")


# In[168]:


BTC_modify = pd.DataFrame(BTC).dropna()


# In[169]:


import numpy
import talib

close = numpy.random.random(30)
print(type(close))
print(talib.SMA(close, timeperiod=5))

close = BTC_modify["Close"].to_numpy()
print(type(close))
print(talib.SMA(close, timeperiod=5))


# In[170]:


# note that all ndarrays must be the same length!
inputs = {
    'open': BTC_modify["Open"].to_numpy(),
    'high': BTC_modify["High"].to_numpy(),
    'low': BTC_modify["Low"].to_numpy(),
    'close': BTC_modify["Close"].to_numpy(),
    'volume': BTC_modify["Volume"].to_numpy()
}

from talib.abstract import *

SMA(inputs, timeperiod=5) # calculate on close prices by default
# print(output)
# print(len(list(output)))
# print(pd.DataFrame(output).dropna())
# print(pd.DataFrame(output).dropna().shape)


# In[171]:


BTC_modify["5ma"]=SMA(inputs,timeperiod=5)


# In[172]:


BTC_modify["7ma"]=None
BTC_modify["15ma"]=None
BTC_modify["21ma"]=None
BTC_modify["7ma"]=SMA(inputs,timeperiod=7)
BTC_modify["15ma"]=SMA(inputs,timeperiod=15)
BTC_modify["21ma"]=SMA(inputs,timeperiod=21)


# In[173]:


BTC_input=pd.DataFrame(BTC_modify).dropna()


# In[174]:


BTC_input["buy_day"]=0
BTC_input["cum_day"]=0
BTC_input["sell_day"]=0
BTC_input["number"]=0
BTC_input["value"]=0
BTC_input["period_return"]=0
BTC_input["holding_period"]=0
BTC_input["annual_return"]=0
BTC_input["diff"]=0
BTC_input["limit"]=-0.05
BTC_input["sell1"]=0


# In[175]:


#Strategy of trading
#買: 7MA>15MA or 7M>21MA
#賣: 21MA<15MA and 跌幅(by today open & adj close)5%隔天放空


# In[176]:


#sell1
for i in range(1, len(BTC_input)):
    upper=BTC_input["Adj Close"].iloc[i]-BTC_input["Open"].iloc[i]
    BTC_input["diff"].iloc[i]=upper/BTC_input["Open"].iloc[i]

for i in range(1, len(BTC_input)):
    if(BTC_input["diff"].iloc[i]<BTC_input["limit"].iloc[i]):
        BTC_input["sell1"].iloc[i]=1


# In[177]:


for i in range(1, BTC_input.shape[0]):
    if((BTC_input["7ma"].iloc[i] > BTC_input["15ma"].iloc[i])    or(BTC_input["7ma"].iloc[i] > BTC_input["21ma"].iloc[i]))    and(BTC_input["cum_day"].iloc[i-1]==0):
        BTC_input["buy_day"].iloc[i]  = 1
        BTC_input["cum_day"].iloc[i]  = 1
        BTC_input["sell_day"].iloc[i] = 0
    elif(BTC_input["21ma"].iloc[i] < BTC_input["15ma"].iloc[i])and(BTC_input["cum_day"].iloc[i-1]==1)and(BTC_input["sell1"].iloc[i+1]==1):
        BTC_input["buy_day"].iloc[i]  = 0
        BTC_input["cum_day"].iloc[i]  = 0
        BTC_input["sell_day"].iloc[i] = 1
    elif(BTC_input["cum_day"].iloc[i-1]>0):
        BTC_input["buy_day"].iloc[i]  = 0
        BTC_input["cum_day"].iloc[i]  = 1
        BTC_input["sell_day"].iloc[i] = 0


# In[178]:


BTC_input.to_excel("progb.xlsx")


# In[179]:


#add
initial=10000
for i in range(1, BTC_input.shape[0]):
#buy signal
    if(BTC_input["buy_day"].iloc[i]==1)and(BTC_input["cum_day"].iloc[i]==1)and(BTC_input["sell_day"].iloc[i]==0):
        BTC_input["number"].iloc[i] =initial/BTC_input["Adj Close"].iloc[i]
        BTC_input["value"].iloc[i]=BTC_input["number"].iloc[i]*BTC_input["Adj Close"].iloc[i]
        BTC_input["period_return"].iloc[i]=round((BTC_input["number"].iloc[i]*BTC_input["Adj Close"].iloc[i]-initial)/initial,4)
#sell signal
    elif(BTC_input["buy_day"].iloc[i]==0)and(BTC_input["cum_day"].iloc[i]==0)and(BTC_input["sell_day"].iloc[i]==1):
        BTC_input["number"].iloc[i]=0
        BTC_input["value"].iloc[i]=BTC_input["number"].iloc[i-1]*BTC_input["Adj Close"].iloc[i]
        BTC_input["period_return"].iloc[i]=round((BTC_input["number"].iloc[i-1]*BTC_input["Adj Close"].iloc[i]-initial)/initial,4)
#hoding
    elif(BTC_input["buy_day"].iloc[i]==0)and(BTC_input["cum_day"].iloc[i]==1)and(BTC_input["sell_day"].iloc[i]==0):
        BTC_input["number"].iloc[i]=BTC_input["number"].iloc[i-1]
        BTC_input["value"].iloc[i]=BTC_input["number"].iloc[i]*BTC_input["Adj Close"].iloc[i]
        BTC_input["period_return"].iloc[i]=round((BTC_input["number"].iloc[i]*BTC_input["Adj Close"].iloc[i]-initial)/initial,4)


# In[180]:


BTC_input.to_excel("progb0604.xlsx")


# In[181]:


start = 0
end = 0
for i in range(1, len(BTC_input)):
    if(BTC_input["buy_day"].iloc[i]==1):
        BTC_input["holding_period"].iloc[i] = 1
    elif((BTC_input["cum_day"].iloc[i] > 0) or (BTC_input["sell_day"].iloc[i] == 1))and(BTC_input["buy_day"].iloc[i] == 0):
        BTC_input["holding_period"].iloc[i] = BTC_input["holding_period"].iloc[i-1] +1
BTC_input.head(6)


# In[182]:


for i in range(1, len(BTC_input)):
    if(BTC_input["buy_day"].iloc[i]==1)or(BTC_input["sell_day"].iloc[i]==1)or(BTC_input["cum_day"].iloc[i]==1):
        BTC_input["annual_return"].iloc[i]= (1+BTC_input["period_return"].iloc[i])**(365/BTC_input["holding_period"].iloc[i])-1


# In[183]:


BTC_input.head(25)


# In[184]:


annual_return=1
annual_period_return=1
trading=0

for i in range(0,BTC_input.shape[0]):
    if(BTC_input["sell_day"].iloc[i]==1):
        annual_return*=(1+BTC_input["annual_return"].iloc[i])
        annual_period_return*=(1+BTC_input["period_return"].iloc[i])
        trading+=1

final_return=annual_return**(1/trading)-1
final_period_return=annual_period_return**(1/trading)-1
print("交易次數：",trading,"年化報酬",final_return,"期間年化報酬",final_period_return)


# In[186]:


annual_return = 1
annual_period_return = 1
trading = 0

for i in range(0, BTC_input.shape[0]):
    if(BTC_input["sell_day"].iloc[i]==1):
        annual_return *= (1 + BTC_input["annual_return"].iloc[i] )
        annual_period_return *= (1 + BTC_input["period_return"].iloc[i] )
        trading+=1

final_return=annual_return**(1/trading)-1
final_period_return=annual_period_return**(1/trading)-1
print("交易次數:", trading, "年化報酬:", final_return, "期間年化報酬:", final_period_return)


# In[188]:


BTC_input.to_excel("AT_Final.xlsx")


# In[ ]:




