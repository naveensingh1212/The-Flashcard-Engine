"""
SM-2 Spaced Repetition Algorithm
quality: 0=complete blackout, 1=wrong, 2=wrong but felt familiar,
         3=correct with difficulty, 4=correct, 5=perfect
"""
from datetime import datetime, timedelta

def apply_sm2(card: dict, quality: int) -> dict:
    if not (0 <= quality <= 5):
        raise ValueError("Quality must be 0-5")

    if quality < 3:
        card["repetitions"] = 0
        card["interval_days"] = 1
    else:
        if card["repetitions"] == 0:
            card["interval_days"] = 1
        elif card["repetitions"] == 1:
            card["interval_days"] = 6
        else:
            card["interval_days"] = round(card["interval_days"] * card["ease_factor"])
        card["repetitions"] += 1

    card["ease_factor"] = max(
        1.3,
        card["ease_factor"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )

    card["due_date"] = (datetime.utcnow() + timedelta(days=card["interval_days"])).isoformat()
    card["last_reviewed"] = datetime.utcnow().isoformat()

    if card["repetitions"] == 0:
        card["mastery"] = 0
    elif card["repetitions"] <= 2:
        card["mastery"] = 1
    elif card["interval_days"] < 21:
        card["mastery"] = 2
    else:
        card["mastery"] = 3

    return card