import logging
import os
import re
from collections import Counter

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from .conf import settings

logger = logging.getLogger(__name__)


@deconstructible
class ChunkerParameterValidator(object):
    """
    Validate Borg chunker parameters
    """

    message = _("Not a valid chunker parameter list")
    code = "invalid"

    def __call__(self, data):
        try:
            if len(map(int, data.split(","))) != settings.BORG_CHUNKER_PARAMETER_COUNT:
                raise ValidationError(self.message, code=self.code)
        except ValueError:
            raise ValidationError(self.message, code=self.code)


@deconstructible
class CompressionValidator(object):
    """
    Validate Borg compression parameters
    """

    message = _("Not a valid chunker parameter list")
    code = "invalid"
    pattern = re.compile(
        r"^(?:(?P<auto>auto)?,?)?(?:(?P<method>(?:none|lz4|zstd|zlib|lzma))(?:,(?P<level>\d+))?)$"
    )
    methods = {
        "none": None,
        "lz4": None,
        "zstd": range(1, 22),
        "zlib": range(0, 9),
        "lzma": range(0, 9),
    }

    def __call__(self, data):
        matches = self.pattern.fullmatch(data)
        if not matches:
            raise ValidationError(self.message, code=self.code)

        method = matches.groupdict().get("method")
        level = matches.groupdict().get("level")

        if not level:
            return

        values = self.methods.get(method)

        if not values:
            raise ValidationError(self.message, code=self.code)

        if int(level) not in values:
            raise ValidationError(self.message, code=self.code)


@deconstructible
class PatternValidator(object):
    """
    Validate Borg patterns
    """

    invalid = _("Not a valid pattern on line {lnr}: {line}")
    wildcards = _("Too many wildcards on line {lnr}: {line}")
    code = "invalid"
    pattern = re.compile(
        r"^(?P<rule>(?:P|R|\+|-|!))\s+(?P<value>.*?)(?:\s*#(?P<comment>.*))?$"
    )

    def __call__(self, data):
        for lnr, line in enumerate(
            (line.lstrip() for line in data.split(os.linesep)), start=1
        ):
            # Ignore empty lines
            if not line:
                continue
            # Ignore comments
            if line.startswith("#"):
                continue
            matches = self.pattern.fullmatch(line)
            if not matches:
                raise ValidationError(
                    self.message.format(lnr=lnr, line=line), code=self.code
                )

            value = matches.groupdict().get("value")

            if Counter(value).get("*", 0) > settings.BORG_PATTERN_WILDCARD_LIMIT:
                raise ValidationError(
                    self.wildcards.format(lnr=lnr, line=line), code=self.code
                )
