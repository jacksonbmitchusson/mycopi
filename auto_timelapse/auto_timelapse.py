import asyncio
import subprocess

async def create_videos():
    while True: 
        command_ls = [
            'python', 
            '-m',
            'auto_timelapse.timelapser',
            '0', #index
            '12', #duration 
            '10', #framerate
        ]
        subprocess.run(command_ls)
        asyncio.sleep(12 * 60 * 60) # 12 hour delay 

async def init_capture():
    asyncio.create_task(create_videos())
    await asyncio.Event().wait()
    
if __name__ == '__main__':
    asyncio.run(init_capture())