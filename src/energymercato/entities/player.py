from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from numpy import identity
import pandas as pd

from energymercato.entities.power import HydroPlant, SolarPlant, WindPlant

class Score():
    def __init__(self):
        self.score = pd.DataFrame(columns=["amount","date","cause"])

    def add_score(self,amount = 0, date = "", cause = ""):
        if isinstance(amount,(int,float)):
            self.score = pd.concat(
            [self.score,
            pd.DataFrame({"amount":[amount], "date":[date], "cause":[cause]})]
            )
        else:
            self.score = pd.concat(
                [self.score,
                pd.DataFrame({"amount":amount, "date":date, "cause":cause})]
                )

    def get_score(self):
        self.score.amount.sum()

    def print_score(self, path):
        self.score.to_csv(path+"_score.csv",sep=";")

class PurePlayer():
    def __init__(self, name = "ndf", score = [0], client_proportion = 0.0, client_price_mwh=41, path="game"):
        self.name=name
        self.score=Score()
        self.client_proportion=client_proportion
        self.client_price_mwh = client_price_mwh
        self.path = path
        p = Path(path) / name
        p.mkdir(parents=True, exist_ok=True)
    def __str__(self) -> str:
        return self.name
    
    def print_score(self, path):
        self.score.print_score(self.path+"/"+self.name+"/"+self.name)


class Player(PurePlayer):
    def __init__(self, name = "ndf", score=[0], client_proportion=0, plant_list=[], client_price_mwh=41, path="game"):
        super().__init__(name, score, client_proportion, client_price_mwh,path)
        self.plant_list = plant_list
        

    def get_prod(self, enr_only = False):
        if self.plant_list:
            if enr_only:
                return sum(c.p_max for c in self.plant_list if c.type in ["WindPlant", "SolarPlant"])    
            return sum(c.p_max for c in self.plant_list)
            
        else:
            print("please fill plant_list")
            return 0

    def write_power_plant(self):
        dp = pd.DataFrame(columns=["Name","type","p_min","p_max","mwh_cost"])
        sr = []
        for pp in self.plant_list:
            sr.append(pd.Series([pp.name, pp.type, pp.p_min, pp.p_max, pp.mwh_cost], index=["Name","type","p_min","p_max","mwh_cost"]).to_frame())
        dp = pd.concat(sr, axis=1, ignore_index= True).T
        dp["p"]=None
        dp["hour"] = None
        return dp.to_csv(self.path+"/"+self.name+"/"+self.name+"_power_plant_list.csv", sep=";", index=False)

    def get_p(self, j_curve_weather):
        """
        write j_prev
        """
        dp = pd.DataFrame(columns = ["Name","type", "hour","p_min","p_max","mwh_cost"])
        sr = []
        for id,w in j_curve_weather.items():
            r = self.get_current_prev(w)
            r["hour"] = id
            sr.append(r)
        dp = pd.concat(sr, axis=0, ignore_index=True)
        self.j_prev = dp
        dp["p"] = 0
        dp.to_csv(self.path+"/"+self.name+"/"+self.name+"_j_prev.csv",sep=";", index=False)

    def get_p_j(self, hour, weather):
        a = self.j_prev_cmd[self.j_prev_cmd.hour == hour].copy()
        hist = {"power": [], "Name":[]}
        for name,power in zip(a.Name.to_list(), a.p.to_list()):
            if not power:
                power=0
            current_plant = self.find_plant_in_list(name)
            hist["power"].append(current_plant.get_p(weather,power))
            hist["Name"].append(name)
        out = pd.DataFrame(hist)
        out["hour"] = hour
        out["player"] = self.name
        return out
        

    def find_plant_in_list(self, name):
        return next(x for x in self.plant_list if x.name == name )

    def get_current_prev(self, weather):
        dp = pd.DataFrame(columns = ["Name","type","p_min","p_max","mwh_cost"])
        sr = []
        for pp in self.plant_list: #[i for i in self.plant_list if type(i) in [WindPlant,SolarPlant,HydroPlant]]:
            v = pp.get_p(weather)
            if pp.type in ["HydroPlant", "WindPlant", "SolarPlant"]:
                sr.append(pd.Series([pp.name,pp.type,pp.p_min,v , pp.mwh_cost], index=["Name","type","p_min","p_max","mwh_cost"]))
            else:
                sr.append(pd.Series([pp.name,pp.type,pp.p_min, pp.p_max , pp.mwh_cost], index=["Name","type","p_min","p_max","mwh_cost"]))
            dp = pd.concat(sr, axis=1, ignore_index= True).T
        return dp

    def read_j_prev(self, path):
        path = Path(path)
        
        try:
            if not path.exists():
                raise FileNotFoundError

            dj = pd.read_csv(path, sep=";")
            if not all(item in dj.columns for item in ['hour','Name','type', 'p_min', 'p_max', 'mwh_cost', 'p'] ):
                for item in ['hour','Name','type', 'p_min', 'p_max', 'cost', 'mwh_cost', 'p']:
                    if not item in dj.columns:
                        print(item)
                raise ValueError("Columns not all in ['hour', 'Name','type', 'p_min', 'p_max', 'mwh_cost', 'p']" )
        except (ValueError,FileNotFoundError):
            self.j_prev_cmd = self.j_prev
            return self.j_prev

        dj[['Name', 'p_min', 'p_max', 'mwh_cost']] = self.j_prev[['Name', 'p_min', 'p_max', 'mwh_cost']].values
        dj = self.cut_p_prev(dj)
        dj.fillna(0, inplace=True)
        self.j_prev_cmd = dj
        return dj


    def read_j_market_cmd(self, path, j_prev_fixing):
        path = Path(path)
        
        try:
            if not path.exists():
                raise FileNotFoundError

            dj = pd.read_csv(path, sep=";")
            if not all(item in dj.columns for item in ["mwh_price","hour","buy_mwh"] ):
                for item in ["mwh_price","hour","buy_mwh"]:
                    if not item in dj.columns:
                        print(item)
                raise ValueError("Columns not all in 'mwh_price','hour'','buy_mwh'" )
        except (ValueError,FileNotFoundError):
            
            self.j_market_cmd = j_prev_fixing
            return j_prev_fixing

        dj[['mwh_price','hour']] = j_prev_fixing[['mwh_price','hour']].values
        dj = self.cut_p_market(dj)
        dj.fillna(0, inplace=True)
        self.j_market_cmd = dj
        return dj

    @staticmethod
    def make_j_prev_from_power_plant_prev(dj):
        return dj.groupby('hour')['p'].sum()


    def verify_j_prev(self, j_curve):
        check_df = self.make_j_prev_from_power_plant_prev(self.j_prev_cmd)
        out = self.j_market_cmd
        out["conso"] = -j_curve[self.name]
        out["j_prev"] = check_df
        out.fillna(0, inplace=True)
        out["balance"] = out[["conso","j_prev","buy_mwh"]].sum(axis=1)
        return out

    @staticmethod
    def cut_p_prev(dj):
        dj.loc[dj.p > dj.p_max,"p"] = dj.p_max[dj.p > dj.p_max]
        dj.loc[dj.p < dj.p_min,"p"] = dj.p_min[dj.p < dj.p_min]
        dj.loc[dj.p < 0,"p"] = 0
        return dj

    @staticmethod
    def cut_p_market(dj):
        dj.loc[dj.buy_mwh < 0,"buy_mwh"] = 0
        return dj

