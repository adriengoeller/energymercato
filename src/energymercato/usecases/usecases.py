import pandas as pd
import numpy as np
from pathlib import Path

MWH_SOLAR_PRICE = 140
MWH_WIND_PRICE = 70

def make_plant(plant_type, pmin, pmax, mwh_cost, start_cost):
    def make_type_plant(p1, name):
        out = plant_type(
            p_min =  pmin*p1,
            p_max = pmax*p1,
            mwh_cost = mwh_cost,
            start_cost = start_cost,
            name = name
        )
        return out
    return make_type_plant


def make_storage_plant(plant_type, pmin, pmax, 
    mwh_cost, start_cost,mwh_cost_in, 
    start_cost_in):
    def make_type_plant(p1,c1):
        out = plant_type(
            p_min =  pmin*p1,
            p_max = pmax*p1,
            mwh_cost = mwh_cost,
            start_cost = start_cost,
            capacity_max = c1,
            mwh_cost_in = mwh_cost_in,
            start_cost_in = start_cost_in)
        return out
    return make_type_plant




# players = [
#     ndf, ngie, gazel, cnr 
# ]

# total_power = sum(c.get_prod() for c in players)
# total_power_enr = sum(c.get_prod(enr_only=True) for c in players)

# print("total_power: ", total_power)
# print("total_power_enr: ", total_power_enr," ", total_power_enr/total_power*100,"%")

# # total client needs : 280 indus + 150 TWh /y
# # edf : 27 m , totalnrj : 3.3m, engie : 4.5m

# # set date
# from datetime import datetime
# dt = datetime(2022,2,28)


# ARENH 





# Core rules penalties

# def rules penalties : each time the balance is not respected
def penalty_amount(diff_power_mwh, penalty_price_j1):
    return -abs(diff_power_mwh) * penalty_price_j1





def create_table(players):
    df = pd.DataFrame(columns=["player","Name","type","hour", "p_min","p_max","mwh_cost"])
    sr = []
    for p in players:

        dft = p.j_prev
        dft["player"]  = p.name
        sr.append(dft)

    df = pd.concat(sr, ignore_index=True, axis=0)

    df.sort_values(['hour', 'mwh_cost', 'p_max'], ascending=[True, True, True], inplace=True)
    return df

 



# # simu for j-1
# # dt to increment heree

# simu_w.generate_j(dt)

# simu_p.generate_j(dt.day, dt.month, simu_w.Tmean)


# simu_p.player_simu_repartition(
#     proportion_list=[p.client_proportion for p in players],
#     names = [p.name for p in players],
# )

# simu_p.j_curve.to_csv(path+"/conso_"+dt.isoformat()+".csv", sep=";",index=False)

# simu_w.get_df_j_curve().to_csv(path+"/meteo_"+dt.isoformat()+".csv", sep=";",index=False)

# # step get enr curves
# for p in players:
#     p.get_p(simu_w.j_curve)


# # creation table
# df_power = create_table(players)
def create_df_power(df_power, h ): 
    
    d = df_power[df_power.hour == h].copy()
    d.loc[:,"cumsum_p_max"] = d.loc[:,"p_max"].cumsum()
    d.reset_index(inplace=True)
    return d


##pause + timing
# # fixing 
# sum_conso = simu_p.j_curve.Consommation
# j_prev_fixing = {}
# j_prev_power_fixed = {}

# # df_power = create_df_power(players)
# for j, i in enumerate(sum_conso):
#     df_power_j = create_df_power(df_power, j)
    
#     id_list = df_power_j[df_power_j.cumsum_p_max < i].index.tolist()
#     id_list.append(max(id_list)+1)
#     j_prev_power_fixed[j] = df_power_j.iloc[id_list,:]

# j_prev_fixing = [j.mwh_cost.max() for i,j in j_prev_power_fixed.items()]

# d_fixing = pd.DataFrame(j_prev_fixing,columns=["mwh_price"])
# d_fixing["hour"] = np.arange(len(d_fixing))
# d_fixing["buy_mwh"] = 0
# for p in players:
#     d_fixing.to_csv(path+"/"+p.name+"/"+p.name+"_j_cmd.csv",sep=";", index=False)

# EOD 1 + enr achat
# for p in players:
#     p.read_j_prev(path+"/"+p.name+"/"+p.name+"_j_prev.csv")

# for p in players:
#     p.read_j_market_cmd(path+"/"+p.name+"/"+p.name+"_j_cmd.csv", d_fixing)






