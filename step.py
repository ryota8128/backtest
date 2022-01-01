import streamlit as st
from datetime import date
from streamlit.state.session_state import Value
from technical import *
from streamlit.type_util import Key
from functions import *
from style import *
from yahoo_finance_api2.exceptions import YahooFinanceError as e
import copy
from trade_functions import *
import altair as alt
import pandas as pd


def leftbar():
    st.sidebar.write("# 設定")
    st.session_state.brand_key = st.sidebar.text_input("銘柄コードを入力", "XXXX.T")
    left_column, middle_column, right_column = st.sidebar.columns([4,1,4])
    start_date = left_column.date_input('対象期間を選択',
                                min_value=date(2000, 1, 1),
                                max_value=date.today(),
                                value=date(2015, 1, 1),
                                )
    middle_column.write("")
    middle_column.markdown("# ~")
    end_date = right_column.date_input('',
                                min_value=date(1900, 1, 1),
                                max_value=date.today(),
                                value=date.today(),
                                )


    st.sidebar.button("データ取得", on_click=get_data, args=(st.session_state.brand_key, start_date, end_date))
    

    return 


##########################################################################################################################

def step0(content1, content2, content3):
    with content1.container():
        st.title("株式トレード　バックテスト")
        if st.session_state.get_data_error:
            st.error("データが見つかりません。データを取得し直してください")
        
        else:
            st.write("データを取得してください。")
           

   
     
        if st.session_state.step==0:
            st.stop()

        return


################################################################################################################################

def step1(content1, content2, content3):
    st.session_state.df = copy.copy(st.session_state.df_origin)
    technical_indicator = ["-", "Simple Moving Average", "Weighted Moving Average", 
                            "Historical Volatility", "Moving Average Convergence Divergence", "Relative Strength Index", "close rate"]
    indicator2key = {"-":"-", "Simple Moving Average" : "SMA", "Weighted Moving Average" : "WMA", "Historical Volatility" : "HV", 
                        "Moving Average Convergence Divergence" : "MACD", "Relative Strength Index" : "RSI", "close rate":"rate"}
    param_num = {"SMA":1, "WMA":1, "HV":1, "MACD":3, "RSI":1, "rate":1}
    input_labels = {"SMA":["期間"], "WMA":["期間"], "HV":["期間"], "MACD":["fast", "slow", "signal period"], "RSI":["期間"], "rate":["何日前との比？"]}
    input_default = {"SMA":[5], "WMA":[5], "HV":[20], "MACD":[12,26,9], "RSI":[14], "rate":[1]}
    if "selected_indicators" not in st.session_state:
        st.session_state.selected_indicators = []

    with content1.container():
        st.title("テクニカル指標の設定")
        st.markdown("#")

        selected_ind = st.selectbox("追加するテクニカル指標を選択", options=technical_indicator)
        selected_ind = indicator2key[selected_ind]
        param = []

      
        if selected_ind != "-":
            st.write("##### パラメータ設定")
            cols = st.columns(param_num[selected_ind])
            for i, col in enumerate(cols):
                param.append(col.number_input(label=input_labels[selected_ind][i] , min_value=1, max_value=200, value=input_default[selected_ind][i]))
    
    
            if st.button("候補に追加"):
                indicator_name = param2name(selected_ind, param)
                if indicator_name not in st.session_state.selected_indicators:
                    st.session_state.selected_indicators.append(indicator_name)


        ###選択したindicatorを全て表示
        st.markdown("####")
        st.markdown("####")
        st.write("##### 選択されたインジケーター")
        st.session_state.selected_true_indicators = st.multiselect("売買ルールに使用するものを選択",options=st.session_state.selected_indicators,default=st.session_state.selected_indicators)
        st.session_state.reset_indicator = True
    

    





    
    id2func = {"SMA":get_sma, "WMA":get_wma, "MACD": get_macd, "HV":get_HV, "RSI": get_RSI, "rate":get_rate}
    

    for indicator in st.session_state.selected_true_indicators:
        if indicator not in st.session_state.df.columns:
            key, param = name2param(indicator)
            id2func[key](*param)



    with content2.container():
      
        st.markdown("##")
        st.write("#####", st.session_state.brand_key)
        #st.write(st.session_state.df[["macd","macd_sig"]].style.format('{:.2f}'))
        st.dataframe(st.session_state.df)
        st.markdown("##")
        st.button("ルール設定へ",on_click=step_change, args=(2,))
    
    return 




#######################################################################################################################################

