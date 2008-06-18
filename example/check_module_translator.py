#$Id$
# -*- coding: cp1251 -*-

##################### module_timed, translator, Timed2
#either run from inside tests/ or set PYTHONPATH=tests/ or this below:
#sys.path.append( 'tests/')
import module_timed
from datetime import datetime, timedelta

from timed2 import Timed2
class Timed2dict( Timed2):
    def time2key_valid_trans( me, time):            return (time['valid'], time['trans'])
    def key_valid_trans2time( me, (trans, valid)):  return dict( trans=trans, valid=valid)
    NOT_FOUND = None

class Customer:
    def __init__( me):
        me.name = Timed2dict()
        me.salary = Timed2dict()
    def get( me, time):
        return dict(
            name   = me.name.get( time),
            salary = me.salary.get( time),
        )
from translator import Translator
def dod_calculate( customer, dod, time):
    t = Translator( time, salary=customer.salary, dod=dod, name=customer.name)
    return t.dod and t.dod.dod( t.salary) or 0, t.salary, t.name

Converter = module_timed.mod2time__all_in_fname___trans_valid
class mod2time__converter( Converter):
    str2time1 = staticmethod( module_timed.dateYYYYMMDD2datetime)
    def maketime( me, trans, valid): return dict( trans=trans, valid=valid)

DOD = module_timed.Module( 'dod2', Timed2dict, mod2time__converter)

print DOD
c = Customer()
c.name.put( 'myname', dict( trans=datetime(2006,1,2), valid=datetime(2006,1,2)))
c.salary.put( 333,    dict( trans=datetime(2006,2,2), valid=datetime(2006,2,2)))
c.salary.put( 500,    dict( trans=datetime(2006,5,2), valid=datetime(2006,5,2)))
c.salary.put( 2000,   dict( trans=datetime(2006,5,22),valid=datetime(2006,6,2)))
c.name.put( 'another',dict( trans=datetime(2006,8,2), valid=datetime(2006,9,2)))
one_u = timedelta( seconds=1)
for i in range(1, 13):
    dt = datetime(2006, i, 1) - one_u
    print dt, dod_calculate( c, DOD, dict( trans=dt, valid=dt) )

# vim:ts=4:sw=4:expandtab
