import pytest
from app.prompt_builder import build_prompt, MAX_DIFF_LINES


def test_build_prompt_includes_title():
    prompt = build_prompt("+ foo = 1", "Fix null check", "")
    assert "Fix null check" in prompt


def test_build_prompt_truncates_long_diff():
    long_diff = "\n".join([f"+ line {i}" for i in range(MAX_DIFF_LINES + 100)])
    prompt = build_prompt(long_diff, "Big PR", "")
    assert "truncated" in prompt


def test_build_prompt_includes_diff():
    diff = "+ def hello(): pass"
    prompt = build_prompt(diff, "title", "body")
    assert "def hello" in prompt
