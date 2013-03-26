from __future__ import absolute_import

import datetime
from time import mktime

try:
    from dateutil.tz import tzutc, tzlocal
except ImportError:
    raise ImportError(
        'Using the datetime fields requires the dateutil library. '
        'You can obtain dateutil from http://labix.org/python-dateutil'
    )

from .base import DateTimeType


class TimeStampType(DateTimeType):
    """Variant of a datetime field that saves itself as a unix timestamp (int)
    instead of a ISO-8601 string.
    """

    def convert(self, value):
        """Will try to parse the value as a timestamp.  If that fails it
        will fallback to DateTimeType's value parsing.

        A datetime may be used (and is encouraged).
        """
        if isinstance(value, datetime.datetime):
            return value
        try:
            return TimeStampType.timestamp_to_date(float(value))
        except (TypeError, ValueError):
            pass
        return super(TimeStampType, self).convert(value)

    @classmethod
    def timestamp_to_date(cls, value):
        return datetime.datetime.fromtimestamp(value, tz=tzutc())

    @classmethod
    def date_to_timestamp(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=tzlocal())
        return int(round(mktime(value.astimezone(tzutc()).timetuple())))

    def to_primitive(self, value):
        return TimeStampType.date_to_timestamp(value)
