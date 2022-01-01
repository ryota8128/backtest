from os import error
from yahoo_finance_api2 import share
import pandas as pd
from datetime import datetime, date
import math
import streamlit as st
from yahoo_finance_api2.exceptions import YahooFinanceError
from step import *
import numpy as np

def param2name(ind_name, param):
    return ind_name + "_" + "_".join(map(str, param))


def name2param(name):
    name = name.split("_")
    id = name[0]
    param = [int(i) for i in name[1:]]
    return id, param

def step_change(k):
    st.session_state.step = k
    return

def display_rule_func(rule_id):
    
    def fn(id, t):
        id = id.split("_")
        a = id[0] + "_"
        a += "{"+ ",".join(id[1:])+ "}"
        a += "^{" + t + "}"
        return a

    if len(rule_id) == 4:##数値入力の時
        id_1 = rule_id[0]
        t_1 = rule_id[1]
        sign = rule_id[2]
        id_2 = rule_id[3]
        return fn(id_1, t_1) + sign + str(id_2)
    elif len(rule_id) == 5:  ##指標入力の時
        id_1 = rule_id[0]
        t_1 = rule_id[1]
        sign = rule_id[2]
        id_2 = rule_id[3]
        t_2 = rule_id[4]
        return fn(id_1, t_1) + sign + fn(id_2, t_2)
    
    elif len(rule_id) == 2:#指値逆指値注文の時
        price = rule_id[0]
        reverse_price = rule_id[1] 
        return "指値: {:.1f}\%, 逆指値: {:.1f}\%".format(price*100, reverse_price*100)



def delete_rule(idx, side):
    if side == "buy":
        del st.session_state.rules_buy[idx]
    if side == "sell":
        del st.session_state.rules_sell[idx]

    return




def get_year(start_date):
    delta = date.today() - start_date
    term = math.ceil(delta.days/365)
    return term
    


def get_data(key, start_date, end_date):
    
    term = get_year(start_date)
    my_share = share.Share(key)
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(
        share.PERIOD_TYPE_YEAR, term,
        share.FREQUENCY_TYPE_DAY, 1)
        st.session_state.get_data_error = False
    except YahooFinanceError as e:
        st.session_state.get_data_error = True
        step_change(0)

    if not st.session_state.get_data_error:
        
        st.session_state.step = 1
        df = pd.DataFrame(symbol_data)
        df["date"] = pd.to_datetime(df.timestamp, unit="ms").dt.strftime("%Y/%m/%d")
        df = df.drop("timestamp", axis=1)
        date_int = np.array([int(i.replace("/","")) for i in list(df.date)])
        start_int = int(str(start_date).replace("-", ""))
        end_int = int(str(end_date).replace("-", ""))
        df = df[date_int <= end_int]
        date_int = date_int[date_int <= end_int]
        df = df[date_int >= start_int]
        st.session_state.df_origin = df.reset_index(drop=True).reindex(columns=["date", "open", "close", "high", "low", "volume"])
        
    
    return 


def reset_sell_rule():
    st.session_state.rules_sell = []
    return 


def date2int(date):
    ##date : str(yyyy/mm/dd)
    return int(date.replace("/", ""))


    