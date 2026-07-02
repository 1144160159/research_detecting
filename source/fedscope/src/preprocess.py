from multiprocessing import Pool, cpu_count
import sys
import pandas as pd
from datetime import datetime, timedelta
from glob import glob
from src.config import *
from flwr.common.logger import log
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN

###############################################################################
# Raw data loading and preliminary transformations
###############################################################################
def pool_setup(flist):
    cpus = len(flist)
    if len(flist) > cpu_count(): cpus = cpu_count()
    try:
        pool = Pool(processes=cpus)
    except ValueError:
        pool = Pool(processes=1)
    iterable = iter(flist)

    return pool, iterable

def get_data(item):
    # Read a single file
    f_df = pd.read_csv(item,
                      # skip_blank_lines=True,
                      # na_values="-",
                      usecols=['ts', 'src_ip', 'dst_port','proto'],
                       ).rename(columns={'src_ip': 'ip', 'dst_port': 'port'})
    
      

    #print(f_df.memory_usage().sum())
   

    # Replace decimal representation of protocols to string identifier

    to_replace = dict()
    for x in f_df.proto.unique():
        if x == 6:
            to_replace[x] = 'tcp'
        elif x == 17:
            to_replace[x] = 'udp'
        elif x == 1:
            to_replace[x] = 'icmp'
        else:
            to_replace[x] = 'oth'
    f_df.proto = f_df.proto.replace(to_replace)
    # Merge port and protocol as 'port/protocol'
    f_df['pp'] = f_df.port.astype(str) + "/" + f_df.proto
    # Convert timestamps
    f_df.ts = f_df.ts.apply(lambda x: datetime.fromtimestamp(x))
    #print(f_df.memory_usage().sum())
    return f_df


###############################################################################
# Filtering preliminary preprocessed data
###############################################################################
def get_files_from(_date,dataset_path):
    """Load a list of file from the starting day to the previous 30th one.

    Parameters
    ----------
    _date : str
        starting date of file loading

    Returns
    -------
    list
        list of files to load

    """
    start = datetime.strptime(_date, '%Y%m%d')
    flist = []

    for d in range(30):
        target = start - timedelta(days=d)
        target = target.strftime('%Y%m%d')

        for fs in glob(f'{dataset_path}*{target}*'):
            flist.append(fs)
        if target == LOWER_BOUND: break

    return flist


def count_daily_ips(x):
    df = pd.read_csv(x, sep=',',usecols=['src_ip']).value_counts("src_ip")
   #print(df)
    return df


def load_filter_from_chunk(day,dataset_path):
    pool, iterable = pool_setup(get_files_from(day,dataset_path))
    df_list = pool.map(count_daily_ips, iterable)
    pool.close()
    counts = pd.concat(df_list).reset_index().groupby(by='src_ip').sum()
    #print(counts)
    return set(counts[counts >= 10].dropna().index)


###############################################################################
# Main functions
###############################################################################

def load_raw_data(day,dataset_path):
    print('Loading files:', f'{dataset_path}*{day}*')
    pool, iterable = pool_setup(glob(f'{dataset_path}*{day}*'))
    df_list = pool.map(get_data, iterable)
    log(DEBUG,f'Loaded {len(df_list)} files')
  
    pool.close()
    pool.join()


    raw_data = pd.concat(df_list)
    return raw_data

def new_get_data(day,darknet_no):
    df =load_raw_data(day,darknet_no)
    
    log(DEBUG,f'Loaded the file')
    #processing
   
    counts = df.reset_index().value_counts('ip')
    print( counts)
    filt = set(counts[counts >= 10].index)
    print( len(filt))
    filtered = df[df.ip.isin(set(filt))]
    # Datetime index
    filtered.index = pd.DatetimeIndex(filtered.ts)
    filtered = filtered.sort_index()

    return filtered




def filter_data_5_IP_daily(raw_data_df):


    counts = raw_data_df.reset_index().value_counts('ip')
    #print( counts)
    filt = set(counts[counts > 5].index)
    #print( len(filt))
    filtered = raw_data_df[raw_data_df.ip.isin(set(filt))]
    # Datetime index
    filtered.index = pd.DatetimeIndex(filtered.ts)
    filtered = filtered.sort_index()

    return filtered


'''
def filter_data(raw_data, day_to_filter,dataset_path):
    filt = load_filter_from_chunk(day_to_filter,dataset_path)
    # Filter IPS
    #print( len(filt))
    filtered = raw_data[raw_data.ip.isin(set(filt))]
    # Datetime index
    filtered.index = pd.DatetimeIndex(filtered.ts)
    filtered = filtered.sort_index()

    return filtered
'''

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