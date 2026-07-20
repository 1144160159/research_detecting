import unittest

from eacr_apt.alignment import accept_candidate, score_event_pair
from eacr_apt.schema import Event


def make_event(event_id, modality, ts, **kwargs):
    values = dict(
        event_id=event_id,
        ts_utc_ns=ts,
        ts_uncertainty_ns=1_000_000,
        host_id="host-1",
        sensor_id=modality,
        modality=modality,
        event_type="CONNECT",
        actor_id="proc-1",
        object_id="socket-1",
        process_guid="proc-guid-1",
        session_id="session-1",
        src_ip="10.0.0.1",
        src_port=50000,
        dst_ip="10.0.0.2",
        dst_port=443,
        protocol="tcp",
    )
    values.update(kwargs)
    return Event(**values)


class AlignmentTests(unittest.TestCase):
    def test_high_confidence_cross_source_pair(self):
        left = make_event("e1", "endpoint", 1_000_000_000)
        right = make_event("e2", "flow", 1_100_000_000)
        candidate = score_event_pair(left, right)
        accepted, reason = accept_candidate(candidate)
        self.assertTrue(accepted)
        self.assertEqual(reason, "accepted")
        self.assertGreater(candidate.score, 0.8)

    def test_ambiguous_pair_is_rejected(self):
        left = make_event("e1", "endpoint", 1_000_000_000)
        right = make_event("e2", "log", 1_100_000_000)
        candidate = score_event_pair(left, right)
        accepted, reason = accept_candidate(candidate, second_best_score=candidate.score - 0.01)
        self.assertFalse(accepted)
        self.assertEqual(reason, "ambiguous")


if __name__ == "__main__":
    unittest.main()
