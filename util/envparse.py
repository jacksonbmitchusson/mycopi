import os
from re import findall
from datetime import datetime

def last_record(envpath):
    with open(envpath, 'rb') as f: 
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        return f.readline().decode()
    
def parse_record(raw: str) -> dict:
    tokens = findall(r'([0-9]+\.[0-9]{2}|[0-9]{2})', raw)
    M, d, h, m, s = map(int, tokens[:5])
    date = datetime(2025, M, d, h, m, s)
    temp, humidity, pressure = map(float, tokens[5:])
    return {
        'date': date, 
        'Temperature': temp, 
        'Humidity': humidity, 
        'Pressure': pressure
    }