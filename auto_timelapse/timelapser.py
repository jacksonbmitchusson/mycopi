import os, cv2
import shutil
import subprocess
import sys
from datetime import datetime
from util import envparse, graphing

def label_copy(path): 
    image = cv2.imread(path)
    font = cv2.FONT_HERSHEY_PLAIN
    pos = (10, 50)
    font_scale = 3
    color_BGR = (50, 255, 50)
    thickness = 5

    filename = path.split('/')[-1]
    label = envparse.parse_date_string(filename).strftime("%m/%d, %H:%M")
    image = cv2.putText(image, label, pos, font, font_scale, color_BGR, thickness, cv2.LINE_AA)
    cv2.imwrite(f'{output_path}/temp/{filename}', image)

output_path = '/home/onaquest/server-output'

# make temp folder for labeled images
if os.path.exists(f'{output_path}/temp'):
    shutil.rmtree(f'{output_path}/temp')
os.mkdir(f'{output_path}/temp')

if len(sys.argv) != 4:
    print(f'Usage: {sys.argv[0]} [camera_index] [length_hours] [framerate]', flush=True)
    exit()

camera_index = int(sys.argv[1])
length_hours = float(sys.argv[2])
framerate = int(sys.argv[3])

# copy image with label to temp with same name
source_folder = f'{output_path}/images{camera_index}'
filenames = sorted(os.listdir(source_folder))

# limit images to specific date range
start, end = graphing.get_relative_range(length_hours)
print(f'start: {start}, end: {end}', flush=True)
filenames = [x for x in filenames if start <= envparse.parse_date_string(x) <= end]

for filename in filenames:
    print(f'labeling file: {filename}', flush=True)
    label_copy(f'{source_folder}/{filename}')

# create filelist.txt, a list of filenames for ffmpeg to concatenate
entries = [f"file '{output_path}/temp/{name}'\nduration {1 / framerate}" for name in filenames]
with open(f'{output_path}/filelist.txt', 'w') as f:
    f.write('\n'.join(entries))

video_name = f'{envparse.format_datetime(start)} to {envparse.format_datetime(end)}'

# final ffmpeg command 
command_ls = ['ffmpeg', 
              '-f', 'concat', 
              '-safe', '0',
              '-i', f'{output_path}/filelist.txt', 
              '-pix_fmt', 'yuv420p', 
              '-c:v', 'libx264', 
              '-crf', '32', 
              '-preset', 'ultrafast', 
              '-r', str(framerate), 
              f'{output_path}/videos{camera_index}/{video_name}.mp4']
subprocess.run(command_ls)

# clean up
os.remove(f'{output_path}/filelist.txt')
shutil.rmtree(f'{output_path}/temp')