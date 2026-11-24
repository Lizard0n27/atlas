from project.project import check_goal, compute_trends, generate_recommendation
import pytest


def test_check_goal_valid():
    assert check_goal("lose") == "lose"
    assert check_goal("GAIN") == "gain"


def test_check_goal_invalid():
    with pytest.raises(ValueError):
        check_goal("bulk")


def test_compute_trends():
    entries = [
        ("2026-07-28", 80.0, 2500, 1),
        ("2026-07-27", 80.5, 2600, 0),
        ("2026-07-26", 81.0, 2400, 1),
    ]
    trends = compute_trends(entries)
    assert round(trends["avg_weight"], 2) == 80.5
    assert round(trends["avg_calories"], 2) == 2500
    assert trends["days_trained"] == 2
    assert round(trends["weight_change"], 2) == -1.0


def test_generate_recommendation_lose():
    recs = generate_recommendation("lose", 0.2, 2600, 2, 2400)
    assert "Reduce calories slightly." in recs[0] or "too high for losing" in " ".join(recs)
