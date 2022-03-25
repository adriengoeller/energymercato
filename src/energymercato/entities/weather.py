# defines weather objects

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Meteo():
    wind:float = 0
    temperature:float = 0
    current_date:datetime = datetime.now()
    cloud_percent:float = 0
    rain_percent:float = 0
    