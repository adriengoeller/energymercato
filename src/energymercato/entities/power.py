# defines powerplants objects

from dataclasses import dataclass
import random


@dataclass
class PowerPlant():
    p_min = 0
    p_max = 0
    p = 0
    mwh_cost = 0
    start_cost = 0

@dataclass
class WindPlant(PowerPlant):
    # wind_power_coef = 5
    rand_level = .1

    @property
    def p(self, weather):
        self.p = weather.wind*self.p_max*(1+self.rand_level*random.random())
        

@dataclass
class SolarPlant(PowerPlant):
    rand_level = .1

    @property
    def p(self, weather):
        self.p = weather.wind*self.p_max*(1+self.rand_level*random.random())
    


@dataclass
class StoragePlant(PowerPlant):
    capacity_max = 0
    capacity_min = 0
    mwh_cost_in = 0
    start_cost_in = 0


@dataclass
class NukePlant(PowerPlant):
    pass

@dataclass
class GazPlant(PowerPlant):
    pass

@dataclass
class CoalPlant(PowerPlant):
    pass


