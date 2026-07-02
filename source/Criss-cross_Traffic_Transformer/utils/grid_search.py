"""
Grid Search Module for CTT Model Hyperparameter Tuning

This module provides functionality to perform grid search over key hyperparameters:
- seq_len: input sequence length
- patch_len: patch length
- stride: stride for patching
- factor: attention factor
"""

import os
import json
import itertools
from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime
from exp.exp_main import Exp_Main


class GridSearch:
    """
    Grid Search class for hyperparameter optimization.
    
    This class performs exhaustive grid search over specified hyperparameter ranges
    and identifies the best combination based on validation performance.
    """
    
    def __init__(self, base_args, search_space: Dict[str, List[Any]], 
                 metric: str = 'f1_score', results_dir: str = './grid_search_results'):
        """
        Initialize GridSearch.
        
        Args:
            base_args: Base argument namespace with default hyperparameters
            search_space: Dictionary mapping hyperparameter names to lists of values to search
                         e.g., {'seq_len': [32, 64, 128], 'patch_len': [2, 4, 8]}
            metric: Metric to optimize ('f1_score', 'accuracy', 'loss')
            results_dir: Directory to save grid search results
        """
        self.base_args = base_args
        self.search_space = search_space
        self.metric = metric
        self.results_dir = results_dir
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Storage for results
        self.results = []
        self.best_params = None
        self.best_score = None
        self.best_result = None
        
    def _validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate parameter combination.
        
        Args:
            params: Dictionary of hyperparameters
            
        Returns:
            True if valid, False otherwise
        """
        # Ensure patch_len <= seq_len
        if 'patch_len' in params and 'seq_len' in params:
            if params['patch_len'] > params['seq_len']:
                return False
        
        # Ensure stride <= patch_len
        if 'stride' in params and 'patch_len' in params:
            if params['stride'] > params['patch_len']:
                return False
        
        # Ensure stride > 0 and patch_len > 0
        if 'stride' in params and params['stride'] <= 0:
            return False
        if 'patch_len' in params and params['patch_len'] <= 0:
            return False
        
        return True
    
    def _generate_param_combinations(self) -> List[Dict[str, Any]]:
        """
        Generate all valid parameter combinations from search space.
        
        Returns:
            List of parameter dictionaries
        """
        # Get all keys and values
        keys = list(self.search_space.keys())
        values = list(self.search_space.values())
        
        # Generate all combinations
        combinations = list(itertools.product(*values))
        
        # Convert to list of dictionaries and filter valid ones
        param_combinations = []
        for combo in combinations:
            params = dict(zip(keys, combo))
            if self._validate_params(params):
                param_combinations.append(params)
        
        return param_combinations
    
    def _update_args(self, params: Dict[str, Any]) -> Any:
        """
        Update base_args with new parameter values.
        
        Args:
            params: Dictionary of hyperparameters to update
            
        Returns:
            Updated args object
        """
        # Create a copy of base_args
        import copy
        updated_args = copy.deepcopy(self.base_args)
        
        # Update parameters
        for key, value in params.items():
            if hasattr(updated_args, key):
                setattr(updated_args, key, value)
        
        # Update dependent parameters
        if 'seq_len' in params and updated_args.mode == 'analysis':
            updated_args.pred_len = params['seq_len']
        
        return updated_args
    
    def _run_single_experiment(self, params: Dict[str, Any], trial_id: int, 
                               total_trials: int) -> Dict[str, Any]:
        """
        Run a single experiment with given parameters.
        
        Args:
            params: Dictionary of hyperparameters
            trial_id: Current trial number
            total_trials: Total number of trials
            
        Returns:
            Dictionary containing results
        """
        print(f"\n{'='*80}")
        print(f"Trial {trial_id}/{total_trials}")
        print(f"Parameters: {params}")
        print(f"{'='*80}\n")
        
        # Update args with current parameters
        current_args = self._update_args(params)
        
        # Create experiment setting name
        setting = self._create_setting_name(current_args, trial_id)
        
        try:
            # Initialize experiment
            exp = Exp_Main(current_args)
            
            # Train model
            print(f'>>>>>>>Training with parameters: {params}>>>>>>>')
            exp.train(setting)
            
            # Get validation performance
            vali_data, vali_loader = exp._get_data(flag='val')
            criterion = exp._select_criterion(name=current_args.loss, label_smoothing=0)
            
            # Run validation
            vali_loss, best_f1 = exp.vali(vali_data, vali_loader, criterion, test_data_flag=0, best_f1=0)
            
            # Get detailed validation metrics by re-running validation
            # Note: vali method already computes these but doesn't return them
            # So we compute them again for grid search tracking
            from sklearn.metrics import classification_report
            import torch.nn.functional as F
            import torch
            
            preds = []
            trues = []
            exp.model.eval()
            with torch.no_grad():
                for i, (batch_x, batch_y) in enumerate(vali_loader):
                    batch_x = batch_x.float().to(exp.device)
                    batch_y = batch_y.long().to(exp.device)
                    if current_args.mode == 'analysis':
                        batch_y = batch_y.reshape(-1)
                        outputs = exp.model(batch_x)
                    elif current_args.mode == 'pred':
                        outputs = exp.model(batch_x)
                        outputs = outputs[:, -current_args.pred_len:, :]
                        batch_y = batch_y[:, -current_args.pred_len:].to(exp.device)
                        outputs = outputs.reshape(-1, outputs.shape[2])
                        batch_y = batch_y.reshape(-1)
                    else:
                        outputs = exp.model(batch_x)
                    
                    pred = F.softmax(outputs, dim=1)
                    pred = torch.argmax(pred, dim=1).detach().cpu().numpy()
                    true = batch_y.detach().cpu().numpy()
                    preds.append(pred)
                    trues.append(true)
            
            preds = np.array(preds).reshape(-1,)
            trues = np.array(trues).reshape(-1,)
            report = classification_report(y_true=trues, y_pred=preds, digits=4, output_dict=True)
            
            # Extract metrics
            f1_score = report['macro avg']['f1-score']
            accuracy = report['accuracy']
            precision = report['macro avg']['precision']
            recall = report['macro avg']['recall']
            
            # Determine score based on metric
            if self.metric == 'f1_score':
                score = f1_score
            elif self.metric == 'accuracy':
                score = accuracy
            elif self.metric == 'loss':
                score = -vali_loss  # Negative because we want to maximize
            else:
                score = f1_score
            
            result = {
                'trial_id': trial_id,
                'params': params,
                'vali_loss': float(vali_loss),
                'f1_score': float(f1_score),
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'score': float(score),
                'setting': setting
            }
            
            print(f"\nTrial {trial_id} Results:")
            print(f"  F1 Score: {f1_score:.4f}")
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  Validation Loss: {vali_loss:.4f}")
            print(f"  Score ({self.metric}): {score:.4f}\n")
            
            # Clean up
            torch.cuda.empty_cache()
            
            return result
            
        except Exception as e:
            print(f"Error in trial {trial_id} with params {params}: {str(e)}")
            result = {
                'trial_id': trial_id,
                'params': params,
                'error': str(e),
                'score': -np.inf
            }
            torch.cuda.empty_cache()
            return result
    
    def _create_setting_name(self, args, trial_id: int) -> str:
        """
        Create a setting name for the experiment.
        
        Args:
            args: Arguments object
            trial_id: Trial number
            
        Returns:
            Setting name string
        """
        # Handle missing model_id attribute
        model_id = getattr(args, 'model_id', 'grid_search')
        
        setting = '{}_{}_{}_{}_{}_ft{}_sl{}_ll{}_pl{}_dm{}_nh{}_el{}_dl{}_df{}_fc{}_eb{}_dt{}_{}_{}_{}'.format(
            args.level,
            args.enc_in,
            model_id,
            args.model,
            args.data,
            args.features,
            args.seq_len,
            args.label_len,
            args.pred_len,
            args.d_model,
            args.n_heads,
            args.e_layers,
            args.d_layers,
            args.d_ff,
            args.factor,
            args.embed,
            args.des,
            trial_id,
            args.learning_rate
        )
        return setting
    
    def search(self) -> Tuple[Dict[str, Any], float]:
        """
        Perform grid search over all parameter combinations.
        
        Returns:
            Tuple of (best_params, best_score)
        """
        # Generate all parameter combinations
        param_combinations = self._generate_param_combinations()
        total_trials = len(param_combinations)
        
        print(f"\n{'='*80}")
        print(f"Starting Grid Search")
        print(f"Total parameter combinations: {total_trials}")
        print(f"Search space: {self.search_space}")
        print(f"Optimizing metric: {self.metric}")
        print(f"{'='*80}\n")
        
        # Run experiments
        for trial_id, params in enumerate(param_combinations, 1):
            result = self._run_single_experiment(params, trial_id, total_trials)
            self.results.append(result)
            
            # Update best result
            if result.get('score', -np.inf) > (self.best_score or -np.inf):
                self.best_score = result['score']
                self.best_params = params.copy()
                self.best_result = result.copy()
                print(f"\n*** New best result found! ***")
                print(f"Best {self.metric}: {self.best_score:.4f}")
                print(f"Best params: {self.best_params}\n")
            
            # Save intermediate results
            self._save_results()
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"Grid Search Complete!")
        print(f"Total trials: {total_trials}")
        print(f"Best {self.metric}: {self.best_score:.4f}")
        print(f"Best parameters: {self.best_params}")
        print(f"{'='*80}\n")
        
        return self.best_params, self.best_score
    
    def _save_results(self):
        """Save grid search results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.results_dir, f"grid_search_results_{timestamp}.json")
        
        output = {
            'search_space': self.search_space,
            'metric': self.metric,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'best_result': self.best_result,
            'all_results': self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Results saved to: {results_file}")


def get_default_search_space() -> Dict[str, List[Any]]:
    """
    Get default search space for grid search.
    
    Returns:
        Dictionary with default hyperparameter ranges
    """
    return {
        'seq_len': [32, 64, 128],
        'patch_len': [2, 4, 8, 16],
        'stride': [1, 2, 4, 8],
        'factor': [5, 10, 20]
    }


def run_grid_search(base_args, search_space: Dict[str, List[Any]] = None,
                    metric: str = 'f1_score', results_dir: str = './grid_search_results') -> Tuple[Dict[str, Any], float]:
    """
    Convenience function to run grid search.
    
    Args:
        base_args: Base argument namespace
        search_space: Dictionary of hyperparameters to search (if None, uses default)
        metric: Metric to optimize
        results_dir: Directory to save results
        
    Returns:
        Tuple of (best_params, best_score)
    """
    if search_space is None:
        search_space = get_default_search_space()
    
    grid_search = GridSearch(base_args, search_space, metric, results_dir)
    return grid_search.search()

