"""
Tests for the advertising detection pipeline (e02 + e03).

Test files expected in test_files/:
  tf1_1.mp3, tf1_2.mp3  — two audio clips from TF1 (at least one repeated segment)
  tf1_1.mp4, tf1_2.mp4  — same clips in video format

No network calls are made: files are loaded directly from disk.
"""

from datetime import datetime
from pathlib import Path

import pytest

from quotaclimat.data_ingestion.advertising_detection.processor import (
    group_segments,
    segment_audio_file,
)

TEST_FILES = Path(__file__).parent.parent.parent / "test_files"

TF1_MP3_1 = TEST_FILES / "tf1_1.mp3"
TF1_MP3_2 = TEST_FILES / "tf1_2.mp3"
TF1_MP4_1 = TEST_FILES / "tf1_1.mp4"
TF1_MP4_2 = TEST_FILES / "tf1_2.mp4"

START_EPOCH_1 = datetime(2025, 1, 1, 8, 0).timestamp()
START_EPOCH_2 = datetime(2025, 1, 1, 8, 15).timestamp()


# ── Helpers ──────────────────────────────────────────────────────────────────


def requires_file(path: Path):
    return pytest.mark.skipif(
        not path.exists(), reason=f"Test file not found: {path.name}"
    )


# ── e02 : segmentation ────────────────────────────────────────────────────────


@requires_file(TF1_MP3_1)
def test_segmentation_mp3_returns_segments():
    segments = segment_audio_file(str(TF1_MP3_1), START_EPOCH_1)
    assert len(segments) > 0


@requires_file(TF1_MP3_1)
def test_segmentation_mp3_segments_have_hashes():
    segments = segment_audio_file(str(TF1_MP3_1), START_EPOCH_1)
    assert all(seg.hashes is not None for seg in segments)


@requires_file(TF1_MP3_1)
def test_segmentation_mp3_segments_have_valid_timestamps():
    segments = segment_audio_file(str(TF1_MP3_1), START_EPOCH_1)
    for seg in segments:
        assert seg.start_sec < seg.end_sec
        assert seg.duration_sec > 0


@requires_file(TF1_MP4_1)
def test_segmentation_mp4_returns_segments():
    segments = segment_audio_file(str(TF1_MP4_1), START_EPOCH_1)
    assert len(segments) > 0


@requires_file(TF1_MP4_1)
def test_segmentation_mp4_segments_have_hashes():
    segments = segment_audio_file(str(TF1_MP4_1), START_EPOCH_1)
    assert all(seg.hashes is not None for seg in segments)


# ── e03 : grouping ────────────────────────────────────────────────────────────


@pytest.mark.skipif(
    not TF1_MP3_1.exists() or not TF1_MP3_2.exists(),
    reason="Test files tf1_1.mp3 and tf1_2.mp3 not found",
)
def test_grouping_mp3_finds_repeated_segments():
    segments_1 = segment_audio_file(str(TF1_MP3_1), START_EPOCH_1)
    segments_2 = segment_audio_file(str(TF1_MP3_2), START_EPOCH_2)

    groups = group_segments([segments_1, segments_2])

    repeated = [g for g in groups if g["count"] > 1]
    assert len(repeated) > 0, "Expected at least one repeated segment group across the two files"


@pytest.mark.skipif(
    not TF1_MP4_1.exists() or not TF1_MP4_2.exists(),
    reason="Test files tf1_1.mp4 and tf1_2.mp4 not found",
)
def test_grouping_mp4_finds_repeated_segments():
    segments_1 = segment_audio_file(str(TF1_MP4_1), START_EPOCH_1)
    segments_2 = segment_audio_file(str(TF1_MP4_2), START_EPOCH_2)

    groups = group_segments([segments_1, segments_2])

    repeated = [g for g in groups if g["count"] > 1]
    assert len(repeated) > 0, "Expected at least one repeated segment group across the two files"
