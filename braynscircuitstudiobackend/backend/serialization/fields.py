import os

from marshmallow import fields, ValidationError


class FilePathField(fields.String):
    def _validate(self, value):
        if not (os.path.isfile(value) and os.path.exists(value)):
            raise ValidationError(f"This path `{value}` does not exist.")
