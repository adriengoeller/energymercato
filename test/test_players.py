# Define client mwh_price
import pytest
from pathlib import Path
import random
from energymercato.entities.player import Player


from energymercato.usecases.usecases import (
    make_plant, 
    make_storage_plant, 
    penalty_amount, 
    create_table,
    create_df_power,
    sales_h,
    compute_balance
    )
from energymercato.entities.power import *

path = Path("test")/"tmp"

random.seed(10)

client_price = 56
penalty_price_j1 = 200
arenh_price = 31
arenh_proportion = .2

# Define players
p1 = 900
p2 = 1300
p3 = 1450

# Define power plant (inspired by Wikipedia power plant informations in France)
print("creation of plant factory...")
make_nuke_plant = make_plant(NukePlant, .1,.95,35, 3000)
make_coal_plant = make_plant(CoalPlant, .2,.9, 45, 500)
make_gas_plant = make_plant(GasPlant, .2,.9,55, 1000)
make_wind_plant = make_plant(WindPlant, 0,1,0, 0)
make_solar_plant = make_plant(SolarPlant, 0,1,0, 0)
make_water_plant = make_storage_plant(StoragePlant, 1,1,0,0,3000,20,0)
make_hydro_plant = make_plant(HydroPlant, 0,1,10, 0)

print("creation of specific plant...")
grave = make_nuke_plant(6*p1, "grave")
choo = make_nuke_plant(1*p3, "choo")
civ = make_nuke_plant(2*p3, "civ")
catt = make_nuke_plant(4*p2, "catt")
palu = make_nuke_plant(4*p2, "palu")
pen = make_nuke_plant(2*p2, "pen")
tri = make_nuke_plant(4*p1, "tri")
bug = make_nuke_plant(4*p1, "bug")
cru = make_nuke_plant(4*p1, "cru")
bla = make_nuke_plant(4*p1, "bla")
chin = make_nuke_plant(4*p1, "chin")
corde = make_coal_plant(1200, "corde")
hydro_ndf = make_hydro_plant(2000, "hydro_ndf")
fossette = make_solar_plant(12, "fossette")
belfays = make_wind_plant(20, "belfays")
marne = make_wind_plant(220, "marne")

prov = make_coal_plant(1200, "prov")
huchet = make_coal_plant(600, "huchet")
fos3 = make_gas_plant(540, "fos3")
camargue = make_solar_plant(100, "camargue")

fos = make_gas_plant(490, "fos")
golfe = make_gas_plant(435, "golfe")
mont = make_gas_plant(435, "mont")
choo2 = make_nuke_plant(1*p3, "choo2")
cvent = make_wind_plant(435, "cvent")
cvent_sol = make_solar_plant(88, "cvent_sol")
solaire_direct = make_solar_plant(1500, "solaire_direct")
hydro_ngie = make_hydro_plant(1800, "hydro_ngie")

cnr_wind = make_wind_plant(800, "cnr_wind")
cnr_solar = make_solar_plant(200, "cnr_solar")
cnr_water = make_hydro_plant(3000, "cnr_water")

huch6 = make_coal_plant(595, "huch6")
prov5 = make_coal_plant(595, "prov5")
gazel_wind = make_wind_plant(83.5, "gazel_wind")
gazel_solar = make_solar_plant(10.5, "gazel_solar")

t_wind = make_wind_plant(600, "t_wind")
t_sol = make_solar_plant(480, "t_sol")
t_hydro = make_hydro_plant(150, "t_hydro")
marcinelle = make_gas_plant(500, "marcinelle")
bayet = make_gas_plant(400, "bayet")

sw_hydro = make_hydro_plant(400, "sw_hydro")
chin2 = make_nuke_plant(3*p1, "chin2")
fos2 = make_gas_plant(490, "fos2")

ndf = Player(name="ndf",score = [0],plant_list=[
    grave,choo,civ,hydro_ndf
], client_proportion = .58, 
client_price_mwh=client_price,path=path)
ngie = Player(name="ngie",score = [0],plant_list=[
    fos, mont, golfe, hydro_ngie
], client_proportion = .15,client_price_mwh=client_price, path=path)
gazel = Player(name="gazel",score = [0],plant_list=[
        gazel_wind, gazel_solar
    ], client_price_mwh=client_price, client_proportion = .02, path=path)

players = [ndf, ngie, gazel]

total_power = sum(c.get_prod() for c in players)
total_power_enr = sum(c.get_prod(enr_only=True) for c in players)

@pytest.mark.unit_test
def test_player_init():
    assert players[1].get_prod()==3024
    assert total_power == 14380.5
    assert players[2].get_prod(enr_only=True) == 94.0
    assert players[1].get_prod(enr_only=True) == 0.0


for p in players:
    p.write_power_plant()

# set date
from datetime import datetime
dt = datetime(2022,1,15)

# Define simulation
simu_w = SimulationWeather()
simu_p = SimulationPowerConsumption(sum_p_max=(total_power-total_power_enr)*.95)
