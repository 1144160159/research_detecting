# Copyright 2020 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Flower server."""


import concurrent.futures
import io
import timeit
import time
from collections import Counter,OrderedDict
import sys
import gc
from typing import Dict, List, Optional, Tuple, Union

from flwr.common import (
    Code,
    DisconnectRes,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    Parameters,
    ReconnectIns,
    PropRes,
    PropIns,
    ArchitectureFitIns,
    Scalar,parameters_to_ndarrays,ndarrays_to_parameters
)
from flwr.common.logger import log
from logging import DEBUG, INFO, WARN,CRITICAL
from flwr.common.typing import GetParametersIns
from flwr.server.client_manager import ClientManager, SimpleClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.history import History
from flwr.server.strategy import FedAvg, Strategy
from numpy import NaN
import pandas as pd
import logging
import time
import json
from .server_config import ServerConfig

FitResultsAndFailures = Tuple[
    List[Tuple[ClientProxy, FitRes]],
    List[Union[Tuple[ClientProxy, FitRes], BaseException]],
]
EvaluateResultsAndFailures = Tuple[
    List[Tuple[ClientProxy, EvaluateRes]],
    List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
]
ReconnectResultsAndFailures = Tuple[
    List[Tuple[ClientProxy, DisconnectRes]],
    List[Union[Tuple[ClientProxy, DisconnectRes], BaseException]],
]
ProposalResultsAndFailures = Tuple[
    List[Tuple[ClientProxy, PropRes]],
    List[Union[Tuple[ClientProxy, PropRes], BaseException]],
]
ArchitectureFitResultsAndFailures = Tuple[
    List[Tuple[ClientProxy, FitRes]],
    List[Union[Tuple[ClientProxy, FitRes], BaseException]],
]


