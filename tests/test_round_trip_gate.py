"""Review F12: evidence checks survive Python optimization and reject absent hooks/saves."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parent/'round-trip.py'
spec=importlib.util.spec_from_file_location('round_trip_gate',SCRIPT)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

class GateControls(unittest.TestCase):
    def test_optimization_cannot_remove_the_validation(self):
        code='import importlib.util; s=importlib.util.spec_from_file_location("gate",'+repr(str(SCRIPT))+'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.require(False,"negative")'
        result=subprocess.run(['python3','-O','-c',code],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('negative',result.stderr)
    def test_missing_replay_save_and_missing_hook_families_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaisesRegex(RuntimeError,'no final engine save'):gate.save_hashes(root)
            (root/'frames.jsonl').write_text(json.dumps({'turn':81,'phase':'exit'})+'\n')
            with self.assertRaises(RuntimeError):gate.validate_channels(root)
