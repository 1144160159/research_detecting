
from collections import Counter, OrderedDict
import io
import os

import random
import pathlib
import sys
import traceback
from typing import List, Tuple
import flwr as fl
from flwr.common import Metrics,parameters_to_ndarrays,ndarrays_to_parameters
from flwr.common.logger import log,update_console_handler
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN
import numpy as np
import json
from flwr.common.typing import Parameters
import time
# Define metric aggregation function


import logging


import pandas as pd
import torch

import argparse
from src.interest import compute_interest_port_darknet
from src.word2vec_torch import Word2VecTorch

from src.date import * 

parser = argparse.ArgumentParser(description="Flower Embedded devices")

parser.add_argument(
    "--server_port",
    type=str,
    required=False,
    default="8080",
    help="PORT of the server, default 8080 ",
)
parser.add_argument(
    "--client_number",
    type=int,
    required=False,
    default="1",
    help="Number of clients ",
)

parser.add_argument(
    "--max_voc_size",
    type=int,
    required=False,
    default="-1",
    help="Maximum size of the vocabulary, -1 for no limit",
)
parser.add_argument(
    "--beta",
    type=float,
    required=False,
    default="0",
    help="Beta, used for compute the interest, default 0",
)

parser.add_argument(
    "--first_day",
    type=str,
    required=True,
    default="1",
    help="first day of traffic capture, date format YYYYMMDD ",
) 

parser.add_argument(
    "--last_day",
    type=str,
    required=True,
    default="1",
    help="last day of traffic capture, date format YYYYMMDD",
) 
parser.add_argument(
    "--checkpoint",
    type=str,
    required=False,
    default="",
    help="Start the training from a previous checkpoint, date format YYYYMMDD",
) 





args = parser.parse_args()

params = {"corpus_services": "auto",
          "corpus_without_duplicates":True,
          "corpus_top_ports":2500,
          "word2vec_c":5,
          "word2vec_e":50,  
          "word2vec_negative_num":5,
          "word2vec_epochs":1,
          "word2vec_batch_size":2048,
          "word2vec_method":"incremental"
          }

# NO USED ?
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    a = metrics[0]
    e,i = a

    if "loss" in  list(i.keys()):
            loss = [num_examples * m["loss"] for num_examples, m in metrics]
            examples = [num_examples for num_examples, _ in metrics]
            accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
            examples = [num_examples for num_examples, _ in metrics]
            return {"accuracy": sum(accuracies) / sum(examples),"loss": sum(loss) / sum(examples)}
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)

    return {"accuracy": sum(accuracies) / sum(examples)}


def aggregate_proposal_req_round(server_round, received_proposals) -> List[dict]:
        proposal = []
        for p in received_proposals:
            proposal.append(p.copy())  #log(INFO,f"-- The server has received this proposal {p}")
        del received_proposals
        return proposal

def configure_proposals_req_round(server_round):
     

        config = params  #iDarkVec parameters
        config["num_client"]=args.client_number
        config["day"] = get_day_from_round(args.first_day,server_round)
        log(INFO,f"The server ask the clients to generate proposal on day {config['day']}")

        return config

def loadCheckpoint(starting_round):

    """
    Loads a model checkpoint, its parameters, and the corresponding features mapping.
    Args:
        starting_round (int): The round number from which to load the checkpoint.
    Returns:
        tuple: A tuple containing:
            - model_architecture (bytes): The architecture of the loaded model in bytes.
            - model_parameters (torch.nn.Parameter): The parameters of the loaded model.
            - features_mapping (dict): The features mapping loaded from the vocabulary file.
    Raises:
        FileNotFoundError: If the model or vocabulary file does not exist.
        json.JSONDecodeError: If the vocabulary file is not a valid JSON.
    """
    

    model = torch.load(f"./models/model_day_{args.checkpoint}_client_aggregated.pt")
    model_parameters = ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])
    buff = io.BytesIO()
    torch.save(model, buff)
    buff.seek(0)
    model_architecture = buff.read()
    with open(f"./vocabularies/voc_day_{args.checkpoint}_client_aggregated.log", "r") as f:
        features_mapping = json.load(f)
    return model_architecture, model_parameters, features_mapping

