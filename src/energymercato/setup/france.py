from energymercato.entities.power import CoalPlant, GasPlant, HydroPlant, NukePlant, SolarPlant, StoragePlant, WindPlant
from energymercato.usecases.usecases import make_plant, make_storage_plant

p1 = 900
p2 = 1300
p3 = 1450

make_nuke_plant = make_plant(NukePlant, .1,.95,35, 3000)
make_coal_plant = make_plant(CoalPlant, .2,.9, 45, 500)
make_gas_plant = make_plant(GasPlant, .2,.9,55, 1000)
make_wind_plant = make_plant(WindPlant, 0,1,0, 0)
make_solar_plant = make_plant(SolarPlant, 0,1,0, 0)
make_water_plant = make_storage_plant(StoragePlant, 0,150,0,0,60,5)
make_hydro_plant = make_plant(HydroPlant, 0,1,10, 0)

print("creation of specific plant for France")
grave = make_nuke_plant(6*p1, "grave") ; grave.mwh_cost = 37
choo = make_nuke_plant(1*p3, "choo") ; choo.mwh_cost = 39
civ = make_nuke_plant(2*p3, "civ") ; civ.mwh_cost = 49
catt = make_nuke_plant(4*p2, "catt") ; catt.mwh_cost = 57
palu = make_nuke_plant(4*p2, "palu") ; palu.mwh_cost = 40
pen = make_nuke_plant(2*p2, "pen") ; pen.mwh_cost = 51
tri = make_nuke_plant(4*p1, "tri") ; tri.mwh_cost = 62
bug = make_nuke_plant(4*p1, "bug") ; bug.mwh_cost = 64
cru = make_nuke_plant(4*p1, "cru") ; cru.mwh_cost = 2
bla = make_nuke_plant(4*p1, "bla") ; bla.mwh_cost = 55
chin = make_nuke_plant(4*p1, "chin") ; chin.mwh_cost = 42
corde = make_coal_plant(1200, "corde") ; corde.mwh_cost = 29
hydro_ndf = make_hydro_plant(2000, "hydro_ndf") ; hydro_ndf.mwh_cost = 1
fossette = make_solar_plant(12, "fossette") ; fossette.mwh_cost = 11
belfays = make_wind_plant(20, "belfays") ; belfays.mwh_cost = 7
marne = make_wind_plant(220, "marne") ; marne.mwh_cost = 3

prov = make_coal_plant(1200, "prov") ; prov.mwh_cost = 38
huchet = make_coal_plant(600, "huchet") ; huchet.mwh_cost = 35
fos3 = make_gas_plant(540, "fos3") ; fos3.mwh_cost = 128
camargue = make_solar_plant(100, "camargue") ; camargue.mwh_cost = 5

fos = make_gas_plant(490, "fos") ; fos.mwh_cost = 131
golfe = make_gas_plant(435, "golfe") ; golfe.mwh_cost = 143
mont = make_gas_plant(435, "mont") ; mont.mwh_cost = 135
choo2 = make_nuke_plant(1*p3, "choo2") ; choo2.mwh_cost = 49
cvent = make_wind_plant(435, "cvent") ; cvent.mwh_cost = 4
cvent_sol = make_solar_plant(88, "cvent_sol") ; cvent_sol.mwh_cost = 8
solaire_direct = make_solar_plant(1500, "solaire_direct") ; solaire_direct.mwh_cost = 15
hydro_ngie = make_hydro_plant(1800, "hydro_ngie") ; hydro_ngie.mwh_cost = 20

cnr_wind = make_wind_plant(800, "cnr_wind") ; cnr_wind.mwh_cost = 13
cnr_solar = make_solar_plant(200, "cnr_solar") ; cnr_solar.mwh_cost = 9
cnr_water = make_hydro_plant(3000, "cnr_water") ; cnr_water.mwh_cost = 10

huch6 = make_coal_plant(595, "huch6") ; huch6.mwh_cost = 37
prov5 = make_coal_plant(595, "prov5") ; prov5.mwh_cost = 32
gazel_wind = make_wind_plant(83.5, "gazel_wind") ; gazel_wind.mwh_cost = 14
gazel_solar = make_solar_plant(10.5, "gazel_solar") ; gazel_solar.mwh_cost = 10

t_wind = make_wind_plant(600, "t_wind") ; t_wind.mwh_cost = 12
t_sol = make_solar_plant(480, "t_sol") ; t_sol.mwh_cost = 6
t_hydro = make_hydro_plant(150, "t_hydro") ; t_hydro.mwh_cost = 4
marcinelle = make_gas_plant(500, "marcinelle") ; marcinelle.mwh_cost = 154
bayet = make_gas_plant(400, "bayet") ; bayet.mwh_cost = 138
alpiq_hydro_1 = t_hydro = make_hydro_plant(50, "alpiq_hydro_1") ; alpiq_hydro_1.mwh_cost = 30
alpiq_hydro_2 = t_hydro = make_hydro_plant(30, "alpiq_hydro_2") ; alpiq_hydro_2.mwh_cost = 33
alpiq_hydro_3 = t_hydro = make_hydro_plant(30, "alpiq_hydro_3") ; alpiq_hydro_3.mwh_cost = 34

sw_hydro = make_hydro_plant(400, "sw_hydro") ; sw_hydro.mwh_cost = 2
chin2 = make_nuke_plant(3*p1, "chin2") ; chin2.mwh_cost = 39
fos2 = make_gas_plant(490, "fos2") ; fos2.mwh_cost = 140
interco_esp = make_gas_plant(650, "interco_esp") ; interco_esp.mwh_cost = 95
interco_de = make_gas_plant(750, "interco_de") ; interco_de.mwh_cost = 85
interco_be = make_gas_plant(550, "interco_be") ; interco_be.mwh_cost = 105