def step2(content1, content2, content3):
    get_style("B_2_size") 

    columns = list(st.session_state.df.columns)
    del columns[0]
    st.session_state.selected_true_indicators = columns


    Ts = ["t", "t-1", "t-2", "t-3", "t-4", "t-5"]
    with content1.container():
        st.title("売買ルール設定")

        ################買いルール設定
        st.write("### 買いルール")
        num_input = st.checkbox("数値入力", value=False, key="call_num_input")
        with st.form(key="rule_form", clear_on_submit=False):
            cols = st.columns([2.5,1.1,1.2,2.5,1.1])
            id_1 = cols[0].selectbox(label="指標", key=0, options=st.session_state.selected_true_indicators)
            t_1 = cols[1].selectbox(label="", key=1, options=Ts)
            sign = cols[2].selectbox(label="", key=2, options=["<", ">", "≦", "≧", "="])
            col_3_content = cols[3].empty()
            

            with col_3_content:
                if num_input:
                    id_2 = st.number_input("数値")
                else:
                    id_2 = cols[3].selectbox(label="指標", key=3, options=st.session_state.selected_true_indicators)
                    t_2 = cols[4].selectbox(label="", key=4, options=Ts)
 
            submit_button = st.form_submit_button("追加")
        
        if submit_button:
            if num_input:
                rule_id = (id_1, t_1, sign, id_2)
                
            else:
                rule_id = (id_1, t_1, sign, id_2, t_2)

            if "rules_buy" not in st.session_state:
                st.session_state.rules_buy = []
            if rule_id not in st.session_state.rules_buy:
                st.session_state.rules_buy.append(rule_id)

        
        #######売りのルール設定
        st.markdown("#")
        st.write("### 売りルール")
        method = st.radio("", options=("指値逆指値方式", "ルール設定方式"), on_change=reset_sell_rule)
        if method == "指値逆指値方式":#############指値逆指値方式
            

            with st.form(key="num_sell_form", clear_on_submit=False):
                cols = st.columns(2)
                price = cols[0].number_input("利益確定",min_value=0.0, max_value=1.0, value=0.10)
                reverse_price  = cols[1].number_input("損切",min_value=-1.0, max_value=0.0, value=-0.10)
                submit_button = st.form_submit_button("追加")
            
            if submit_button:
                rule_id = (price, reverse_price)
                if "rules_sell" not in st.session_state:
                    st.session_state.rules_sell = []
                if rule_id not in st.session_state.rules_sell:
                    if len(st.session_state.rules_sell) == 1:
                        st.error("指値逆指値方式のルールは二つ以上登録できません")
                    else:
                        st.session_state.rules_sell.append(rule_id)

            
        
        else:#####ルール設定方式の時      
            num_input_sell = st.checkbox("数値入力", value=False, key="sell_num_input")
            with st.form(key="rule_buy_form", clear_on_submit=False):
                cols = st.columns([2.5,1.1,1.2,2.5,1.1])
                id_1 = cols[0].selectbox(label="指標", key=4, options=st.session_state.selected_true_indicators)
                t_1 = cols[1].selectbox(label="", key=5, options=Ts)
                sign = cols[2].selectbox(label="", key=6, options=["<", ">", "≦", "≧", "="])
                col_3_content = cols[3].empty()
                
                
                with col_3_content:
                    if num_input_sell:
                        id_2 = st.number_input("数値")
                    else:
                        id_2 = cols[3].selectbox(label="指標", key=3, options=st.session_state.selected_true_indicators)
                        t_2 = cols[4].selectbox(label="", key=4, options=Ts)

                submit_button = st.form_submit_button("追加")

                if submit_button:
                    if num_input_sell:
                        rule_id = (id_1, t_1, sign, id_2)
                        
                    else:
                        rule_id = (id_1, t_1, sign, id_2, t_2)


                    if rule_id not in st.session_state.rules_sell:
                        st.session_state.rules_sell.append(rule_id)


            ######売りルール設定終了


        if "rules_buy" in st.session_state:
            #選択済みルールを全て表示
            st.write("#### 選択された買いルール")
            left, right = st.columns([7,3])

            for i, rule_id in enumerate(st.session_state.rules_buy):
                left.latex(display_rule_func(rule_id))
                right.button("delete", key=f"2_0_{i}", on_click=delete_rule, args=(i,"buy"))

        if "rules_sell" in st.session_state:
            #選択済みルールを全て表示
            st.write("#### 選択された売りルール")
            left, right = st.columns([7,3])
            
            for i, rule_id in enumerate(st.session_state.rules_sell):
                left.latex(display_rule_func(rule_id))
                right.button("delete", key=f"2_1_{i}", on_click=delete_rule, args=(i,"sell"))
                    

    con3 = content3.container()
    with content2.container():
        st.markdown("#")
        st.markdown("#")
        left, right = con3.columns([9,1])

        if "rules_buy" in st.session_state and "rules_sell" in st.session_state:
            if len(st.session_state.rules_sell) * len(st.session_state.rules_buy) == 0:
                st.warning("買いと売りのルールの両方を設定してください")
            else:
                right.button("実行", on_click=step_change, args=(3,))
        else:
            st.warning("買いと売りのルールの両方を設定してください")
        left.button("指標設定に戻る", on_click=step_change, args=(1,))





#################################################################################################################################
#st.session_state.rules_sell
#st.session_state.rules_buy

    