#@profile
def on_compute_new_architecture(server_round,model_architecture, model_weights, proposals,features):
        """
        Compute a new model architecture based on the current round's proposals and features.
        Args:
            server_round (int): The current round of the server.
            model_architecture (bytes or None): The serialized model architecture from the previous round, or None if this is the first round.
            model_weights (fl.common.Parameters): The model weights from the previous round.
            features (dict): A dictionary containing the features from the previous round.
            proposals (list of dict): A list of dictionaries, each containing IP addresses and their counts proposed by clients.
        Returns:
            tuple: A tuple containing:
                - buff_byte (bytes): The serialized new model architecture.
                - Parameters (fl.common.Parameters): The new model weights.
                - word_to_ind (dict): A dictionary mapping IP addresses to their indices in the vocabulary.
        """
        #1 - Aggregate todays IPs proposed,

        log(DEBUG,f"N° of IPs in the vocabulary of the previous round: {len(features)}")

        del features; # we don't need the features since we retrive from the interest. Keep for compatibility with previous version


        
        darknet_data = []
        for client_prop in proposals:
            darknet_data.append({"client_id": client_prop["client_id"], "darknet_size": client_prop["darknet_size"]})
        darknet_df = pd.DataFrame(darknet_data)

       # today_ips_dict ={}
        today_ips_df = pd.DataFrame(columns=["ip"])
        #today_ips_df.set_index("ip")

        for client_prop in proposals: #list of dict
              
             # {
             # "client_id":"darknet01",
             # "darknet_size":256,
             # "ip1": "count1;#port1", 
             # "ip2": "count2;#port2" 
             # }
            id = client_prop["client_id"]
            client_prop.pop("client_id")
            client_prop.pop("darknet_size")
            client_df = pd.DataFrame([{"ip": key, f"count_{id}": int(value.split(";")[0]), f"port_{id}": int(value.split(";")[1])} for key, value in client_prop.items()])
            today_ips_df= today_ips_df.merge(client_df, on="ip", how="outer")
        
        proposals=None
        

        today_ips_df.fillna(0, inplace=True)   
        #print(today_ips_df)        
    
        #2 - Load the interest_df of the previous day/ from the checkpoint
        
        
        if args.checkpoint!="" and server_round == 0: #CASE CHECKPOINT 
            path = pathlib.Path(f"./interest/interest_day_{args.checkpoint}.csv")
            if path.exists() and args.checkpoint == "":
                interest_df = pd.read_csv(path)
                log(INFO, f"Loaded interest {path}")
            else:
                log(ERROR,f"./interest/interest_day_{args.chekpoint}.csv NOT found")
                raise FileNotFoundError(f"./interest/interest_day_{args.checkpoint}.csv NOT found")
        
        elif args.checkpoint=="" and server_round == 0: #CASE FIRST DAY, NO CHECKPOINT
             log(INFO, f"Created new interest dataframe")
             interest_df = pd.DataFrame(columns=["ip"])
        else:
            # Try to load previous day interest
            path = pathlib.Path(f"./interest/interest_day_{get_day_from_round(args.first_day,server_round-1)}.csv")
            if path.exists() :
                interest_df = pd.read_csv(path)
                log(INFO, f"Loaded interest {path}")
            else:
                log(ERROR,f"{path} NOT found")
                raise FileNotFoundError(f"{path} NOT found")

        #3 - Compute today interest

        interest_df = compute_interest_port_darknet(
             interest_df, 
             today_ips_df,
             darknet_df,
             args.beta,
             get_day_from_round(args.first_day,server_round)
             )
        del(today_ips_df)
        del(darknet_df)
        #3a - Sort today interest
        today_interest = interest_df[["ip", interest_df.columns[-1]]].copy()    
         
        del interest_df

        today_interest.sort_values(
             inplace=True,
            by=[today_interest.columns[-1], 'ip'],  # Primary and secondary sort keys
            ascending=[False, True]  # Descending for first column, ascending for 'ip'
        )
        #4 - Extract most interessing IPs and generate the word_to_ind/vocabulary
        if args.max_voc_size != -1:
            rows_to_take = min(len(today_interest), args.max_voc_size)
        else:
            rows_to_take=len(today_interest)
        temp = today_interest.iloc[:rows_to_take]["ip"].reset_index(drop=True).to_dict()

        today_interest.iloc[:rows_to_take].reset_index(drop=True).to_csv(f"./interest/interest_day_{get_day_from_round(args.first_day,server_round)}.csv")
        today_interest.iloc[rows_to_take:].reset_index(drop=True).to_csv(f"./interest/LOW_interest_day_{get_day_from_round(args.first_day,server_round)}.csv")
        
        #print(temp)
        word_to_ind = {value: index for index, value in temp.items()}
        #print(word_to_ind)
        vocab = set(word_to_ind.keys())
        log(DEBUG,f"N° of IPs in the vocabulary for the day {get_day_from_round(args.first_day,server_round)}: {len(vocab)}")

        
        #5 - Create/Update the model according to the IPs used


        if model_architecture == None:
            #Create a new model
            model = Word2VecTorch(
                vocab_size=len(vocab),
                embedding_dim=params['word2vec_e'],
                word_to_ind=word_to_ind
                )
        else:
            #Retrive old model and update
            #After the first round the updated weights is inside 'model_weights', the 'model_architecture' contains the architecture plus old weights
            #we need to upload the old_model, update the weights with 'model_weights', then update


            with io.BytesIO(model_architecture) as buff:
                buff.seek(0)
                model = torch.load(buff, weights_only=False)

                # Convert zip iterator to a list to avoid lingering references
                params_dict = list(zip(model.state_dict().keys(), parameters_to_ndarrays(model_weights)))

                # Convert values to PyTorch tensors efficiently
                state_dict = OrderedDict({k: torch.tensor(v).detach() for k, v in params_dict})

                # Free up memory from previous model state
                del params_dict
                

                # Load the new state into the model
                model.load_state_dict(state_dict, strict=True)

                # Free memory from state_dict after loading
                del state_dict
               
                
                model.update_with_removal(len(vocab),word_to_ind)


            #del model_weights
           # del model_architecture
        #6- Serialize the updated model to be sent to the clients
        
        with io.BytesIO() as buff:
            torch.save(model,buff)
            buff.seek(0)
            buff_byte = buff.read() # this contains weights + architecture in a single entity



        #print(len(buff_byte))
        #print(len(word_to_ind))
        # Using other library like tensorflow the weights and architecture are two separate entity
        #model_weights = [val.cpu().numpy() for _, val in model.state_dict().items()]      
        #model_weights = fl.common.ndarrays_to_parameters(model_weights) # this contains 
      
        
        return  buff_byte, Parameters(tensor_type="", tensors=[]), word_to_ind


