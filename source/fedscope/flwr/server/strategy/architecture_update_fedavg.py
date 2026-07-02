

from logging import WARNING
from typing import Callable, Dict, List, Optional, Tuple, Union

from flwr.common import (
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    PropIns,
    PropRes,
    MetricsAggregationFn,
    NDArrays,
    Parameters,
    Scalar,
    ArchitectureFitIns,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)

from logging import INFO, WARN
from flwr.common.logger import log
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from .aggregate import aggregate, aggregate_inplace, weighted_loss_avg
from flwr.server.strategy.fedavg import FedAvg
WARNING_MIN_AVAILABLE_CLIENTS_TOO_LOW = """
Setting `min_available_clients` lower than `min_fit_clients` or
`min_evaluate_clients` can cause the server to fail when there are too few clients
connected to the server. `min_available_clients` must be set to a value larger
than or equal to the values of `min_fit_clients` and `min_evaluate_clients`.
"""

import datetime
now = datetime.datetime.now

from pathlib import Path # just a utility for better cross-platform file-loading
from scipy.io import loadmat
from sklearn.model_selection import cross_validate
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit

from flwr.common.logger import log
from logging import DEBUG, ERROR, INFO, WARN
import flwr as fl





# pylint: disable=line-too-long
class   Architecture_Update_FedAvg(FedAvg):

    """Federated Averaging strategy.

    Implementation based on https://arxiv.org/abs/1602.05629


    """

    def __init__(
        self,
        *,
        #fraction_fit: float = 1.0,
        #fraction_evaluate: float = 1.0,
        min_clients: int = 2,#min_fit_clients: int =2,
        #min_evaluate_clients: int = 2,
        #min_available_clients: int = 2,
        evaluate_fn: Optional[
            Callable[
                [int, NDArrays, Dict[str, Scalar]],
                Optional[Tuple[float, Dict[str, Scalar]]],
            ]
        ] = None,
        on_fit_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
        on_evaluate_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
        accept_failures: bool = True,
        initial_parameters: Optional[Parameters] = None,
        fit_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,
        evaluate_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,
        inplace: bool = True,
        #new parameters introductuced with the proposals and the architcture update
        on_configure_proposals_req_round_fn: Optional[Callable] = None,
        on_compute_new_architecture_fn: Callable,
        on_configure_architecture_fit_round_fn :  Optional[Callable] = None,
        on_aggregate_proposal_req_round_fn : Optional[Callable] = None,
        on_aggregate_architecture_fit_round_fn :  Optional[Callable] = None,
        on_downstream_task_fn : Optional[Callable] = None,
        save_model_fn : Optional[Callable] = None,
        on_task_fn : Optional[Callable] = None,
        save_proposals_fn: Optional[Callable] = None,
        has_evaluate_round: Optional[bool] = True,
        load_checkpoint_fn: Optional[Callable] = None,
       

    ) -> None:
        super().__init__(fraction_fit=1,
                        fraction_evaluate= 1,
                        min_fit_clients = min_clients,
                        min_evaluate_clients = min_clients,
                        min_available_clients= min_clients,
                        evaluate_fn = evaluate_fn,
                        on_fit_config_fn= on_fit_config_fn,
                        on_evaluate_config_fn = on_evaluate_config_fn,
                        accept_failures = accept_failures,
                        initial_parameters = initial_parameters,
                        fit_metrics_aggregation_fn = fit_metrics_aggregation_fn,
                        evaluate_metrics_aggregation_fn = evaluate_metrics_aggregation_fn,
                        inplace = inplace)
        
        
        self.on_configure_proposals_req_round_fn = on_configure_proposals_req_round_fn
        self.on_configure_architecture_fit_round_fn = on_configure_architecture_fit_round_fn
        self.on_compute_new_architecture_fn=on_compute_new_architecture_fn
        self.on_aggregate_proposal_req_round_fn=on_aggregate_proposal_req_round_fn
        self.on_aggregate_architecture_fit_round_fn=on_aggregate_architecture_fit_round_fn

        self.on_downstream_task_fn = on_downstream_task_fn
        self.save_model_fn = save_model_fn
        self.on_task_fn=on_task_fn
        self.on_save_proposals_fn=save_proposals_fn
        self.has_evaluate_round = has_evaluate_round
        self.load_checkpoint_fn = load_checkpoint_fn

    def configure_proposal_req_round(
        self, server_round: int, client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, PropIns]]:
        
        """Configure the next round of training."""
        
        config= {}  # default behavior is empty
        if self.on_configure_proposals_req_round_fn is not None:
            
            config = self.on_configure_proposals_req_round_fn(server_round)

        prop_ins = PropIns(config)

        # Sample clients
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()
        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )
        # Return client/config pairs
        return [(client, prop_ins) for client in clients]
    
    def configure_architecture_fit_round(
        self, 
        server_round: int, 
        model_architecture : Scalar,
        parameters: Parameters,
        features_mapping: Dict[str, Scalar], 
        client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, PropIns]]:
        """Configure the next round of training."""
        
        config = {}  # default behavior is fit without any config
        if self.on_configure_architecture_fit_round_fn is not None:
            config = self.on_configure_architecture_fit_round_fn(server_round)

       
        # Sample clients
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()

        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )
        # Return client/config pairs
        return [(client, ArchitectureFitIns(model_architecture,parameters,features_mapping,config)) for client in clients] 
    
    def aggregate_proposal_req_round(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, PropRes]],
        failures: List[Union[Tuple[ClientProxy, PropRes], BaseException]],
    ) -> Dict[str, Scalar]:
        
        if len(failures)>0:
            log(ERROR, "One client has encountered an error doing proposal_req")   
            raise Exception(failures) 
        

        if self.on_aggregate_proposal_req_round_fn is not None:
                received_proposals = [x[1].proposal for x in results]
                return self.on_aggregate_proposal_req_round_fn(server_round, received_proposals)

        
        log(WARNING, "Missing aggregate_proposal_req_round !!!")



        return {}



    def compute_new_architecture(self,server_round, model,parameters,proposal,features):
        
        return  self.on_compute_new_architecture_fn(server_round,model,parameters,proposal,features)

       
