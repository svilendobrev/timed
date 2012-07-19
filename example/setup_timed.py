#$Id: setup_timed.py 8270 2009-04-10 13:14:04Z stefanb $

#### setup Timed/TimeContext/UniversalTime
from engine.basedb import base # engine.timed.setup

#setup converter of UniversalTime to TimeContext.Time
from svd_util.vreme import UniversalTime
from timed.timecontext import TimeContext
UniversalTime.to_timecontext_time = dict(
        valid = lambda me: me.exact_time.date(),
        trans = lambda me: me.exact_time,
    )   #XXX different types in TimeContext for valid and trans

from timed.timecontext import _Timed2overTimeContext
class Timed2( _Timed2overTimeContext):
    TIME_CLASS4check = TimeContext.Time

# vim:ts=4:sw=4:expandtab
