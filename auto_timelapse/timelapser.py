import os, cv2
import shutil
import subprocess
from datetime import datetime

def get_datetime(filename):
    year = 2025
    month = int(filename[:2]) 
    day = int(filename[3:5]) 
    hour = int(filename[6:8]) 
    minute = int(filename[9:11])
    return datetime(year, month, day, hour, minute)

def duration_tuple(filenames, index, speed):
    difference = get_datetime(filenames[index + 1]) - get_datetime(filenames[index])
    return (filenames[index], difference.seconds/speed)

def make_label(filename):
    return get_datetime(filename).strftime("%m/%d, %H:%M")

def label_copy(path): 
    image = cv2.imread(path)
    font = cv2.FONT_HERSHEY_PLAIN
    pos = (10, 50)
    font_scale = 3
    color_BGR = (50, 255, 50)
    thickness = 5

    filename = path.split('/')[-1]
    image = cv2.putText(image, make_label(filename), pos, font, font_scale, color_BGR, thickness, cv2.LINE_AA)
    cv2.imwrite(f'temp/{filename}', image)

# make temp folder for labeled images
if os.path.exists('temp'):
    shutil.rmtree('temp')
os.mkdir('temp')

# copy image with label to temp with same name
source_folder = 'Q:/shroom_images_dump/images1'
filenames = sorted(os.listdir(source_folder))

for filename in filenames:
    print(f'current file: {filename}')
    label_copy(f'{source_folder}/{filename}')

# generate duration_list.txt
speed = 4000
durations = [duration_tuple(filenames, i, speed) for i in range(len(filenames) - 1)]
entries = [f"file 'temp/{entry[0]}'\nduration {entry[1]}" for entry in durations]
with open('duration_list.txt', 'w') as f:
    f.write('\n'.join(entries))

# final ffmpeg command 
framerate = 60
command_ls = ['ffmpeg', '-f', 'concat', '-i', 'duration_list.txt', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-r', str(framerate), 'output.mp4']
subprocess.run(command_ls)

# clean up
os.remove('duration_list.txt')
shutil.rmtree('temp')