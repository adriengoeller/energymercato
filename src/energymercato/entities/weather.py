# defines weather objects

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Meteo():
    wind = 0
    temperature = 0
    current_date = datetime.now()
    cloud_percent = 0
    rain_percent = 0
    