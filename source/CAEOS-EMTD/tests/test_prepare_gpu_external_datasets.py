import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from prepare_gpu_external_datasets import (
    SeedReservoir,
    categorical_number,
    numeric_value,
    prepare_dataset,
    write_prepared,
)


class PrepareGpuExternalDatasetsTests(unittest.TestCase):
    def test_numeric_conversion_is_finite_and_stable(self) -> None:
        self.assertEqual(numeric_value("0x10"), 16.0)
        self.assertEqual(numeric_value("nan"), 0.0)
        self.assertEqual(categorical_number("TCP"), categorical_number("TCP"))

    def test_reservoir_limits_groups_and_rows(self) -> None:
        state = SeedReservoir(seed=223, groups_per_label=2, rows_per_group=2)
        for group in ("0" * 64, "1" * 64, "2" * 64):
            for index in range(5):
                if state.consider_group("attack", group):
                    state.consider_row(
                        label="attack",
                        group=group,
                        member="a.csv",
                        row_index=index,
                        row={"x": float(index), "Flow_Group": group, "Attack": "attack"},
                    )
        summary = state.summary()
        self.assertEqual(summary["groups_per_label"]["attack"], 2)
        self.assertEqual(summary["rows_per_label"]["attack"], 4)

    def test_small_lsnm_archive_prepares_three_seed_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path = root / "lsnm.zip"
            header = [
                "Time",
                "Source",
                "Destination",
                "Protocol",
                "Length",
                "frame length",
                "IP Length",
                "IP TTL",
                "IP Fragment Offset",
                "IP Protocol",
                "IP Version",
                "IP DSCP Field",
                "ICMP Type",
                "TCP Source Port",
                "TCP Destination Port",
                "TCP Length",
                "TCP Sequence Number",
                "TCP Acknowledgment Number",
                "TCP Flags",
                "TCP SYN Flag",
                "TCP ACK Flag",
                "TCP FIN Flag",
                "TCP RST Flag",
                "TCP Window Size",
                "UDP Source Port",
                "UDP Destination Port",
                "UDP Length",
                "HTTP Content-Length",
                "HTTP Response Code",
                "DNS Query Type",
                "HTTP Request Method",
                "HTTP Request URI",
                "HTTP Host",
                "HTTP Cookie",
                "DNS Query Name",
            ]
            rows = []
            for index in range(6):
                values = [""] * len(header)
                mapping = dict(zip(header, range(len(header))))
                values[mapping["Time"]] = str(index)
                values[mapping["Source"]] = f"10.0.0.{index + 1}"
                values[mapping["Destination"]] = "10.0.1.1"
                values[mapping["Protocol"]] = "6"
                values[mapping["Length"]] = "100"
                values[mapping["frame length"]] = "100"
                values[mapping["IP Protocol"]] = "6"
                rows.append(",".join(values))
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "Dataset-Ready (Use This)/Benign/normal_data.csv",
                    ",".join(header) + "\n" + "\n".join(rows) + "\n",
                )
            config = {
                "label_column": "Attack",
                "group_column": "Flow_Group",
                "modalities": {"m": ["Length", "Packet Time Delta", "Has HTTP Method"]},
            }
            outputs, summary = prepare_dataset(
                dataset="LSNM2024",
                archive_paths=[archive_path],
                config=config,
                seeds=[223, 227, 229],
                groups_per_label=4,
                rows_per_group=1,
            )
            self.assertEqual(set(outputs), {223, 227, 229})
            self.assertTrue(all(len(rows) == 4 for rows in outputs.values()))
            manifest = write_prepared(
                dataset="LSNM2024",
                outputs=outputs,
                summary=summary,
                config=config,
                output_root=root / "prepared",
                provenance={"test": True},
            )
            self.assertTrue(manifest["passed"])
            sidecar = json.loads(
                (root / "prepared/LSNM2024/seed223.csv.json").read_text(encoding="utf-8")
            )
            self.assertEqual(sidecar["groups_per_label"]["normal"], 4)


if __name__ == "__main__":
    unittest.main()
