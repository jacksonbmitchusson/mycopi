import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from datetime import datetime, timedelta
from pytz import timezone
from re import findall
from collections import defaultdict
from io import BytesIO
from util import envparse

# inputs: date range, which data, other settings

def datestr(date):
    return date.strftime("%m/%d, %H:%M")

def records_to_lists(records): 
    lists = defaultdict(list)
    for record in records:
        for k, v in record.items():
            lists[k].append(v)
    return lists

def parse_data(path, range):
    records = ...
    with open(path) as f:
        raw = [x for x in f.read().split('\n') if not x.isspace() and x != ''] # remove whitespace/empty records
        records = [envparse.parse_record(raw_record) for raw_record in raw]
    start, end = range
    ranged_records = [record for record in records if start <= record['date'] <= end]
    return records_to_lists(ranged_records)

def get_relative_range(hours_difference):
    end = datetime.now(timezone('America/Chicago'))
    start = end - timedelta(hours=hours_difference)    
    return (start, end)

def rolling_avg(data, window):
    averages = []
    for i in range(len(data)): 
        chunk = data[max(0, i - window + 1):i+1]
        averages.append(sum(chunk)/len(chunk))

def make_graph(path, range, selection, width=720, height=480, dpi=200): 
    env_data = parse_data(path, range)
    fig, ax = plt.subplots(figsize=(6, 4))
    try:
        ax.grid()
        ax.margins(x=0)
        ax.plot(env_data['date'], env_data[selection])
        if(selection == 'Temperature'):
            ax.set_ylim(68, 78)
            ax.yaxis.set_major_locator(MultipleLocator(1))
            with open('/home/onaquest/mycopi/heater_controller/target_temp') as f:
                target_temp = float(f.read())
            ax.plot(env_data['date'], [target_temp for _ in env_data['date']], color='red')    
        if(selection == 'Humidity'):
            ax.set_ylim(50, 100)
            ax.yaxis.set_major_locator(MultipleLocator(5))
            rolling = rolling_avg(env_data['Humidity'], 20)
            print(rolling, flush=True)
            print(len(rolling), flush=True)
            ax.plot(env_data['date'], rolling_avg(env_data['Humidity'], 20), color='orange')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %I:%M %p', tz=timezone('America/Chicago')))
        ax.set_xlabel('Date')
        ax.set_ylabel(selection)
        ax.set_title(f'{selection} from {datestr(range[0])} to {datestr(range[1])}')
        fig.autofmt_xdate()
        fig.tight_layout()

        image_file = BytesIO()
        fig.savefig(image_file, dpi=dpi)
        image_file.seek(0)
        return image_file
    finally:
        plt.close(fig)
