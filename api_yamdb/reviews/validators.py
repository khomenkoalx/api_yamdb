from django.core.validators import MaxValueValidator
from django.utils import timezone


class CurrentYearMaxValueValidator(MaxValueValidator):
    def __init__(self, message=None):
        super().__init__(limit_value=timezone.now().year, message=message)

    def __call__(self, value):
        self.limit_value = timezone.now().year
        super().__call__(value)