def step3(content1, content2, content3):
    st.title("シミュレーション結果") 

    total_history = {"cash_hist":[], "asset_hist":[],  "hold_stock_num_hist":[], 
                    "PL_ratio":[],"hold_period":[], "win_num":0, "lose_num":0, "date_list":[],
                    "entry_num" : 0, "trade_info":[]}
    
    cash_init = 10000000 #現金
    cash = cash_init
    asset = cash  #資産（エントリー中の銘柄は買値で換算）
    hold_stock_num = 0 #所持株式数/100
    in_entry_info = []  #エントリー中の情報 : (stock_num, entry_day, entry_price)
    #total_history["entry_num"]通算entry回数（同時に200株買っても+1)
    #total_history["trade_info"] (entry_day, exit_day, entry_price, exit_price, margin(1株あたり), PL_ratio, hold_period, stock_num)
    #entry_stock_num = 0 #エントリー時に何(100)株買うかを一時的に保存
    df = st.session_state.df
    start_idx = df.isnull().sum().max()
    for t in range(len(df)):
        if t < start_idx or t == len(df)-1:####テクニカル指標の数値がないところは飛ばす
            continue
        
        total_history["date_list"].append(df.date[t])
        total_history["cash_hist"].append(cash)
        total_history["asset_hist"].append(asset)
        total_history["hold_stock_num_hist"].append(hold_stock_num)
        pop_index = []
        for j, ent_info in enumerate(in_entry_info):
            #### ent_info : (株数/100, entry_day, entry_price)
            exit_bool, exit_price, stock_num, hold_period = exit_check(st.session_state.rules_sell, df, ent_info, t)
            if exit_bool:#売却時処理
                ent_day, exit_day, ent_price,  = ent_info[1], df.date[t+1], ent_info[2]
                margin = exit_price - ent_price #1株あたり
                PL_r = margin / ent_price
    
                total_history["trade_info"].append((ent_day, exit_day, ent_price, exit_price, margin, stock_num))
                pop_index.append(j)
                hold_stock_num -= stock_num
                cash += stock_num * 100 * exit_price
                asset += stock_num * 100 * margin
                total_history["PL_ratio"].append(PL_r)
                total_history["hold_period"].append(hold_period)
                if margin > 0:
                    total_history["win_num"] += 1
                else:
                    total_history["lose_num"] += 1
        if len(pop_index) > 0:
            in_entry_info = [in_entry_info[i] for i in range(len(in_entry_info)) if i not in pop_index]

        
        
        if entry_check(st.session_state.rules_buy, df, t):
                entry_stock_num = 1 #100株１単位購入
                if df["close"][t] * 100 * entry_stock_num  < 0.8 * cash: #余裕を持ったcashで購入できる場合
                    entry_price = df["open"][t+1]
                    #brand.entry_info.append((date, entry_price)) ##
                    in_entry_info.append((entry_stock_num, df.date[t+1], entry_price)) ##売却時に削除する(購入単位、買い日、買値)
                    total_history["entry_num"] += 1 #エントリー回数を+1
                    cash -= entry_price * entry_stock_num * 100
                    hold_stock_num += entry_stock_num
    

    ###################トレード終了##################
   
    st.markdown("#")
    if len(total_history["trade_info"]):
        ave_rate = sum(total_history["PL_ratio"]) / len(total_history["PL_ratio"])
        win_rate = total_history["win_num"] / (total_history["win_num"] + total_history["lose_num"])
        ave_hold_period = sum(total_history["hold_period"]) / len(total_history["hold_period"])

        total_PL_ratio = (cash / cash_init) - 1 
        entry_num = total_history["entry_num"]
        st.write("平均損益率：{:.1f}%".format(ave_rate*100))
        st.write("勝率：{:.1f}%".format(win_rate*100))
        st.write(f"取引回数：{entry_num}回")

        st.write("平均保有期間：{:.1f}日".format(ave_hold_period))
        st.write("通算総利益：{:.1f}%".format(total_PL_ratio*100))
        #st.write(total_history["hold_stock_num_hist"])
        ymin = 0.5
        ymax = 1.5
        asset_hist = np.array(total_history["asset_hist"]) /cash_init
        cash_hist = np.array(total_history["cash_hist"]) /cash_init
        chart_df = pd.DataFrame({
            "date":total_history["date_list"],
            "asset" : asset_hist,
        })
        #data = pd.melt(chart_dic, id_vars="date")
        #st.dataframe(data)

        st.sidebar.write("""## グラフの範囲指定""")
        ymin, ymax = st.sidebar.slider(
            "範囲を指定してください",
            0.0, 3.0, (0.7, 1.4),
        )

        chart = (
                alt.Chart(chart_df)
                .mark_line(opacity=0.8, clip=True)
                .encode(
                    x="date:T",
                    y=alt.Y("asset:Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
                )
            )
        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("一度も取引が行われませんでした")
    st.button("ルール設定に戻る", on_click=step_change, args=(2,))

        



        






















                

        
        

    
