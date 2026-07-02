# OIPR

Repository  for the Operator Interest-based Precision and Recall metrics, which are developed by the State Key Laboratory of Networking and Switching Technology, Beijing University of Posts and Telecommunications.

Using the following codes to calculated the *OIPR* metrics:

```
from evaluation_methods import evaluate_OIPR
OIPR_config = {'l_dis': 5, 'l_obs': 20, 'b_dur': 0.5}
precision, recall, f1_score = evaluate_OIPR(gt, pred, **OIPR_config)
```

*OIPR* is a set of evaluation metrics for Time-series Anomaly Detection (TAD) based on the operator interest. It utilizes the area under the operator interest curve to assess the Precision, Recall, and F1-score of anomaly detectors. You can configure this evaluation method by adjusting the following three parameters:

* Discovery period length (l_dis): The number of sampling intervals within which an anomaly detector needs to detect an anomaly event to be considered "timely". This parameter can be set to "auto" to adaptively match the lengths of anomaly events in the time-series.
* Observation period length (l_obs): The number of sampling intervals that need to be observed after an anomaly detector reports an anomaly point, or an anomaly event is resolved to confirm that the time-series is normal or has returned to normal. This parameter can be set to "auto" to adaptively match the lengths of anomaly events in the time-series.
* Upper bound of interest for the duration period (b_dur): If the anomaly detector fails to detect the anomaly event "timely" within the discovery period but still detects the anomaly during this event, to what extent such an anomaly report is considered "useful".

For more detailed explanations regarding the characteristics and parameter configuration of OIPR, please refer to the corresponding paper by the authors.

When using *OIPR* evaluation metrics, please cite the following reference:

Jing, Y., Wang, J., Zhang, L., Sun, H., He, B., Zhuang, Z., Wang, C., Qi, Q., Liao, J. (2025). OIPR: Evaluation for Time-series Anomaly Detection Inspired by Operator Interest. arXiv preprint arXiv:2503.01260.

