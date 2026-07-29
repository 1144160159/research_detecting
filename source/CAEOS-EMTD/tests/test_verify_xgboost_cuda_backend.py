from verify_xgboost_cuda_backend import find_device_values


def test_find_device_values_recurses() -> None:
    value = {
        "learner": {
            "generic_param": {"device": "cuda:0"},
            "gradient_booster": [{"device": "cpu"}],
        }
    }
    assert find_device_values(value) == ["cuda:0", "cpu"]
