from datetime import time
import numpy as np
import streamlit as st
import math

def get_sma(param1):
    name = "SMA_" + str(param1)
    st.session_state.df[name] = np.array(st.session_state.df["close"].rolling(window=param1).mean())
    return 

def get_wma(param1):
    name = "WMA_" + str(param1)
    wma = np.array([])
    den = param1 * (param1+1) / 2
    for i in range(len(st.session_state.df.close)):
        if i < param1-1:
            wma = np.append(wma, np.nan)
        else:
            mol = 0
            for j in range(param1):
                mol += (param1 - j) * st.session_state.df.close[i-j]
            wma = np.append(wma, mol/den)
    st.session_state.df[name] = wma
    return 

def get_macd(fast, slow, signalperiod):
    name_no = str(fast) + "_" + str(slow) + "_" + str(signalperiod)
    name1 = "MACD_" + name_no
    name2 = "MACDs_" + name_no
    name3 = "MACDh_" + name_no
  
    st.session_state.df[name1] = st.session_state.df.close.ewm(span=fast).mean() - st.session_state.df.close.ewm(span=slow).mean()
    st.session_state.df[name2] = st.session_state.df[name1].ewm(span=signalperiod).mean()
    st.session_state.df[name3] = st.session_state.df[name1] - st.session_state.df[name2]
    idx = slow + signalperiod - 2
    st.session_state.df[name1][:idx] = np.nan
    st.session_state.df[name2][:idx] = np.nan
    st.session_state.df[name3][:idx] = np.nan
    
    return 




def get_RSI(timeperiod):
    name = "RSI_" + str(timeperiod)
    diff = st.session_state.df.close.diff()
    diff_data = diff
    up, down = diff_data.copy(), diff_data.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    up_sma = up.rolling(window=timeperiod, center=False).mean()
    down_sma = down.abs().rolling(window=timeperiod, center=False).mean()
    RS = up_sma / down_sma
    st.session_state.df[name] = 100.0 - (100.0 / (1.0 + RS))

    return 

def get_HV(term):
    name = "HV_" + str(term)
    R = np.array([])
    R_s = np.array([])

    for i in range(len(st.session_state.df.close)):
        if i == 0 : R = np.append(R, 0)
        else:
            R_i = math.log(st.session_state.df.close[i] / st.session_state.df.close[i-1])
            R = np.append(R, R_i)
            
    
    for i in range(len(st.session_state.df.close)):
        if i < term-1: R_s = np.append(R_s, np.nan)
        else:
            R_s_i = np.std(R[i-term+1:i+1], ddof=0)
            R_s = np.append(R_s, R_s_i)

    HV = R_s* (math.sqrt(250) * 100)
    st.session_state.df[name] = HV

    return 


def get_rate(n):
    name = "rate_" + str(n) 
    rates = []
    
    for i in range(len(st.session_state.df["close"])):
        if i < n:
            rate = np.nan
        else:
            rate = (st.session_state.df["close"][i] - st.session_state.df["close"][i-n]) / st.session_state.df["close"][i-n]
        rates.append(rate)

    st.session_state.df[name] = rates
    return 