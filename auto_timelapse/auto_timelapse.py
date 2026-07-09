import time
import subprocess

while True: 
    for cam in ['0']:
        command_ls = [
            'python', 
            '-m',
            'auto_timelapse.timelapser',
            cam, #index
            '12', #duration 
            '10', #framerate
        ]
    subprocess.run(command_ls)
    time.sleep(12 * 60 * 60) # 12 hour delay 