def configure_architecture_fit_round(server_round):
      return params # we don't need any extra parameters




def save_model(model_architecture,
               parameters,
               server_round,
               client:str  #ID string  of the client who trained the model 
                           #OR "aggregated" for rappresent the model aggregated by the server since the function used is the same
               ):

    buff = io.BytesIO(model_architecture)
    buff.seek(0)
    model = torch.load(buff,weights_only=False)  
    params_dict = zip(model.state_dict().keys(),parameters_to_ndarrays(parameters))
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)
    torch.save(model,f"./models/model_day_{get_day_from_round(args.first_day,server_round)}_client_{client}.pt")
      
def save_vocabulary(
            vocabulary,
            server_round: int,
            client:str      #ID string  of the client who proposed the vocabulary
                            #OR "aggregated" for rappresent the vocabulary aggregated by the server 
            ):
   
    with open(f"./vocabularies/voc_day_{get_day_from_round(args.first_day,server_round)}_client_{client}.txt", "w") as f:
        json.dump(vocabulary,f)
        f.close()


#create the required folder (if dont exist)
os.makedirs("./vocabularies", exist_ok=True)
os.makedirs("./models", exist_ok=True) 
os.makedirs("./log", exist_ok=True) 
os.makedirs("./interest", exist_ok=True) 



strategy = fl.server.strategy.Architecture_Update_FedAvg(  
                evaluate_metrics_aggregation_fn=weighted_average,
                fit_metrics_aggregation_fn=weighted_average,
                on_configure_proposals_req_round_fn =configure_proposals_req_round,
                on_aggregate_proposal_req_round_fn=aggregate_proposal_req_round,
                on_compute_new_architecture_fn=on_compute_new_architecture,
                on_configure_architecture_fit_round_fn=configure_architecture_fit_round,
                min_clients=args.client_number,
                save_model_fn = save_model,
                save_proposals_fn=  save_vocabulary,
                load_checkpoint_fn = loadCheckpoint,
                has_evaluate_round=False,
                )  
                
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

loggerFile1 = logging.getLogger(f"server")
logging.basicConfig(handlers=[], encoding='utf-8', level=logging.DEBUG)
loggerFile1.addHandler(logging.FileHandler("./log/server.log",mode="a"))
loggerDefault= logging.getLogger("flwr")
loggerDefault.addHandler(logging.FileHandler(f"./log/terminal_server.log",mode="a"))




loggerFile1.log(INFO, f"[{time.time()}] Server started")
loggerFile1.log(INFO, f"[{time.time()}] Parameters received  {vars(args)}")


# Custom exception handler
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Let Ctrl+C work normally
        return
    loggerFile1.log(CRITICAL, f"[{time.time()}] Uncaught exception")
    loggerDefault.log(CRITICAL, f"[{time.time()}] Uncaught exception exc_info=({traceback.format_exception(exc_type, exc_value, exc_traceback)})")
# Redirect uncaught exceptions to log
sys.excepthook = log_exception



log(INFO, f"[{time.time()}] Parameters received  {vars(args)}")
rounds= get_round_from_day(args.first_day,args.last_day)
fl.server.start_server( server_address=f"[::]:{args.server_port}",
                        strategy=strategy,
                        config=fl.server.ServerConfig(
                             num_rounds = rounds,
                             load_checkpoint=True if args.checkpoint else False
                        ))