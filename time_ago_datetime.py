from datetime import datetime, timedelta
import re

pattern = re.compile(r'(\d+)\s+(\w+)\s+ago')

def convert_time_ago(time_ago_str):
    match = pattern.search(time_ago_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2).lower()
    else:
        raise ValueError("Invalid time ago string")

    if unit == 'seconds' or unit == 'second':
        time_delta = timedelta(seconds=num)
    elif unit == 'minutes' or unit == 'minute':
        time_delta = timedelta(minutes=num)
    elif unit == 'hours' or unit == 'hour':
        time_delta = timedelta(hours=num)
    elif unit == 'days' or unit == 'day':
        time_delta = timedelta(days=num)
    elif unit == 'weeks' or unit == 'week':
        time_delta = timedelta(weeks=num)
    elif unit == 'months' or unit == 'month':
        time_delta = timedelta(days=num*30)
    elif unit == 'years' or unit == 'year':
        time_delta = timedelta(days=num*365)
    else:
        return datetime.now()

    datetime_obj = datetime.now() - time_delta

    return datetime_obj