class Server:
    """Flower server."""

    def __init__(
        self,
        *,
        client_manager: ClientManager,
        config : ServerConfig,
        strategy: Optional[Strategy] = None,
        
    ) -> None:
        self._client_manager: ClientManager = client_manager
        self.strategy: Strategy = strategy if strategy is not None else FedAvg()
        self.max_workers: Optional[int] = None
        self.server_config = config


    def set_max_workers(self, max_workers: Optional[int]) -> None:
        """Set the max_workers used by ThreadPoolExecutor."""
        self.max_workers = max_workers

    def set_strategy(self, strategy: Strategy) -> None:
        """Replace server strategy."""
        self.strategy = strategy

    def client_manager(self) -> ClientManager:
        """Return ClientManager."""
        return self._client_manager

    # pylint: disable=too-many-locals
    #@profile
    def fit(self) -> Tuple[History, float]:


        """Run federated averaging for a number of rounds."""
        #history = History()
        logger = logging.getLogger(f"server")

        timeout = self.server_config.round_timeout
        num_rounds = self.server_config.num_rounds

        # Run federated learning for num_rounds
        start_time = timeit.default_timer()
        #Initialize model parameters
        model_parameters_previous_round=None
        model_architecture = None
        features_mapping= {}

        # TO BE IMPLEMENTED
        #if self.starting_round != 1 and self.Strategy.load_checkpoint_fn != None:
        #    self.model_parameters,self.model_architecture = self.strategy.load_checkpoint_fn()

     
        for current_round in range( 0,num_rounds+1 ):
      
            """
             Request clients' proposal
            """ 

            log(INFO, "")          
            log(INFO, f"[{time.time()}] [ROUND {current_round}]")
            logger.info(f"[{time.time()}] [ROUND {current_round}]")
            log(INFO, f"[{time.time()}] [Proposals_request]")
            start = time.time()
            logger.info(f"[{start}] Starting proposals_request_round")
            proposals, _= self.proposals_req_round( server_round = current_round, timeout= timeout)
            logger.info(f"[{time.time()}] Ended proposals_request_round - Duration {time.time()-start}")
           
            """
             Update global model phase
            """ 
            log(INFO,"")
            log(INFO, f"[{time.time()}] [Update global model]")
            start = time.time()
            logger.info(f"[{start}] Starting compute_new_architecture")
            model_architecture, model_parameters, features_mapping = self.strategy.compute_new_architecture(
                current_round,
                model_architecture,
                model_parameters_previous_round,
                proposals,
                features_mapping,
                
                
            )
            logger.info(f"[{time.time()}] Ended compute_new_architecture - Duration {time.time()-start}")

           
            #if self.strategy.save_model_fn!=None:
            #    self.strategy.save(self.features_mapping,current_round,"aggregated")
            #classes = list(self.features_mapping.keys())
            #log(DEBUG, f"The features are {classes}")
            
            if  model_architecture== None:
                log(CRITICAL,"The model is NULL !!")
            
            #print(self.parameters)
            #print(self.vocabulary)


            """
             Client's training with the updated global model
            """ 
            log(INFO,"")
            start = time.time()
            log(INFO, f"[{time.time()}] [Local training]")
            logger.info(f"[{start}] Starting architecture_fit_round")
            model_parameters_previous_round,_ = self.architecture_fit_round(
               # num_rounds=current_round,
                server_round=current_round,
                timeout=timeout,
                model_architecture=model_architecture,
                model_parameters=model_parameters,
                features_mapping=features_mapping,
            )
            


        

            logger.info(f"[{time.time()}] Endend architecture_fit_round - Duration {time.time()-start}")
   	        # task [if available]

            if self.strategy.on_task_fn != None:
                start=time.time()
                logger.info(f"[{start}] Starting Downstream task")
                self.strategy.on_task_fn(model_architecture,model_parameters,current_round)
                logger.info(f"[{time.time()}] Endend Downstream task - Duration {time.time()-start}")
        
            """
             Client's evaluation phase [optional]
            """ 
            if self.strategy.has_evaluate_round == True:
            
                start = time.time()
            
                logger.info(f"[{start}] Starting evaluate_round")
        
                # Evaluate model on a sample of available clients
                res_fed = self.evaluate_round(server_round=current_round, timeout=timeout)
                if res_fed is not None:
                    loss_fed, evaluate_metrics_fed, _ = res_fed
                    if loss_fed is not None:
                        log(
                                    INFO,
                                    "Training progress: (Round=%s, Loss_fed=%s, Accuracy = %s, Time=%s)",
                                    current_round,
                                    loss_fed,
                                    evaluate_metrics_fed["accuracy"],
                                    timeit.default_timer() - start_time,
                        )
                logger.info(f"[{time.time()}] Endend evaluate_round - Duration {time.time()-start}") 
            else:
                log(INFO,"Skipping evaluate round")
            '''
            NOT LONGER USED
            history.add_data(
                        server_round=current_round, time = timeit.default_timer() - start_time,f_loss=NaN ,f_accuracy=NaN,
                        t_loss= metrics_aggregated_fit["loss"],t_accuracy=metrics_aggregated_fit["accuracy"], feature= len(list(self.features_mapping.keys()))
            )
            #Downstream task [if available]

            if self.strategy.on_downstream_task_fn != None:

            self.strategy.on_downstream_task_fn(self.model_architecture,self.model_parameters)

                # Bookkeeping
            end_time = timeit.default_timer()
            elapsed = end_time - start_time
            return history, elapsed
            '''
        end_time = timeit.default_timer()
        elapsed = end_time - start_time
        return  elapsed

    def evaluate_round(
        self,
        server_round: int,
        timeout: Optional[float],
    ) -> Optional[
        Tuple[Optional[float], Dict[str, Scalar], EvaluateResultsAndFailures]
    ]:
        """Validate current global model on a number of clients."""
        # Get clients and their respective instructions from strategy
        client_instructions = self.strategy.configure_evaluate(
            server_round=server_round,
            parameters=self.model_parameters,
            client_manager=self._client_manager,
        )
        if not client_instructions:
            log(INFO, "configure_evaluate: no clients selected, skipping evaluation")
            return None
        log(
            INFO,
            "configure_evaluate: strategy sampled %s clients (out of %s)",
            len(client_instructions),
            self._client_manager.num_available(),
        )
        logger = logging.getLogger(f"server")
        logger.info(f"[{time.time()}] Ended evaluate_round preparation")
        # Collect `evaluate` results from all clients participating in this round
        results, failures = evaluate_clients(
            client_instructions,
            max_workers=self.max_workers,
            timeout=timeout,
            group_id=server_round,
        )
        log(
            INFO,
            "aggregate_evaluate: received %s results and %s failures",
            len(results),
            len(failures),
        )
        logger.info(f"[{time.time()}] Received evaluate_round result")
        # Aggregate the evaluation results
        aggregated_result: Tuple[
            Optional[float],
            Dict[str, Scalar],
        ] = self.strategy.aggregate_evaluate(server_round, results, failures)

        loss_aggregated, metrics_aggregated = aggregated_result
        return loss_aggregated, metrics_aggregated, (results, failures)

    def fit_round(
        self,
        server_round: int,
        timeout: Optional[float],
    ) -> Optional[
        Tuple[Optional[Parameters], Dict[str, Scalar], FitResultsAndFailures]
    ]:
        """Perform a single round of federated averaging."""
        # Get clients and their respective instructions from strategy
        client_instructions = self.strategy.configure_fit(
            server_round=server_round,
            parameters=self.parameters,
            client_manager=self._client_manager,
        )

        if not client_instructions:
            log(INFO, "configure_fit: no clients selected, cancel")
            return None
        log(
            INFO,
            "configure_fit: strategy sampled %s clients (out of %s)",
            len(client_instructions),
            self._client_manager.num_available(),
        )

        # Collect `fit` results from all clients participating in this round
         
        results, failures = fit_clients(
            client_instructions=client_instructions,
            max_workers=self.max_workers,
            timeout=timeout,
            group_id=server_round,
        )
        log(
            INFO,
            "aggregate_fit: received %s results and %s failures",
            len(results),
            len(failures),
        )

        # Aggregate training results
        aggregated_result: Tuple[
            Optional[Parameters],
            Dict[str, Scalar],
        ] = self.strategy.aggregate_fit(server_round, results, failures)

        parameters_aggregated, metrics_aggregated = aggregated_result
        return parameters_aggregated, metrics_aggregated, (results, failures)
    
    def architecture_fit_round(
        self,
        model_architecture: bytes,
        model_parameters: Parameters,
        features_mapping: Dict[str,int],
        server_round: int,
        timeout: Optional[float],
    ) -> Optional[
        Tuple[Dict[str, Scalar],   ArchitectureFitResultsAndFailures]
    ]:
        """Perform a single round of federated averaging."""

        client_instructions = self.strategy.configure_architecture_fit_round(
            server_round=server_round,
            model_architecture= model_architecture,
            parameters=model_parameters,
            features_mapping = features_mapping,
            client_manager=self._client_manager,
        )
       
        if not client_instructions:
            log(INFO, "Architecture_fit: no clients selected, cancel")
            return None
        log(
            INFO,
            "Architecture_fit: strategy sampled %s clients (out of %s)",
            len(client_instructions),
            self._client_manager.num_available(),
        )
        logger = logging.getLogger(f"server")
        logger.info(f"[{time.time()}] Ended architecture_fit_round preparation")
        # Collect `fit` results from all clients participating in this round
        results, failures = architecture_fits(
            client_instructions=client_instructions,
            max_workers=self.max_workers,
            timeout=timeout,
            group_id=server_round,
        )
        logger.info(f"[{time.time()}] Received architecture_fit_round result")
        log(
            INFO,
            "Architecture_fit: received %s results and %s failures",
            len(results),
            len(failures),
        )


        
        aggregated_result: Tuple[
            Optional[Parameters],
            Dict[str, Scalar],
        ] = self.strategy.aggregate_fit(server_round, results, failures)

        parameters_aggregated, metrics_aggregated = aggregated_result

        if self.strategy.save_model_fn!=None:
            #SAVE ALL THE CLIENTS RECEIVED MODELS [Optional]
            for client, fit_res in results:
                self.strategy.save_model_fn(model_architecture,fit_res.parameters,server_round,client.cid)
            self.strategy.save_model_fn(model_architecture,parameters_aggregated,server_round,"aggregated")
        
        return parameters_aggregated, metrics_aggregated#, (results, failures)
    
        

       
    def proposals_req_round(
        self,
        server_round: str,
        timeout: Optional[float],
    ) -> Optional[
        Tuple[Dict[str, Scalar], ProposalResultsAndFailures]
    ]:
   
        client_instructions = self.strategy.configure_proposal_req_round(
                                                                            server_round=server_round,
                                                                            client_manager=self._client_manager,
                                                                        )

        if not client_instructions:
            log(INFO, "Proposal_request: no clients selected, cancel")
            return None
        log(
            INFO,
            "Proposal_request: involved %s clients (out of %s)",
            len(client_instructions),
            self._client_manager.num_available(),
        )

        logger = logging.getLogger(f"server")
        logger.info(f"[{time.time()}] Ended Proposal_req preparation")
        results, failures = proposals_reqs(
            client_instructions=client_instructions,
            max_workers=self.max_workers,
            timeout=timeout,
            group_id=server_round,
        )
        
        if self.strategy.on_save_proposals_fn!=None:
            #save the clients vocabulary [optional]
            for client, prop_res in results:
               # print(prop_res.proposal)
                self.strategy.on_save_proposals_fn(prop_res.proposal,server_round,client.cid)

        #compute aggregated proposal
        proposals=self.strategy.aggregate_proposal_req_round(server_round,results,failures)

        if self.strategy.on_save_proposals_fn!=None:
                self.strategy.on_save_proposals_fn(proposals,server_round,"aggregated")

        logger.info(f"[{time.time()}] Received Proposal_req result")
        log(
            INFO,
            "Received %s results and %s failures",
            len(results),
            len(failures),
        )
        return proposals ,(results,failures)

    def disconnect_all_clients(self, timeout: Optional[float]) -> None:
        """Send shutdown signal to all clients."""
        all_clients = self._client_manager.all()
        clients = [all_clients[k] for k in all_clients.keys()]
        instruction = ReconnectIns(seconds=None)
        client_instructions = [(client_proxy, instruction) for client_proxy in clients]
        _ = reconnect_clients(
            client_instructions=client_instructions,
            max_workers=self.max_workers,
            timeout=timeout,
        )

    def _get_initial_parameters(
        self, server_round: int, timeout: Optional[float]
    ) -> Parameters:
        """Get initial parameters from one of the available clients."""
        # Server-side parameter initialization
        parameters: Optional[Parameters] = self.strategy.initialize_parameters(
            client_manager=self._client_manager
        )
        if parameters is not None:
            log(INFO, "Using initial global parameters provided by strategy")
            return parameters

        # Get initial parameters from one of the clients
        log(INFO, "Requesting initial parameters from one random client")
        random_client = self._client_manager.sample(1)[0]
        ins = GetParametersIns(config={})
        get_parameters_res = random_client.get_parameters(
            ins=ins, timeout=timeout, group_id=server_round
        )
        log(INFO, "Received initial parameters from one random client")
        return get_parameters_res.parameters


