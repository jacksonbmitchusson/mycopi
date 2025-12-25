import cv2, os
from datetime import datetime
from pytz import timezone
import asyncio
import json 
import smbus2 # type: ignore
import bme280 # type: ignore

addr = 0x77
bus = smbus2.SMBus(1)
calib_params = bme280.load_calibration_params(bus, address=addr)

cam = [cv2.VideoCapture(2, cv2.CAP_V4L2), cv2.VideoCapture(0)]

cam[0].set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam[0].set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# seconds
image_delay = 180
env_delay = 30
output_path = '/home/onaquest/server-output'

def get_timestamp():
    return datetime.now(timezone('America/Chicago')).strftime('%m-%d-%Y_%H-%M-%S')

def open_cam(index, cam_params):
    params = cam_params[index]
    video_src_index = int(os.path.realpath(params['path'])[-1]) # hacky !
    cam = cv2.VideoCapture(video_src_index, cv2.CAP_V4L2)

    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*params['fourcc']))
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, params['width'])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, params['height'])
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    msg = {
        True: 'opened successfully :)',
        False: 'failed to open :('
    }
    print(f'Cam {index} {msg[cam.isOpened()]}', flush=True)
    return cam

async def capture_images():
    with open('/home/onaquest/mycopi/data_collector/cam_params.json') as f: 
        cam_params = json.load(f) 
    cams = [open_cam(i, cam_params) for i in [0, 1]]

    def reopen(index):
        nonlocal cams
        print(f'Attemping to reopen cam {index}')
        if cams[index] is not None:
            cams[index].release()
        cams[index] = open_cam(index, cam_params)

    async def capture_image(timestamp, index):
        if cams[index] is None:
            reopen(index)
        print(f'Capturing image with camera {index}...', flush=True)
        cams[index].grab()
        ret, frame = cams[index].read()
        if ret:
            path = f'{output_path}/images{index}/{timestamp}.png'
            cv2.imwrite(path, frame)
        else:
            print('Got no image :( gonna try to reopen')
            reopen(index)

    while True:    
        await capture_image(get_timestamp(), 0)
        await asyncio.sleep(image_delay/2)
        await capture_image(get_timestamp(), 1)
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
    asyncio.create_task(capture_images())
    asyncio.create_task(capture_env())
    await asyncio.Event().wait()
    
if __name__ == '__main__':
    asyncio.run(init_capture())