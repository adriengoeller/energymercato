from datetime import datetime, timedelta
import pickle
import random
from time import sleep
from typing import Tuple

import numpy as np
import pandas as pd
from energymercato.entities.player import Player
from energymercato.setup.france import *
from energymercato.usecases.simulation import SimulationPowerConsumption, SimulationWeather
from pathlib import Path

from energymercato.usecases.usecases import compute_balance, compute_score_hour, create_df_power, create_table, read_spot, sales_h


def print_style(*args):
    print("="*80)
    print(*args)

class RealTimeSetup():
    def __init__(self, spot_setup, spot_price = 300, transaction_price = 300,h = -1):
        self.df_real= spot_setup.df_power.copy()
        self.spot_price=spot_price
        self.transaction_price=transaction_price
        self.h=h
        self.spot_setup = spot_setup
        
        print_style("ready for next phase")


    def start_spot(self):
        # Begining of 1/24 game round 
        self.h +=1
        print("="*80+f"\n Welcome in the SPOT Market of day {self.spot_setup.dt.strftime('%Y-%m-%d')} at {self.h}h !")

        self.df_spot = self.df_real[self.df_real.hour == self.h]
        res = {}
        self.balance = 2

        sr=[]
        for p in self.spot_setup.players:
            res = p.get_p_j(self.h, self.spot_setup.simu_w.j_curve[self.h])
            sr.append(res)
            
        self.df_spot = self.df_spot.merge(pd.concat(sr,ignore_index=True), how="left", on=["player","Name","hour"])

        self.df_spot = self.df_spot.fillna(0.0)

        sum_power = self.df_spot.power.sum()
        conso_h = self.spot_setup.simu_p.j_curve.Consommation[self.h]
        self.balance = abs(conso_h - sum_power)

        self.transaction = []

        self.df_spot["spot"] = 0
        self.df_spot.to_csv(self.spot_setup.path+"/"+"spot_"+str(self.h)+"h.csv", sep=";")

        print_style(f"Real consumption = {conso_h}\nReal Production = {sum_power}\nBalance = {self.balance}")
        print_style("Go to spot file and fill spot column with adjustment to reach balance = 0")

        print_style("Ready for balancing\n", f"Difference of Real Consumption with SPOT is {self.balance}")

    def wait_for_adjustment(self, time_minutes=2, repeat=5):
        print_style(f"You have {time_minutes} x {repeat} minutes before blackout")
        for i in range(1,5):
            print("Tic, Toc... Blackout is coming")
            sleep(60*time_minutes)
            try:
                self.read_spot()
            except Exception as e:
                pass
            if abs(self.balance) < 1:
                break
            else:
                print_style(f"Balance left : {self.balance}")
        if abs(self.balance) < 1:
            print_style("Ready for computing scores")
        else:
            print_style("System has blacked out")
            print("-"*80)
            print_style("Game Over")



    def read_spot(self):
        df_spot = read_spot(self.spot_setup.path+"/"+"spot_"+str(self.h)+"h.csv", self.df_spot.copy())
        df_spot["spot_changes"] = df_spot.power - df_spot.spot
        sum_power = self.df_spot.spot.sum()
        balance = abs(self.spot_setup.simu_p.j_curve.Consommation[self.h] - sum_power)
        
        print_style(f"Balance was {self.balance}. It is now {balance}")
        
        if abs(balance) < 1:
            self.df_spot = df_spot
            self.balance = balance
            self.transaction.append(self.df_spot.player[self.df_spot.spot_changes != 0].to_list())
            print_style("Balance is adjusted !")

        else:
            print_style("Balance is not adjusted")

        

    def compute_score(self):
        compute_score_hour(self.spot_setup.players,self.transaction, self.transaction_price, self.h, self.spot_price, self.df_spot, self.spot_setup.dt)
        print("="*80+f"\n End of SPOT for hour {self.h}")
        print("Please start for next hour"+"\n"+"="*80)

        if self.h == 24:
            print("end of day : please go to next j-1")
            print("\n"+"#"*80+"\n"+"="*80)

def save(obj_save_tuple, path_file_pkl):
    with open(path_file_pkl, 'wb') as outp:
        pickle.dump(obj_save_tuple, outp, pickle.HIGHEST_PROTOCOL)

def load(path_file_pkl) -> Tuple:
    with open(path_file_pkl, 'wb') as outp:
        return pickle.dump(path_file_pkl, outp, pickle.HIGHEST_PROTOCOL)