def reconnect_clients(
    client_instructions: List[Tuple[ClientProxy, ReconnectIns]],
    max_workers: Optional[int],
    timeout: Optional[float],
) -> ReconnectResultsAndFailures:
    """Instruct clients to disconnect and never reconnect."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted_fs = {
            executor.submit(reconnect_client, client_proxy, ins, timeout)
            for client_proxy, ins in client_instructions
        }
        finished_fs, _ = concurrent.futures.wait(
            fs=submitted_fs,
            timeout=None,  # Handled in the respective communication stack
        )

    # Gather results
    results: List[Tuple[ClientProxy, DisconnectRes]] = []
    failures: List[Union[Tuple[ClientProxy, DisconnectRes], BaseException]] = []
    for future in finished_fs:
        failure = future.exception()
        if failure is not None:
            failures.append(failure)
        else:
            result = future.result()
            results.append(result)
    return results, failures


def reconnect_client(
    client: ClientProxy,
    reconnect: ReconnectIns,
    timeout: Optional[float],
) -> Tuple[ClientProxy, DisconnectRes]:
    """Instruct client to disconnect and (optionally) reconnect later."""
    disconnect = client.reconnect(
        reconnect,
        timeout=timeout,
        group_id=None,
    )
    return client, disconnect


# === ARCHITECTURE FIT ===

def architecture_fits(
    client_instructions: List[Tuple[ClientProxy, ArchitectureFitIns]],
    max_workers: Optional[int],
    timeout: Optional[float],
    group_id: int,
) -> ArchitectureFitResultsAndFailures:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted_fs = {
            executor.submit(architecture_fit, client_proxy, ins, timeout, group_id)
            for client_proxy, ins in client_instructions
        }
        finished_fs, _ = concurrent.futures.wait(
            fs=submitted_fs,
            timeout=None,  # Handled in the respective communication stack
        )
   
    # Gather results
    results: List[Tuple[ClientProxy, FitRes]] = []
    failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]] = []
    for future in finished_fs:
        _handle_finished_future_after_architecture_fit(
            future=future, results=results, failures=failures
        )
 
    return results, failures

def architecture_fit(
    client: ClientProxy, ins: ArchitectureFitIns, timeout: Optional[float], group_id: int
) -> Tuple[ClientProxy, FitRes]:
    fit_res = client.architecture_fit(ins, timeout=timeout, group_id=group_id)
    return client, fit_res

def _handle_finished_future_after_architecture_fit(
    future: concurrent.futures.Future,  # type: ignore
    results: List[Tuple[ClientProxy, FitRes]],
    failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
) -> None:
    """Convert finished future into either a result or a failure."""
    # Check if there was an exception
    failure = future.exception()

    if failure is not None:
        failures.append(failure)
        return

    # Successfully received a result from a client
    result: Tuple[ClientProxy, FitRes] = future.result()
    _, res = result

    # Check result status code
    if res.status.code == Code.OK:
        results.append(result)
        return

    # Not successful, client returned a result where the status code is not OK
    failures.append(result)


# === PROPOSALS REQUEST ===
def proposals_reqs(
    client_instructions: List[Tuple[ClientProxy, PropIns]],
    max_workers: Optional[int],
    timeout: Optional[float],
    group_id: int,
) -> ProposalResultsAndFailures:
    """Refine parameters concurrently on all selected clients."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted_fs = {
            executor.submit(proposals_req, client_proxy, ins, timeout, group_id)
            for client_proxy, ins in client_instructions
        }
        finished_fs, _ = concurrent.futures.wait(
            fs=submitted_fs,
            timeout=None,  # Handled in the respective communication stack
        )

    # Gather results
    results: List[Tuple[ClientProxy, PropRes]] = []
    failures: List[Union[Tuple[ClientProxy, PropRes], BaseException]] = []
    for future in finished_fs:
        _handle_finished_future_after_proposals_req(
            future=future, results=results, failures=failures
        )
    return results, failures

