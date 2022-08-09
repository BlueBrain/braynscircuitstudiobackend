import os.path

from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class PathFileValidator:
    def __call__(self, value):
        logger.debug(f"Validating path file: {value}")

        if not (os.path.isfile(value) and os.path.exists(value)):
            raise ValidationError(f"This path `{value}` does not exist.")