def bank_j(player, dt):
    a = player.j_prev_cmd.loc[:,("mwh_cost", 'hour', "p")]
    a.loc[:,"amount"] = -a.loc[:,"mwh_cost"] * a.loc[:,"p"]
    player.score.add_score(amount = a["amount"], date = dt.isoformat(), cause = "pay power J-1")

def get_paid_by_client(player, j_curve, dt):
    b = j_curve[player.name] * player.client_price_mwh 
    player.score.add_score(amount = b, date = dt.isoformat(), cause = "get pay power J-1")
    

def sales_h(df_power, d_fixing, players, dt, arenh_price, arenh_proportion):
    

    df_power = df_power.merge(d_fixing[["hour", "mwh_price"]], how="left", on="hour")

    df_temp = pd.DataFrame(columns= ["hour", "buy_mwh", "player"])
    sr=[]
    for p in players:
        aa = p.j_market_cmd.loc[:,("mwh_price", "hour", "buy_mwh")]
        aa["player"] = p.name
        sr.append(aa)
    df_temp = pd.concat(sr, axis=0, ignore_index=True)
    d_merge = pd.DataFrame({"buy_mwh":df_temp.groupby("hour").buy_mwh.sum()})
    df_power = df_power.merge(d_merge, how="left", on= ["hour"])

    df_power["p_left"] = df_power.p_max - df_power.p
    df_power["cumsum"] = df_power.groupby('hour')['p_left'].transform(pd.Series.cumsum)
    df_power["balance"] = df_power["cumsum"] - df_power["buy_mwh"]
    

    df_power["diff"] = df_power.balance.diff()
    df_power["p_sale"] = np.where(df_power.balance < 0, df_power.loc[df_power.index]["diff"], -df_power.loc[df_power.index]["balance"]+df_power.loc[df_power.index]["diff"])
    df_power = df_power.fillna(0)
    df_power.loc[df_power.p_sale < 0, "p_sale"] = 0.0

    df_power["amount_sales"] = df_power.p_sale*df_power.mwh_price
    df_power["amount_sales_cost"] = -df_power.p_sale*df_power.mwh_cost

    enr_valo = df_power[ (df_power["p_left"] > 0) & (df_power.type.isin(["WindPlant", "SolarPlant"])) ].copy()
    enr_valo["enr_amount_sales"] = enr_valo[enr_valo.type=="SolarPlant"].p_left*MWH_SOLAR_PRICE
    enr_valo["enr_amount_sales"] = enr_valo[enr_valo.type=="WindPlant"].p_left*MWH_WIND_PRICE

    enr_valo = enr_valo.fillna(0)

    arenh_valo = df_power[(df_power.player == "ndf") & (df_power.type == "NuclearPlant") & (df_power.amount_sales >0)].copy()
    arenh_valo["arenh_amount"] = df_power.p_sale*(df_power.mwh_price - arenh_price)*arenh_proportion
    arenh = float(arenh_valo["arenh_amount"].sum())

    ndf_player = next(x for x in players if x.name == "ndf")
    ndf_player.score.add_score(
                    amount = -arenh,
                    date = dt.isoformat(),
                    cause = "ARENH tax"
                )

    for p in players:
        p.score.add_score(
            amount = df_power.groupby("player").amount_sales.sum()[p.name],
            date = dt.isoformat(),
            cause = "energy sales amount J-1"
        )
        p.score.add_score(
            amount = df_power.groupby("player").amount_sales_cost.sum()[p.name],
            date = dt.isoformat(),
            cause = "energy sales cost producer amount J-1"
        )

        if not p.name == "ndf":
            score_enr = enr_valo.groupby("player").enr_amount_sales.sum()
            if p.name in score_enr.index:
                p.score.add_score(
                    amount = score_enr[p.name],
                    date = dt.isoformat(),
                    cause = "EnR sales to NDF"
                )
                ndf_player.score.add_score(
                    amount = -score_enr[p.name],
                    date = dt.isoformat(),
                    cause = "EnR buy obligation from "+ p.name
                )
            p.score.add_score(
                amount = arenh/(len(players)-1),
                date = dt.isoformat(),
                cause = "ARENH gain from NDF"
            )
                
            


def compute_balance(players, df_power,dt, penalty_price,simu_p):
    for p in players:
        a = p.j_prev_cmd[["Name","hour","p"]].rename(columns={"p":"p_"+p.name})
        a["player"] = p.name
        df_power = df_power.merge( a,on=["player","Name","hour"], how="left")
        df_power.update(df_power["p_"+p.name].rename("p"))
        df_power.drop("p_"+p.name, axis=1, inplace=True)
    
    for p in players:
        b = p.verify_j_prev(simu_p.j_curve)
        p.score.add_score(amount = penalty_amount(b["balance"], penalty_price_j1=penalty_price), date = dt.isoformat(), cause = "penalty J-1")
        get_paid_by_client(player=p,j_curve=simu_p.j_curve,dt=dt)
        bank_j(p, dt)

        p.score.add_score(amount = -float((p.j_market_cmd.mwh_price*p.j_market_cmd.buy_mwh).sum()), date = dt.isoformat(), cause = "Market MWH purchase J-1")
        # score euros
    return df_power

