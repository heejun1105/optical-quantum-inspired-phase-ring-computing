from pathlib import Path
import runpy
import subprocess
import sys

import pytest

from phase_ring import ROOT


@pytest.mark.parametrize("name", ["basic_phase_addition.py", "image_lut_example.py"])
def test_examples_run_outside_repo(tmp_path, name):
    result = subprocess.run([sys.executable, str(ROOT / "examples" / name)], cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


def test_image_demo_endpoints_and_bounds():
    demo = runpy.run_path(str(ROOT / "examples" / "image_lut_example.py"))
    assert demo['process_rgb']((0, 0, 0)) == (0, 0, 0)
    assert demo['process_rgb']((255, 255, 255)) == (255, 255, 255)
    with pytest.raises(ValueError):
        demo['pixel_to_phase'](256)
