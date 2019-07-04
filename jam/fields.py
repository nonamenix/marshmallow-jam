from datetime import datetime, time, date, timedelta

from marshmallow.fields import DateTime, Time, Date, TimeDelta


class WithIdentityMixin:
    identity_type: type

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, self.identity_type):
            return value
        return super()._deserialize(value, attr, data, **kwargs)


class DateTimeIdentity(WithIdentityMixin, DateTime):
    identity_type = datetime


class TimeIdentity(WithIdentityMixin, Time):
    identity_type = time


class DateIdentity(WithIdentityMixin, Date):
    identity_type = date


class TimeDeltaIdentity(WithIdentityMixin, TimeDelta):
    identity_type = timedelta
