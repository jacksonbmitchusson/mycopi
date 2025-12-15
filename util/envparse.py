import os
from re import findall
from pytz import timezone
from datetime import datetime

def last_record(envpath):
    with open(envpath, 'rb') as f: 
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        return f.readline().decode()
    
def parse_record(raw: str) -> dict:
    tokens = findall(r'([0-9]+\.[0-9]{2}|[0-9]{2})', raw)
    M, d, y, h, m, s = map(int, tokens[:6])
    date = datetime(y, M, d, h, m, s, tzinfo=timezone('America/Chicago'))
    temp, humidity, pressure = map(float, tokens[6:])
    return {
        'date': date, 
        'Temperature': temp, 
        'Humidity': humidity, 
        'Pressure': pressure
    }