def read_spot(path, dd):
    path = Path(path)
    
    try:
        if not path.exists():
            raise FileNotFoundError

        dj = pd.read_csv(path, sep=";")
        if not all(item in dj.columns for item in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"] ):
            for item in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"]:
                if not item in dj.columns:
                    print(item)
            raise ValueError('Columns not all in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"]' )
    except (ValueError,FileNotFoundError):
        # j_prev_cmd = dd
        return dd

    dj[["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p"]] = dd[["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p"]].values
    dj.loc[dj.p > dj.p_max,"p"] = dj.loc[dj.p > dj.p_max,"p_max"]
    dj.loc[dj.p < dj.p_min,"p"] = dj.loc[dj.p < dj.p_min,"p_min"]
    dj.loc[dj.p < 0] = 0

    return dj

def compute_score_hour(players,transaction, transaction_price, h, spot_price, dd, dt):
    for p in players:
        for t in transaction:
            if p.name in t:
                p.score.add_score(
                    amount=-transaction_price,
                    date=dt.replace(hour=h),
                    cause="SPOT EXCHANGE TRANSACTION"
                )
        if p.name in dd.player[dd.spot_changes != 0].to_list():
            p.score.add_score(
                amount=int(abs(dd.spot_changes).sum())*spot_price,
                date=dt.replace(hour=h),
                cause="SPOT EXCHANGE"
            )

    
#     # scores :
# # le score doit se clculer a partir du df_power 
# df_power = compute_balance(players, df_power, dt)
# sales_h(df_power,sum_conso, d_fixing, players, dt)

# for p in players:
#     p.print_score("score")

# add tarification enr



# score


# correct fixing table with j_prev

# spot_price = 300
# df_real = df_power.copy()
# transaction_price = 300

# for h in range(0,24):
#     dd = df_real[df_real.hour == h]
#     res = {}
#     balance = 2

#     for p in players:
#         res = p.get_p_j(h, simu_w.j_curve[h])
#         dd.merge(res, how="left", on=["player","Name","hour"])

#     dd = dd.fillna(0.0)

 
#     sum_power = dd.power.sum()
#     balance = abs(simu_p.j_curve.Consommation[0] - sum_power)

#     transaction = []

#     dd["spot"] = 0
#     dd.to_csv(path+"/"+"spot_"+h+"h.csv")

#     def read_spot(path):
#         path = Path(path)
        
#         try:
#             if not path.exists():
#                 raise FileNotFoundError

#             dj = pd.read_csv(path, sep=";")
#             if not all(item in dj.columns for item in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"] ):
#                 for item in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"]:
#                     if not item in dj.columns:
#                         print(item)
#                 raise ValueError('Columns not all in ["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p", "spot"]' )
#         except (ValueError,FileNotFoundError):
#             self.j_prev_cmd = self.j_prev
#             return self.j_prev

#         dj[["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p"]] = dd[["player", "Name", "type", "hour", "p_min", "p_max", "mwh_cost", "p"]].values
#         dj.p[dj.p > dj.p_max] = dj.p_max[dj.p > dj.p_max]
#         dj.p[dj.p < dj.p_min] = dj.p_min[dj.p < dj.p_min]
#         dj.p[dj.p < 0] = 0

#         return dj


#     while balance < 1 :
        

#         dd = read_spot(path+"/"+"spot_"+h+"h.csv", dd)

#         dd["spot_changes"] = dd.power - dd.spot

#         transaction.append(dd.player[dd.spot_changes != 0].to_list())

#         sum_power = dd.spot.sum()
#         balance = abs(simu_p.j_curve.Consommation[0] - sum_power)


#     for p in players:

#         for t in transaction:
#             if p.name == t:
#                 p.score.add_score(
#                     amount=-transaction_price,
#                     date=dt.replace(hour=h)
#                     cause="SPOT EXCHANGE TRANSACTION"
#                 )

#         if p.name in dd.player[dd.spot_changes != 0].to_list():
#             p.score.add_score(
#                 amount=abs(dd.spot_changes).sum()*spot_price,
#                 date=dt.replace(hour=h)
#                 cause="SPOT EXCHANGE"
#             )




        







# pass

