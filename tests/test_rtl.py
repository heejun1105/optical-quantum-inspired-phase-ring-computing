import shutil
import subprocess

import pytest

from compare_rtl_reference import compare_results, run_comparison
from phase_ring import ROOT

HAS_ICARUS = bool(shutil.which("iverilog") and shutil.which("vvp"))


@pytest.mark.skipif(not HAS_ICARUS, reason="iverilog/vvp not on PATH; install Icarus to run RTL verification")
@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_actual_rtl_against_python(tmp_path, n_mod):
    assert run_comparison(n_mod, tmp_path) == 2*n_mod + 4136


@pytest.mark.skipif(not HAS_ICARUS, reason="iverilog/vvp not on PATH")
@pytest.mark.parametrize("top", ["tb_pim_phase_adder", "tb_phase_adders"])
def test_self_checking_testbenches(tmp_path, top):
    output = tmp_path / f"{top}.vvp"
    sources = [str(p) for p in sorted((ROOT / "rtl").glob("*.v"))]
    compile_result = subprocess.run(
        ["iverilog", "-g2012", "-Wall", "-s", top, "-o", str(output), *sources,
         str(ROOT / "testbench" / f"{top}.v")], cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    result = subprocess.run(["vvp", str(output)], cwd=ROOT, capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS:" in result.stdout
    assert "ERROR:" not in result.stdout and "WARNING:" not in result.stdout


@pytest.mark.parametrize("result", ["", "0 0 xxxx\n", "0 1 0000\n", "0 0 0000\n1 0 0000\n"])
def test_comparator_rejects_incomplete_unknown_wrong_or_extra_results(tmp_path, result):
    vector_file, result_file = tmp_path / "vectors", tmp_path / "results"
    vector_file.write_text("0 0\n")
    result_file.write_text(result)
    with pytest.raises(AssertionError):
        compare_results(vector_file, result_file, 1024)
