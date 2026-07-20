import unittest

from eacr_apt.schema import ChainGroundTruth, Event


class SchemaTests(unittest.TestCase):
    def test_event_round_trip(self):
        event = Event(
            event_id="e1",
            ts_utc_ns=100,
            ts_uncertainty_ns=5,
            host_id="h1",
            sensor_id="sysmon",
            modality="endpoint",
            event_type="PROCESS_START",
            actor_id="p0",
            object_id="p1",
            src_port=443,
        )
        restored = Event.from_mapping(event.to_dict())
        self.assertEqual(event, restored)

    def test_ground_truth_is_separate(self):
        truth = ChainGroundTruth("c1", "campaign-1", ("e1",), ("TA0001",), "manifest.json")
        self.assertEqual(truth.event_ids, ("e1",))
        self.assertNotIn("campaign_id", Event.__dataclass_fields__)

    def test_invalid_modality_rejected(self):
        with self.assertRaises(ValueError):
            Event("e1", 1, 0, "h", "s", "truth", "x", "a", "o")


if __name__ == "__main__":
    unittest.main()