class SpotSetup():

    def __init__(self, path, solo=True, client_price=60,penalty_price_j1 = 300, arenh_price = 50, arenh_proportion = .25):

        if Path(path).parent.exists():
            print("path ",str(Path(path).parent), "is existing ?",Path(path).parent.exists())
        else:
            raise ValueError("Path is not existing, quitting...")
        if solo:
            random.seed(10)
        self.solo=solo
        self.client_price=client_price 
        self.path=path
        self.penalty_price_j1=penalty_price_j1
        self.arenh_price=arenh_price
        self.arenh_proportion=arenh_proportion
        print_style("Initialization of SPOT Market with parameters :")
        print_style(f"- legal client price : {client_price}€\n"
                    +f"penalty price for J-1 : {penalty_price_j1}€/MWh\n"
                    +f"ARENH Price and volume proportion: {arenh_price} / {arenh_proportion}")

    def generate_players(self):
        solo=self.solo
        client_price=self.client_price
        path=self.path

        print("defining players...")
        if solo : 
            print("solo mode !")
            ndf = Player(name="ndf",score = [0],plant_list=[
                grave,hydro_ndf
            ], client_proportion = .58, 
            client_price_mwh=client_price,path=path)
            ngie = Player(name="ngie",score = [0],plant_list=[
                fos
            ], client_proportion = .15,client_price_mwh=client_price, path=path)
            gazel = Player(name="gazel",score = [0],plant_list=[
                    gazel_wind, gazel_solar
                ], client_price_mwh=client_price, client_proportion = .02, path=path)
            self.players = [ndf, ngie, gazel,]
        else :
            ndf = Player(name="ndf",score = [0],plant_list=[
                grave,choo,civ, catt, palu, pen,
                tri, bug,cru,bla,chin, corde,
                hydro_ndf,fossette,belfays,marne
            ], client_proportion = .5,client_price_mwh=client_price, path=path)
            ngie = Player(name="ngie",score = [0],plant_list=[
                fos, mont, golfe,choo2, cvent, 
                cvent_sol, solaire_direct, hydro_ngie
            ], client_proportion = .15,client_price_mwh=client_price, path=path)
            gazel = Player(name="gazel",score = [0],plant_list=[
                huch6,prov5, gazel_wind, gazel_solar
            ], client_proportion = .05, client_price_mwh=client_price,path=path)

            cnr = Player(name = "cnr", score = [0],plant_list=[
                cnr_wind,cnr_solar,cnr_water
            ], client_proportion=0.1, client_price_mwh=client_price, path=path)


            totalnrj = Player(name = "totalnrj",score = [0],plant_list=[
                t_sol,t_wind,t_hydro, marcinelle, bayet , fos3, camargue 
            ], client_proportion = .15, client_price_mwh=client_price, path=path)


            alpiq = Player(name="alpiq", plant_list=[sw_hydro, fos2, chin2],client_proportion = .05, client_price_mwh=client_price, path=path)

            self.players = [
                ndf, ngie, gazel, cnr, alpiq, totalnrj, 
            ]

        self.total_power = sum(c.get_prod() for c in self.players)
        self.total_power_enr = sum(c.get_prod(enr_only=True) for c in self.players)

        for p in self.players:
            p.write_power_plant()

    def simulate_game_data(self, dt = datetime(2022,1,15), ):
        print(f"Power consumption is taken on Pmax = {(self.total_power-self.total_power_enr)*.95} = self.total_power-self.total_power_enr)*.95")
        # Define simulation
        self.dt = dt
        self.simu_w = SimulationWeather()
        self.simu_p = SimulationPowerConsumption(sum_p_max=(self.total_power-self.total_power_enr)*.95)

    def change_round_day(self):
        # Beginning of game round here
        # dt increment
        self.dt += timedelta(days=1)
        # simulation

        self.simu_w.generate_j(self.dt)

        self.simu_p.generate_j(self.dt.day, self.dt.month, self.simu_w.Tmean)

        self.simu_p.player_simu_repartition(
            proportion_list=[p.client_proportion for p in self.players],
            names = [p.name for p in self.players],
        )

        self.simu_p.j_curve.to_csv(self.path+"/conso_"+self.dt.isoformat()+".csv", sep=";",index=False)

        self.simu_w.get_df_j_curve().to_csv(self.path+"/meteo_"+self.dt.isoformat()+".csv", sep=";",index=False)

        # step get enr curves
        for p in self.players:
            p.get_p(self.simu_w.j_curve)

        # creation table
        self.df_power_0 = create_table(self.players)
        self.df_power = self.df_power_0.copy()

    def fix_market(self):
        # fixing 
        sum_conso = self.simu_p.j_curve.Consommation
        j_prev_fixing = {}
        j_prev_power_fixed = {}

        # df_power = create_df_power(players)
        for j, i in enumerate(sum_conso):
            df_power_j = create_df_power(self.df_power, j)
            
            id_list = df_power_j[df_power_j.cumsum_p_max < i].index.tolist()
            if max(id_list) < len(df_power_j)-1:
                id_list.append(max(id_list)+1)
            j_prev_power_fixed[j] = df_power_j.iloc[id_list,:]

        j_prev_fixing = [j.mwh_cost.max() for i,j in j_prev_power_fixed.items()]

        self.d_fixing = pd.DataFrame(j_prev_fixing,columns=["mwh_price"])
        self.d_fixing["hour"] = np.arange(len(self.d_fixing))
        self.d_fixing["buy_mwh"] = 0
        for p in self.players:
            self.d_fixing.to_csv(self.path+"/"+p.name+"/"+p.name+"_j_cmd.csv",sep=";", index=False)
        print_style("waiting for filling...")

    def read_prev_from_players(self):
        
        for p in self.players:
            p.read_j_prev(self.path+"/"+p.name+"/"+p.name+"_j_prev.csv")
        print_style("ok for production orders")
        for p in self.players:
            p.read_j_market_cmd(self.path+"/"+p.name+"/"+p.name+"_j_cmd.csv", self.d_fixing)
        print_style("ok for market orders")

    def compute_scores(self):
        # scores :
        self.df_power = compute_balance(self.players, self.df_power, self.dt, self.penalty_price_j1,self.simu_p)
        sales_h(self.df_power, self.d_fixing, self.players, self.dt,self.arenh_price, self.arenh_proportion)

    def get_scores(self):
        for p in self.players:
            p.print_score("score")