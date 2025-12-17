import requests
from util.envparse import last_record, parse_record
from matplotlib import pyplot as plt
from time import sleep
from datetime import datetime, timedelta
from pytz import timezone

env_path = '/home/onaquest/server-output/environment_log.txt'

def get_timestamp():
    return datetime.now(timezone('America/Chicago')).strftime('%m-%d_%H-%M-%S')

def duty_curve(temp_delta, params): 
    min_th_diff, min_ontime, max_th_diff, max_ontime = params
    if temp_delta < min_th_diff:
        return 0
    if temp_delta > max_th_diff:
        return max_ontime
    lerp_amt = (temp_delta - min_th_diff)/(max_th_diff - min_th_diff)
    return min_ontime*(1 - lerp_amt) + max_ontime*lerp_amt
detail = 100

def turn_heater(state):
    requests.get(f'http://192.168.1.246/relay/0?turn={state}')

def debug_show_curve(params):
    x = [xi/detail for xi in range(-2*detail, 7*detail)]
    y = [duty_curve(xi, params) for xi in x]
    plt.plot(x, y)
    plt.show()

def append_log(temp_delta, ontime, cycle_seconds):
    # time, temp_delta, ontime %, ontime seconds
    timestamp = get_timestamp()
    with open(f'heater_controller/heater_log.txt', 'a') as log:
        log_string = f'{timestamp} - temp_delta: {temp_delta:.2F} deg F, ontime %: {(100*ontime):.2f}%, ontime seconds: {ontime*cycle_seconds:.2f}\n'
        log.write(log_string)
        print(log_string, flush=True)

def duty_cycle(params, target_temp, cycle_time: timedelta):
    record = parse_record(last_record(env_path))
    record_timedelta = datetime.now(timezone('America/Chicago')) - record['date']
    temp_delta = target_temp - record['Temperature']
    ontime = duty_curve(temp_delta, params)
    cycle_seconds = cycle_time.total_seconds()
    if ontime != 0:     
        append_log(temp_delta, ontime, cycle_seconds)
        turn_heater('on')
        sleep(ontime*cycle_seconds)
        turn_heater('off')
        sleep((1 - ontime)*cycle_seconds)
    else: 
        append_log(temp_delta, ontime, cycle_seconds)
        turn_heater('off')
        sleep(cycle_seconds)


params = (-1, 0.05, 2.5, 0.7)
with open('/home/onaquest/mycopi/heater_controller/target_temp') as f:
    target_temp = float(f.read())
    print(f'Target Temp: {target_temp}F', flush=True)
cycle_time = timedelta(seconds=180)

while True:
    duty_cycle(params, target_temp, cycle_time)