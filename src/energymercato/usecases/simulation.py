

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
import random
from typing import Dict
import pandas as pd
import numpy as np
import copy

from energymercato.entities.weather import Meteo


meteo_temp = {
    1:0,
    2:5,
    3:10,
    4:15,
    5:20,
    6:25,
    7:30,
    8:30,
    9:20,
    10:15,
    11:10,
    12:5
}


class SimulationPowerConsumption():
    def __init__(self, rand_level = .05, peak = .9, sum_p_max = 125000) -> None:
        self.peak = peak
        self.sum_p_max = sum_p_max
        self.rand_level = rand_level
        self.month = 2
        df = pd.read_csv("src/energymercato//data/power_data.csv", sep=";")
        df = df.dropna()
        df['datetime'] = df['Date'] + " " + df['Heures']
        df['datetime'] = pd.to_datetime(df['datetime'])
        data_p_max = df.Consommation.max()
        df['Consommation'] = df['Consommation'] * self.sum_p_max*self.peak / data_p_max
        self.df = df

    def generate_j(self, day=27, month=2, weather_temp = 0):
        self.month = month
        dt = datetime(2019,month,day)
        datelist = pd.date_range(dt, dt+timedelta(1), periods=25).tolist()
        datelist = datelist[:-1]
        dd = self.df[["datetime", "Consommation"]]
        ddd = dd[dd["datetime"].isin(datelist)].reset_index()
        ddd.Consommation = ddd.Consommation + np.ones_like(ddd.Consommation) * 1000 * (meteo_temp[self.month] - weather_temp) # 1GW per degree
        ddd.Consommation = ddd.Consommation.astype(int)
        self.j_curve = ddd


    def get_current_j(self, id, real_time=True):
        if real_time:
            level = 0
        current_power = self.j_curve.drop(columns=['datetime','Consommation']).loc[id,:]
        current_power = current_power *(1+self.rand_level*level*(2*random.random()-1))
    
    def player_simu_repartition(self,proportion_list= [0.1,.6,.3], names=["ngi","ndf", "cnr"]):
        prop_list = self.get_proportion_random(proportion_list)
        for i,n in zip(prop_list,names):
            self.j_curve[n] = (self.j_curve.Consommation*i).astype(int)

    @staticmethod
    def get_proportion_random(proportion_list= [.1,.6,.3]):
        proportion_list = proportion_list
        a = np.array(proportion_list[:-1]) *(.8+.4*(np.random.random(len(proportion_list)-1)-.4))
        proportion_list = a.tolist()
        proportion_list.append(1-sum(proportion_list))

        return proportion_list

    




@dataclass
class SimulationWeather():
    Tmean:float = 0
    j_curve:Dict = field(default_factory=lambda: {})

    def generate_j(self,dt):
        rT = 6 * random.random() -3
        amplitude_T = 5+ 15 * random.random() -10
        Tmax = meteo_temp[int(dt.month)] + rT + amplitude_T/2
        Tmin = meteo_temp[int(dt.month)] - rT - amplitude_T/2
        self.Tmean = (Tmax-Tmin)/2
        if Tmax > 45:
            Tmax = 45
        m = Meteo()

        cp = 90*random.random() + 10
        rain_today = 10*random.random()
        if rain_today > 7:
            rp = 100*random.random()
        else:
            rp = 0

        wind = np.random.poisson(3)* random.random()+1 
 
        meteo_dict = {}

        df = pd.DataFrame(columns=["wind","temperature","rain_percent","cloud_percent"])

        for i in range(24):
            a = random.randint(-1,2)
            b = random.randint(-2,2)
            m.temperature = (Tmax-Tmin)*(math.cos(2*math.pi/(24+b)*(i-14+a))+1)/2 +Tmin
            if rp > 100:
                rp =100
            m.rain_percent = rp
            w = wind + random.gauss(0,.8)
            if w < 0:
                w = 0
            m.wind = w
            c = abs(cp *(1+random.gauss(0,.2)))
            if c < 0:
                c = 0
            elif c > 100:
                c = 100
            else:
                pass
            
            if i<18 and i>8:
                # print(c)
                m.cloud_percent = c
            else: 
                # print(i)
                m.cloud_percent = 100
            # print(m)

            meteo_dict[i] = copy.copy(m)
        self.j_curve = meteo_dict

    def get_df_j_curve(self):
        return pd.DataFrame([i for i in self.j_curve.values()])

    def get_current(self,id_hour, real_time=True):

        return self.j_curve[id_hour]

    

    


