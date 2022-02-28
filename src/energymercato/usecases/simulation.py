

from dataclasses import dataclass
from datetime import datetime
import math
import random
import pandas as pd
import numpy as np

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
    def __init__(self, rand_level = .05) -> None:
        self.rand_level = rand_level
        self.month = 2
        df = pd.read_csv("./data/power_data.csv", sep=";")
        df = df.dropna()
        df['datetime'] = df['Date'] + " " + df['Heures']
        df['datetime'] = pd.to_datetime(df['datetime'])

    def make_j(self, day=27, month=2, weather_temp = 0):
        self.month = month
        dt = datetime(2019,month,day)
        datelist = pd.date_range(dt, dt+datetime.timedelta(1), periods=25).tolist()
        datelist = datelist[:-1]
        dd = self.df[["datetime", "Consommation"]]
        ddd = dd[dd["datetime"].isin(datelist)].reset_index()
        self.j_curve = ddd + 1000 * (meteo_temp[self.month] - weather_temp) # 1GW per degree

    def get_current_j(self, id):
        current_power = self.j_curve["Consommation"][id]
        current_power = current_power *(1+self.rand_level*random.random())
    
@dataclass
class SimulationWeather():
    wind = 0
    temperature =0
    cloud_percent = 0
    rain_percent = 0
    j_curve = {}



    def generate_J(self,dt):
        rT = 6 * random.random() -3
        amplitude_T = 5+ 15 * random.random() -10
        Tmax = meteo_temp[int(dt.month)] + rT + amplitude_T/2
        Tmin = meteo_temp[int(dt.month)] - rT - amplitude_T/2
        if Tmax > 45:
            Tmax = 45
        m = Meteo()

        cp = 80*random.random() + 20
        rain_today = 10*random.random()
        if rain_today > 7:
            rp = 100*random.random()
        else:
            rp = 0

        wind = np.random.poisson(3)* random.random()+1 
 
        meteo_dict = {}

        for i in range(24):
            a = random.randint(-1,2)
            b = random.randint(-2,2)
            m.temperature = (Tmax-Tmin)*(math.cos(2*math.pi/(24+b)*(i-14+a))+1)/2 +Tmin
            m.rain_percent = rp
            w = wind + random.gauss(0,.8)
            if w < 0:
                w = 0
            m.wind = w
            c = abs(cp *(1+random.gauss(0,20)))
            m.cloud_percent = c

            meteo_dict[i] = m
        self.j_curve = meteo_dict

    def get_current(self,id_hour):
        return self.j_curve[id_hour]

    


