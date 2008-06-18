#$Id$
# -*- coding: cp1251 -*-

NEED_DEFAULT_CONTEXT = 1
from timecontext import TimeContext

from util.stacks import Stack
#from util.stacks import StackPerThread as Stack

#maybe import all visible stuff here?
#from objects    import TimedObject, TimedModule
#from translator import Translator, Translator1

# този обект държи началния NEED_DEFAULT_CONTEXT.
class _default: pass

def setup( Time, now, Delta, isTime =None, isTransTime =None ):
    '''връща този обект (т.е. наследниците му) прави и държи началния NEED_DEFAULT_CONTEXT.
    след изчезването на този обект, стекът трябва да е празен.
    може и трябва да има точно един такъв обект - иначе се прави нов стек ...
    '''
    TimeContext.Time  = Time
    TimeContext.Delta = Delta
    TimeContext.now   = now
    TimeContext.isTime = isTime or TimeContext._isTime
    TimeContext.isTransTime = isTransTime or TimeContext._isTransTime

    '''един единствен текущ времеви контекст - и всички го ползват.
        освен ако трябват успоредни контексти... едва ли.
    '''
    TimeContext.stack = Stack( 'time', type= TimeContext)

    if NEED_DEFAULT_CONTEXT:
        _now = TimeContext.now()
        _default._default = TimeContext.stack.new( trans= _now, valid= _now )

#new  = stack.new
#push = stack.push
#current = get = last = stack.last


def USE_datetime():
    from datetime import datetime, timedelta
    return setup(
        Time  = datetime,
        now   = datetime.now,
        Delta = timedelta,
    )
def USE_date():
    from datetime import date, timedelta
    return setup(
        Time  = date,
        now   = date.today,
        Delta = timedelta,
    )

def _setup4iso( Time, now ):
    from datetime import timedelta

    def isTime( klas, time): return isinstance( time, klas.Time._base )
    isTime = classmethod( isTime)
    return setup(
        Time  = Time,
        now   = now,
        Delta = timedelta,
        isTime = isTime,
        isTransTime = isTime,
    )

def USE_datetime4iso():
    from util.datetimez import datetime
    return _setup4iso(
        Time  = datetime,
        now   = datetime.now,
    )
def USE_date4iso():
    from util.datetimez import date
    return _setup4iso(
        Time  = date,
        now   = date.today,
    )

def USE_str_yyyymmdd():
    Delta = int
    class Time( str):       #XXX HACK HACK just to play
        def __iadd__(me, i):
            if isinstance( i, Delta): return me.__class__( Delta( me)+i )
            return me.__class__( str.__iadd__( me,i))
        def __isub__(me, i):
            assert isinstance( i, Delta)
            return me.__class__( Delta( me)-i )

    def isTime( klas,time):    #yyyymmdd
        return isinstance( time, klas.Time ) and len( time)==8 and time.isdigit()

    return setup(
        Time  = Time,
        now   = staticmethod( lambda : Time( '20060529') ),
        Delta = Delta,
        isTime = classmethod( isTime)
    )

def USE_int():
    return setup(
        Time  = int,
        now   = staticmethod( lambda : 351 ),
        Delta = int,
    )



if __name__ == '__main__':
    def test():
        print TimeContext.Time, 'now()=', TimeContext.now
        _now = TimeContext.now()
        print '  now:', _now, type(_now)

    for f in [
            USE_int,
            USE_str_yyyymmdd,
            USE_date,
            USE_datetime,
            USE_datetime4iso,
            USE_date4iso,
        ]:
        f()
        test()

# vim:ts=4:sw=4:expandtab
