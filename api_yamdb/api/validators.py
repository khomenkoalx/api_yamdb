from django.core.exceptions import ValidationError

from .constants import MIN_SCORE, MAX_SCORE


def validate_score(value):
    if not (MIN_SCORE <= value <= MAX_SCORE):
        raise ValidationError(f'Оценка должна быть от {MIN_SCORE} до {MAX_SCORE}')
    return value
