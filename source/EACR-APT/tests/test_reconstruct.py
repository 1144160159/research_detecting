import unittest

from eacr_apt.reconstruct import (
    ChainEvidence,
    ChainScoreWeights,
    beam_search_paths,
    score_chain,
)


class ReconstructionTests(unittest.TestCase):
    def test_score_penalizes_noise_and_redundancy(self):
        weights = ChainScoreWeights()
        clean = ChainEvidence(1, 1, 1, 1, 1, 0, 0)
        noisy = ChainEvidence(1, 1, 1, 1, 1, 0.5, 0.5)
        self.assertGreater(score_chain(clean, weights), score_chain(noisy, weights))

    def test_beam_search_is_acyclic_and_ranked(self):
        graph = {
            "seed": (("a", 0.8), ("b", 0.2)),
            "a": (("goal", 0.9), ("seed", 9.0)),
            "b": (("goal", 0.3),),
        }
        paths = beam_search_paths(graph, "seed", max_hops=3, beam_width=5)
        self.assertEqual(paths[0][0], ("seed", "a", "goal"))
        self.assertEqual(len(paths[0][0]), len(set(paths[0][0])))


if __name__ == "__main__":
    unittest.main()