def proposals_req(
    client: ClientProxy, ins: PropIns, timeout: Optional[float], group_id: int
) -> Tuple[ClientProxy, PropRes]:
    """Refine parameters on a single client."""
    prop_res = client.proposal_req(ins, timeout=timeout, group_id=group_id)
    
    return client, prop_res


def _handle_finished_future_after_proposals_req(
    future: concurrent.futures.Future,  # type: ignore
    results: List[Tuple[ClientProxy, PropRes]],
    failures: List[Union[Tuple[ClientProxy, PropRes], BaseException]],
) -> None:
    """Convert finished future into either a result or a failure."""
    # Check if there was an exception
    failure = future.exception()
    if failure is not None:
        failures.append(failure)
        return

    # Successfully received a result from a client
    result: Tuple[ClientProxy, PropRes] = future.result()
    _, res = result

    # Check result status code
    if res.status.code == Code.OK:
        results.append(result)
        return

    # Not successful, client returned a result where the status code is not OK
    failures.append(result)


# === FIT ===

def fit_client(
    client: ClientProxy, ins: FitIns, timeout: Optional[float], group_id: int
) -> Tuple[ClientProxy, FitRes]:
    """Refine parameters on a single client."""
    tok_res = client.fit(ins, timeout=timeout, group_id=group_id)
    return client, tok_res

