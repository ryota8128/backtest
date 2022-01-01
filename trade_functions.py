from datetime import datetime

def exit_check(sell_rules, df, info, t):
    ### info : (株数/100, entry_day, entry_price)
    t2t = {"t":t, "t-1":t-1, "t-2":t-2, "t-3":t-3, "t-4":t-4, "t-5":t-5}
    exi_bool = True
    exi_price = 0
    stock_num = info[0]
    exit_date = df.date[t+1]
    sasine_bool = True
    hold_period = 0

    for rule in sell_rules:
        if len(rule) == 4 or len(rule) ==5:
            sasine_bool = False
            if len(rule) == 5:
                L = df[rule[0]][t2t[rule[1]]] 
                R = df[rule[3]][t2t[rule[4]]]

            else:#len(rule) == 4
                L = df[rule[0]][t2t[rule[1]]] 
                R = rule[3]

            check = {"<": L<R, ">": L>R, "<=":L<=R, ">=": L>=R, "=":L==R}
            if not check[rule[2]]:
                exi_bool = False
                break

        if len(rule) == 2:
            win_r, lose_r = rule[0], rule[1]
            win_price = info[2] * (win_r+1)
            lose_price = info[2] * (lose_r+1)

            if df["high"][t] > win_price:
                exi_bool = True
                exi_price = max(df["open"][t], win_price)
            elif df["low"][t] < lose_price:
                exi_bool = True
                exi_price = min(df["open"][t], lose_price)
            else:
                exi_bool = False


    if exi_bool:
        if not sasine_bool:
            exi_price = df["open"][t+1]

        hold_period = days_calc(info[1], exit_date) 
    
    return exi_bool, exi_price, stock_num, hold_period


def days_calc(date1, date2):
    #str(yyyy/mm/dd)を入力として二つの日付の差をintで取得
    day1 = [int(i) for i in date1.split("/")]
    day2 = [int(i) for i in date2.split("/")]
    dt = datetime(*day2) - datetime(*day1)
    return int(dt.days)


def entry_check(buy_rules, df, t):
    entry_bool = True
    t2t = {"t":t, "t-1":t-1, "t-2":t-2, "t-3":t-3, "t-4":t-4, "t-5":t-5}
    for rule in buy_rules:
        if len(rule) == 5:
            L = df[rule[0]][t2t[rule[1]]] 
            R = df[rule[3]][t2t[rule[4]]]


        else:#len(rule) == 4
            L = df[rule[0]][t2t[rule[1]]] 
            R = rule[3]

        check = {"<": L<R, ">": L>R, "≦":L<=R, "≧": L>=R, "=":L==R}
        print(L,R)
        print(check[rule[2]])
        if not check[rule[2]]:
            entry_bool = False
            break

    return entry_bool
