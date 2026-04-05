from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.analysis import (
    build_lab_analysis,
    render_terminal_transcript,
    write_analysis_bundle,
)


def test_build_lab_analysis_covers_all_variants() -> None:
    analysis = build_lab_analysis(
        max_repeat=5,
        max_results=10,
        sample_count=4,
        seed=11,
        benchmark_iterations=1,
    )

    assert analysis["meta"]["variant_count"] == 4
    assert analysis["meta"]["expression_count"] == 12
    assert len(analysis["variants"]) == 4
    assert analysis["variants"][0]["label"] == "variant 1"
    assert len(analysis["variants"][0]["expressions"]) == 3


def test_render_terminal_transcript_mentions_benchmarks_and_validation() -> None:
    analysis = build_lab_analysis(
        max_repeat=5,
        max_results=8,
        sample_count=3,
        seed=5,
        benchmark_iterations=1,
    )

    transcript = render_terminal_transcript(analysis)
    assert "Regular Expressions Lab 4 - analysis transcript" in transcript
    assert "Benchmark:" in transcript
    assert "Validation target:" in transcript


def test_write_analysis_bundle_writes_expected_files(tmp_path: Path) -> None:
    analysis = build_lab_analysis(
        max_repeat=5,
        max_results=8,
        sample_count=3,
        seed=7,
        benchmark_iterations=1,
    )

    write_analysis_bundle(tmp_path, analysis)

    summary_json = tmp_path / "summary.json"
    summary_md = tmp_path / "summary.md"
    transcript_txt = tmp_path / "terminal_transcript.txt"

    assert summary_json.exists()
    assert summary_md.exists()
    assert transcript_txt.exists()

    data = json.loads(summary_json.read_text(encoding="utf-8"))
    assert data["meta"]["variant_count"] == 4


def test_main_can_export_analysis_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "evidence"

    command = [
        sys.executable,
        "4_regular_expressions/main.py",
        "--variant",
        "all",
        "--samples",
        "3",
        "--max-results",
        "8",
        "--validate",
        "--export-analysis-dir",
        str(output_dir),
        "--benchmark-iterations",
        "1",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    assert result.returncode == 0, result.stderr
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "terminal_transcript.txt").exists()