def fit_clients(
    client_instructions: List[Tuple[ClientProxy, FitIns]],
    max_workers: Optional[int],
    timeout: Optional[float],
    group_id: int,
) -> FitResultsAndFailures:
    """Refine parameters concurrently on all selected clients."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted_fs = {
            executor.submit(fit_client, client_proxy, ins, timeout, group_id)
            for client_proxy, ins in client_instructions
        }
        finished_fs, _ = concurrent.futures.wait(
            fs=submitted_fs,
            timeout=None,  # Handled in the respective communication stack
        )

    # Gather results
    results: List[Tuple[ClientProxy, FitRes]] = []
    failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]] = []
    for future in finished_fs:
        _handle_finished_future_after_fit(
            future=future, results=results, failures=failures
        )
    return results, failures


def _handle_finished_future_after_fit(
    future: concurrent.futures.Future,  # type: ignore
    results: List[Tuple[ClientProxy, FitRes]],
    failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
) -> None:
    """Convert finished future into either a result or a failure."""
    # Check if there was an exception
    failure = future.exception()
    if failure is not None:
        failures.append(failure)
        return

    # Successfully received a result from a client
    result: Tuple[ClientProxy, FitRes] = future.result()
    _, res = result

    # Check result status code
    if res.status.code == Code.OK:
        results.append(result)
        return

    # Not successful, client returned a result where the status code is not OK
    failures.append(result)


# === EVALUATE ===


def evaluate_clients(
    client_instructions: List[Tuple[ClientProxy, EvaluateIns]],
    max_workers: Optional[int],
    timeout: Optional[float],
    group_id: int,
) -> EvaluateResultsAndFailures:
    """Evaluate parameters concurrently on all selected clients."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted_fs = {
            executor.submit(evaluate_client, client_proxy, ins, timeout, group_id)
            for client_proxy, ins in client_instructions
        }
        finished_fs, _ = concurrent.futures.wait(
            fs=submitted_fs,
            timeout=None,  # Handled in the respective communication stack
        )

    # Gather results
    results: List[Tuple[ClientProxy, EvaluateRes]] = []
    failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]] = []
    for future in finished_fs:
        _handle_finished_future_after_evaluate(
            future=future, results=results, failures=failures
        )
    return results, failures


