from datetime import datetime, timedelta

def get_next_day(start):
    start = datetime.strptime(start, '%Y%m%d')
    day = start + timedelta(days=1)
    day = day.strftime('%Y%m%d')

    return day


def get_prev_day(start):
    start = datetime.strptime(start, '%Y%m%d')
    day = start - timedelta(days=1)
    day = day.strftime('%Y%m%d')

    return day

def get_round_from_day(day1,day2):
    day1 = datetime.strptime(day1, '%Y%m%d')
    day2 = datetime.strptime(day2, '%Y%m%d')

    # Calculate the difference in days
    days_difference = abs((day2 - day1).days)
    
    # Return the rounded result
    return round(days_difference)



def get_day_from_round(start,round):
    start = datetime.strptime(start, '%Y%m%d')
    day = start + timedelta(days=round)
    day = day.strftime('%Y%m%d')
    return day
