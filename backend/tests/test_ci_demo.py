"""Throwaway test for the M0.5 CI demo PR. Never merged."""


def test_ci_demo_passes() -> None:
    assert 1 + 1 == 2


def test_ci_demo_fails_on_purpose() -> None:
    assert 1 + 1 == 3, "deliberate failure: CI must turn red"
