from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GpuServiceLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "scripts/start_gpu_service.sh").read_text(
            encoding="utf-8"
        )

    def test_launches_the_frozen_environment_interpreter_directly(self):
        self.assertIn('PYTHON_BIN="${PYTHON_BIN:-', self.source)
        self.assertIn('"${PYTHON_BIN}" -m hft_mgbs.gpu_service', self.source)
        self.assertNotIn("run --no-capture-output", self.source)

    def test_listener_owner_is_the_recorded_service_pid(self):
        self.assertIn('observed_listener_pid="$(listener_pid)"', self.source)
        self.assertIn('"${observed_listener_pid}" != "${pid}"', self.source)
        self.assertIn('is_expected_service_pid "${pid}"', self.source)

    def test_pid_and_manifest_are_published_atomically_after_readiness(self):
        ready = self.source.index("observed_listener_pid")
        manifest_move = self.source.index('mv -f "${manifest_tmp}"')
        pid_move = self.source.index('mv -f "${pid_tmp}"')
        self.assertLess(ready, manifest_move)
        self.assertLess(manifest_move, pid_move)
        self.assertIn("startup_complete=1", self.source)

    def test_restart_refuses_unverified_listener_ownership(self):
        self.assertIn("port ${bind_port} belongs to an unverified process", self.source)
        self.assertIn("stale PID file names a live unrelated process", self.source)
        self.assertIn("has_exact_pair --model", self.source)

    def test_runtime_manifest_binds_live_process_identity(self):
        for field in (
            '"schema_version": 2',
            '"process_group_id"',
            '"process_start_ticks"',
            '"python_executable"',
            '"working_directory"',
            '"command_sha256"',
            '"model_sha256"',
            '"service_source_sha256"',
            '"numpy_engine_source_sha256"',
            '"launcher_sha256"',
            '"inference_engine"',
        ):
            self.assertIn(field, self.source)

    def test_numpy_engine_is_explicit_opt_in_and_command_bound(self):
        self.assertIn('INFERENCE_ENGINE="${INFERENCE_ENGINE:-sklearn}"', self.source)
        self.assertIn('--inference-engine "${INFERENCE_ENGINE}"', self.source)
        self.assertIn('has_exact_pair --inference-engine', self.source)

    def test_current_279_inline_cpu6_is_the_only_single_cpu_candidate(self):
        self.assertIn('inline:6) RUNTIME_CANDIDATE="inline_cpu6"', self.source)
        self.assertNotIn('thread:6) RUNTIME_CANDIDATE=', self.source)
        for cpu in range(0, 6):
            self.assertNotIn(
                f'inline:{cpu}) RUNTIME_CANDIDATE="inline_cpu{cpu}"', self.source
            )
        for cpu in range(7, 80):
            self.assertNotIn(
                f'inline:{cpu}) RUNTIME_CANDIDATE="inline_cpu{cpu}"', self.source
            )

    def test_command_hash_preserves_null_argument_boundaries(self):
        self.assertIn('sha256sum "/proc/${pid}/cmdline"', self.source)
        self.assertNotIn("tr '\\0' '\\n'", self.source)

    def test_signals_recheck_pid_start_time_and_cleanup_partial_files(self):
        self.assertIn("process_start_ticks", self.source)
        self.assertIn("same_process", self.source)
        self.assertIn('rm -f "${manifest_tmp}" "${pid_tmp}"', self.source)
        self.assertIn("trap 'exit 143' TERM", self.source)
        self.assertIn('kill -KILL "${pid}"', self.source)

    def test_dead_stale_pidfile_is_a_normal_empty_start_ticks_case(self):
        function_start = self.source.index("process_start_ticks()")
        function_end = self.source.index("\n}\n", function_start)
        function = self.source[function_start:function_end]
        self.assertIn('[[ -r "/proc/${candidate_pid}/stat" ]] || return 0', function)
        self.assertIn("2>/dev/null || true", function)

    def test_legacy_wrapper_must_match_conda_command_and_listener_ancestry(self):
        self.assertIn("is_legacy_conda_wrapper_pid", self.source)
        self.assertIn('[[ "${old_pid_owns_listener}" != "true"', self.source)
        self.assertIn('|| "${old_pid_legacy_verified}" != "true"', self.source)

    def test_convenience_link_mutation_follows_all_refusal_gates(self):
        refusal = self.source.index("stale PID file names a live unrelated process")
        symlink = self.source.index('ln -sfn "${MODEL_DIR}"')
        self.assertLess(refusal, symlink)


if __name__ == "__main__":
    unittest.main()
