from pathlib import Path

import pytest

from download_sharepoint_folder import api_path, safe_relative_path


def test_api_path_encodes_spaces_and_dollar_suffix() -> None:
    result = api_path(
        "GetFileByServerRelativeUrl",
        "/personal/user/Documents/TON_IoT datasets/ReadMe.pdf",
        "/%24value",
    )
    assert result == (
        "/_api/web/GetFileByServerRelativeUrl(%27/personal/user/Documents/"
        "TON_IoT%20datasets/ReadMe.pdf%27)/%24value"
    )


def test_safe_relative_path_preserves_dataset_tree() -> None:
    result = safe_relative_path(
        "/personal/user/Documents/TON_IoT datasets",
        "/personal/user/Documents/TON_IoT datasets/Raw_datasets/"
        "network_data/capture.pcap",
    )
    assert result == Path("Raw_datasets/network_data/capture.pcap")


def test_safe_relative_path_rejects_outside_item() -> None:
    with pytest.raises(ValueError, match="outside requested root"):
        safe_relative_path(
            "/personal/user/Documents/TON_IoT datasets",
            "/personal/user/Documents/Other/file.zip",
        )
