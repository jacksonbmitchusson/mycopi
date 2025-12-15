import cv2
from datetime import datetime
from pytz import timezone
import asyncio
import smbus2 # type: ignore
import bme280 # type: ignore

addr = 0x77
bus = smbus2.SMBus(1)
calib_params = bme280.load_calibration_params(bus, address=addr)

GSTREAMER_PIPELINE = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=1920, height=1080, pixelformat=YUYV, framerate=5/1 ! "
    "videoconvert ! video/x-raw, format=BGR ! appsink"
)

cam = [cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER), cv2.VideoCapture(2)]

# seconds
image_delay = 180
env_delay = 30
output_path = '/home/onaquest/server-output'

def get_timestamp():
    return datetime.now(timezone('America/Chicago')).strftime('%m-%d-%Y_%H-%M-%S')

def capture_image(timestamp, id):
    print(f'Capturing image with camera {id}...', flush=True)
    ret, frame = cam[id].read()
    if ret:
        path = f'{output_path}/images{id}/{timestamp}.png'
        cv2.imwrite(path, frame)

async def capture_images():
    while True:    
        capture_image(get_timestamp(), 0)
        await asyncio.sleep(image_delay/2)
        capture_image(get_timestamp(), 1)
        await asyncio.sleep(image_delay/2)

async def capture_env():
    while True:
        print(f'Capturing env...', flush=True)
        data = bme280.sample(bus, addr)
        t = (data.temperature * 9/5) + 32
        h = data.humidity
        p = data.pressure
        record_str = f'{get_timestamp()} - {t:05.2f}°F {h:05.2f}% {p:05.2f} hPa'

        with open(f'{output_path}/environment_log.txt', 'a') as log:
            log.write('\n' + record_str)

        await asyncio.sleep(env_delay)
        
async def init_capture():
    actual_width = cam[0].get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cam[0].get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(f"Requested resolution: 1920x1080")
    print(f"Actual resolution set: {actual_width}x{actual_height}")

    asyncio.create_task(capture_images())
    asyncio.create_task(capture_env())
    await asyncio.Event().wait()
    
if __name__ == '__main__':
    asyncio.run(init_capture())