def evaluate_client(
    client: ClientProxy,
    ins: EvaluateIns,
    timeout: Optional[float],
    group_id: int,
) -> Tuple[ClientProxy, EvaluateRes]:
    """Evaluate parameters on a single client."""
    evaluate_res = client.evaluate(ins, timeout=timeout, group_id=group_id)
    return client, evaluate_res


def _handle_finished_future_after_evaluate(
    future: concurrent.futures.Future,  # type: ignore
    results: List[Tuple[ClientProxy, EvaluateRes]],
    failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
) -> None:
    """Convert finished future into either a result or a failure."""
    # Check if there was an exception
    failure = future.exception()
    if failure is not None:
        failures.append(failure)
        return

    # Successfully received a result from a client
    result: Tuple[ClientProxy, EvaluateRes] = future.result()
    _, res = result

    # Check result status code
    if res.status.code == Code.OK:
        results.append(result)
        return

    # Not successful, client returned a result where the status code is not OK
    failures.append(result)


def init_defaults(
    server: Optional[Server],
    config: ServerConfig,
    strategy: Optional[Strategy],
    client_manager: Optional[ClientManager],
) -> Tuple[Server, ServerConfig]:
    """Create server instance if none was given."""

    # Set default config values
    #if config is None:
    #    config = ServerConfig()
    if server is None:
        if client_manager is None:
            client_manager = SimpleClientManager()
        if strategy is None:
            strategy = FedAvg()
        server = Server(client_manager=client_manager, 
                        strategy=strategy,
                        config = config
                        )
    elif strategy is not None:
        log(WARN, "Both server and strategy were provided, ignoring strategy")

  

    return server


def run_fl(
    server: Server,
) -> History:
    """Train a model on the given server and return the History object."""
    #hist, 
    elapsed_time = server.fit()


    log(INFO, "")
    log(INFO, "[SUMMARY]")
    log(INFO,"Flower Server is finished in %.2fs", elapsed_time)
    '''
    for idx, line in enumerate(io.StringIO(str(hist))):
        if idx == 0:
            log(INFO, "%s", line.strip("\n"))
        else:
            log(INFO, "\t%s", line.strip("\n"))
    log(INFO, "")

    df = pd.DataFrame(hist.data,columns=
                      pd.MultiIndex.from_tuples([("Round", ""),
                                                 ("Time", ""),
                                                ("Before aggregation", "LOSS"),  
                                                ("Before aggregation", "ACCURACY"), 
                                                ("After aggregation", "LOSS"),  
                                                ("After aggregation", "ACCURACY"),
                                                ("Feature","") ]) )
                                    
    df2 = df.to_string(index=False)     
   
  
    print(df2)
    '''
    # Graceful shutdown
    server.disconnect_all_clients(timeout=server.server_config.round_timeout)

    #return hist
