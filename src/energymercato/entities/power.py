# defines powerplants objects

from dataclasses import dataclass
import random


@dataclass
class PowerPlant():
    def __init__(self, p_min=0, p_max=0, p =0 , mwh_cost = 0, start_cost = 0, name=""):
        self.p_min = p_min
        self.p_max = p_max
        self.p = p
        self.mwh_cost = mwh_cost
        self.start_cost = start_cost
        self.type:str = self.__class__.__name__
        self.name = name

@dataclass
class WindPlant(PowerPlant):
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0,name="",
    rand_level = .1):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost,name)
        self.rand_level = rand_level
    

    def get_p(self, weather, p=None):
        rl = self.rand_level
        if p:
            rl /= 2
        p = weather.wind*self.p_max*(1+self.rand_level*random.random())
        return int(p)

@dataclass
class SolarPlant(PowerPlant):
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0,name="",
    rand_level = .1):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost,name)
        self.rand_level = rand_level
    
    def get_p(self, weather, p=None):
        rl = self.rand_level
        if p:
            rl /= 2
        p = (1-.01*weather.cloud_percent)*self.p_max*(1+self.rand_level*random.random())
        return abs(int(p))

@dataclass
class HydroPlant(PowerPlant):
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0,name="",
    rand_level = .1):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost,name)
        self.rand_level = rand_level
    
    def get_p(self, weather, p=None):
        rl = self.rand_level
        if p:
            rl /= 10        
        p = (1+weather.rain_percent/100)*self.p_max*(1+self.rand_level*random.random())
        return abs(int(p))


@dataclass
class StoragePlant(PowerPlant):
    capacity_max:int = 0
    capacity_min:int = 0
    mwh_cost_in:int = 0
    start_cost_in:int = 0


@dataclass
class NukePlant(PowerPlant):
    failure = 0.05
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0,name=""):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost, name)


    def get_p(self, weather, p=None):
        if p:
            if random.randint(0,int(1/self.failure)) == int(1/self.failure):
                p = self.p_min
        else:    
            p = self.p
        return int(p)

@dataclass
class GasPlant(PowerPlant):
    failure = 0.01
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0, name=""):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost, name)

    def get_p(self, weather, p=None):
        if p:
            if random.randint(0,int(1/self.failure)) == int(1/self.failure):
                p = self.p_min
        else:    
            p = self.p
        return int(p)

@dataclass
class CoalPlant(PowerPlant):
    failure = 0.1
    def __init__(self, p_min=0, p_max=0, p=0, mwh_cost=0, start_cost=0, name=""):
        super().__init__(p_min, p_max, p, mwh_cost, start_cost, name)

    def get_p(self, weather, p=None):
        if p:
            if random.randint(0,int(1/self.failure)) == int(1/self.failure):
                p = self.p_min
        else:    
            p = self.p
        return int(p)

