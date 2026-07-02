
from collections import Counter,OrderedDict
import io
import os
import random
import sys
import traceback
import flwr as fl
import logging 
import time
import argparse
import numpy as np
import torch

import pandas as pd
from src.SGNSTrainer import SGNSTrainer
from src.corpus import get_corpus
from src.data_generation import gen_vocabs, gen_training_pairs, gen_ns_table, ContextGenerator
from src.interest import filter_corpus_based_on_vocabulary
from src.preprocess import filter_data_5_IP_daily, load_raw_data
from src.date import * 
from flwr.common.logger import log
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN

class DarkVecClient(fl.client.NumPyClient):

    def __init__(self,client_id,darknet_size):
        self.client_id=client_id
        self.darknet_size = darknet_size
        self.logger  = logging.getLogger(f"client_{client_id}")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        log(INFO,f"The client is using {self.device} device")
        
    def get_parameters(self, config):
        pass  
    

    def set_parameters(self, parameters):
        pass

    def evaluate(self, parameters, config):
        pass
    
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
    
    def generate_dataset(self,config,features_mapping):

        corpus_filtered = filter_corpus_based_on_vocabulary(features_mapping.keys(),self.corpus)
        training_pairs = gen_training_pairs(corpus_filtered,context_window_size=config['word2vec_c'])
        
        del self.corpus #free memory, not needed anymore
        del corpus_filtered #free memory, not needed anymore
        #previous version of filtering
        #self.training_pairs =  [pair for pair in training_pairs if pair[0] in features_mapping.keys() and pair[1] in features_mapping.keys()]

        ns_table = gen_ns_table(training_pairs)
        self.logger.log(DEBUG,f"#training_pairs={len(training_pairs)}")
    
        return training_pairs,ns_table
        
 

    def read_dataset(self,config):
        
        
        DAY = config["day"]
   
        log(INFO, f"Starting loading file of the day {DAY}")

        #OLD DARKVEC FILTERING - 10 IPs over 30 days
        #self.traffic_df = filter_data(load_raw_data(DAY,args.dataset_path), DAY,args.dataset_path)

        traffic_df = filter_data_5_IP_daily(load_raw_data(DAY,args.dataset_path))
        self.logger.log(DEBUG,f"#pkt={len(traffic_df)}")
        ip_counts = traffic_df['ip'].value_counts().reset_index()
        ip_counts.columns = ['ip', 'count']

        unique_ports_per_ip = traffic_df.groupby("ip")["port"].nunique()


        proposal_df = pd.merge(ip_counts, unique_ports_per_ip, on="ip", how="inner")
        print(proposal_df)
        self.corpus = get_corpus(
                traffic_df,
                config['corpus_without_duplicates'],
                config['corpus_services'],
                config['corpus_top_ports']
                )

        proposal = {row["ip"]: f"{row['count']};{row['port']}" for idx, row in proposal_df.iterrows()}

        proposal["darknet_size"] =  self.darknet_size
        proposal["client_id"] =  self.client_id

        return proposal

    def proposals_req(self, config):
       
        log(INFO,f"Architecture update day {config['day']}")
        proposal = self.read_dataset(config)
        return proposal
    
    


    def architecture_fit(self,model_architecture,parameter,features_mapping,config):
      
        buff = io.BytesIO(model_architecture)
        buff.seek(0)
        model = torch.load(buff,weights_only=False)

        log(DEBUG,"Model loaded")


        training_pairs, ns_table = self.generate_dataset(config,features_mapping)
       # log(DEBUG,self.word_to_ind)
       # log(DEBUG,self.ns_table)
        trainer = SGNSTrainer(pairs=training_pairs,
                            model=model,
                            word_to_ind=features_mapping,
                            batch_size=config['word2vec_batch_size'],
                            device = self.device,
                            ns_table=ns_table,
                            n_epochs=config['word2vec_epochs'],
                            k=config['word2vec_negative_num'])
        

        log(DEBUG,"Trainer created")
        if args.no_train == True:
            loss =0
            log(INFO,"Skipping training...")
        else:
            loss= trainer.train()
        
        return [val.cpu().numpy() for _, val in model.state_dict().items()], len(features_mapping), {"accuracy":np.NaN,"loss":loss}
        
   

parser = argparse.ArgumentParser(description="Flower Embedded devices")
parser.add_argument(
    "--cid",
    type=str,
    required=True,
    help="Client identification, can be any string. USE A UNIQUE ID",
)
parser.add_argument(
    "--server_address",
    type=str,
    required=False,
    default="localhost:8080",
    help="IP:PORT of the server, Default localhost:8080 ",
)
parser.add_argument(
    "--darknet_size",
    type=int,
    default= 256,
    required=False,
    help="Size of the client's darknet",
)


parser.add_argument(
    "--no_train",
  
    action="store_true",
    required=False,
    help="Skip training process. Useful for debug",
)

#f'dataset/{darknet_no}/{darknet_no}_{day}*'

parser.add_argument(
    "--dataset_path",
    type=str,
    required=False,
    default="./dataset/darknet01/",
    help="Path of the dataset",
)
def ensure_trailing_slash(path):
    """Ensures the given path has a trailing slash."""
    return path if path.endswith('/') else path + '/'


os.makedirs("./log", exist_ok=True) 

args = parser.parse_args()

loggerFile1 = logging.getLogger(f"client_{args.cid}")
loggerDefault= logging.getLogger("flwr")
logging.basicConfig(handlers=[], encoding='utf-8', level=logging.DEBUG)
loggerFile1.addHandler(logging.FileHandler(f"./log/client_{args.cid}.log",mode="a"))
loggerDefault.addHandler(logging.FileHandler(f"./log/terminal_client_{args.cid}.log",mode="a"))


# Custom exception handler
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Let Ctrl+C work normally
        return
    loggerFile1.log(CRITICAL, f"[{time.time()}] Uncaught exception")
    loggerDefault.log(CRITICAL, f"[{time.time()}] Uncaught exception exc_info=({traceback.format_exception(exc_type, exc_value, exc_traceback)})")
# Redirect uncaught exceptions to log
sys.excepthook = log_exception


#SETTING SEED FOR GENERATE THE SAME RESULT EVERY TIME
seed =0 
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
np.random.default_rng(seed)
# When running on the CuDNN backend, two further options must be set
#torch.backends.cudnn.deterministic = True
#torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False
# Set a fixed value for the hash seed
os.environ["PYTHONHASHSEED"] = str(seed)



loggerFile1.log(INFO, f"[{time.time()}] Client {args.cid} started")
loggerFile1.log(INFO, f"[{time.time()}] Parameters received  {vars(args)}")

args.dataset_path = ensure_trailing_slash(args.dataset_path)
log(INFO, f"[{time.time()}] Parameters received  {vars(args)}")

client_darkvec=DarkVecClient(args.cid,args.darknet_size).to_client()

fl.client.start_client(server_address=args.server_address, client = client_darkvec, client_id=args.cid)



