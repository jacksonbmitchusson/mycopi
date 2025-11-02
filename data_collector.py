from cv2 import VideoCapture, imwrite
from datetime import datetime
from pytz import timezone
import time
import smbus2 # type: ignore
import bme280 # type: ignore

# DATA GATHER
addr = 0x77
bus = smbus2.SMBus(1)
calib_params = bme280.load_calibration_params(bus, address=addr)
cam = [VideoCapture(0), VideoCapture(2)]

# seconds
delay = 120
output_path = '/home/onaquest/server-output'

def capture_data():
    while True:
        print('logginnggg')
        timestamp = datetime.now(timezone('America/Chicago')).strftime('%m-%d_%H-%M')
        capture_temphumid(timestamp)
        capture_image(timestamp, 0)
        time.sleep(delay/2)
        capture_image(timestamp, 1)
        time.sleep(delay/2)

def capture_temphumid(timestamp):
    data = bme280.sample(bus, addr)
    t = (data.temperature * 9/5) + 32
    h = data.humidity
    p = data.pressure
    record_str = f'{timestamp} - {t:05.2f}°F {h:05.2f}% {p:05.2f} hPa'

    with open(f'{output_path}/environment_log.txt', 'a') as log:
        log.write('\n' + record_str)

def capture_image(timestamp, id):
    ret, frame = cam[id].read()
    if ret:
        path = f'{output_path}/images{id}/{timestamp}.png'
        imwrite(path, frame)