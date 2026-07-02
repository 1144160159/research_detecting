import pandas as pd
import numpy as np

from src.date import get_prev_day

def filter_corpus_based_on_vocabulary ( vocab:set, corpus: list):
    new_corpus = []
    for sentence in corpus:
        new_sentence = []
        
        for ip in sentence: 
            if ip in vocab:
                new_sentence.append(ip)
        if len(new_sentence)>0:
            new_corpus.append(new_sentence)
    
    return new_corpus



def compute_interest_port_darknet(interest_df, traffic_df,darknet_df,beta, day):
     # Define column name
    column_name_traffic_df =  'count'
    today_interest_column = f'{day}'
    yesterday_interest_column = f'{get_prev_day(day)}'

    # FIRST STEP ->  COMPUTE THE DECREASED INTEREST OF KNOWN IPs 
    
    if yesterday_interest_column in interest_df.columns: # this is skipped on day 0
           interest_df[today_interest_column] = beta * interest_df[yesterday_interest_column]

    #SECOND STEP -> Compute today's IP interest based on traffic

    #traffic_df['temp'] = (1 - beta) * np.log10(traffic_df[column_name_traffic_df] + 1)
    
    #traffic_df["temp"] = (1-beta)* sum((np.log10(traffic_df[f'count_{row["client_id"]}']) * np.log2(traffic_df[f'port_{row["client_id"]}']))/row["darknet_size"] for row in darknet_df.iterrows()) 
    
    traffic_df["temp"] = (1 - beta) * darknet_df.apply(
    lambda row: (
                np.log10(
                    traffic_df[f'count_{row["client_id"]}'][traffic_df[f'count_{row["client_id"]}'] != 0]
                )             
                + np.log2(
                     traffic_df[f'port_{row["client_id"]}'][traffic_df[f'port_{row["client_id"]}']!= 0]
                )
                /row["darknet_size"] 
                ), 
    axis=1
    ).sum()
    # Merge interest_df and traffic_df on 'ip'
    interest_df = interest_df.merge(traffic_df[['ip', 'temp']], on='ip', how='outer')
    
    # THIRD STEP -> Merge the traffic_df["temp"] containing today interest with the interest df o

    if today_interest_column in interest_df.columns: # this is skipped on day 0
           interest_df[today_interest_column] = (
                interest_df[today_interest_column].fillna(0)  
                + interest_df["temp"].fillna(0) 
    )
            
    else:
        # Update today's interest for existing IPs and fill NaN for new IPs
        interest_df[today_interest_column] = (interest_df["temp"].fillna(0))

    
    # Drop the temporary column created during the merge
    interest_df.drop(columns=[f"temp"], inplace=True)

    return interest_df

