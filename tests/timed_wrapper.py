#$Id$
# -*- coding: cp1251 -*-
from disabled import Disabled4Timed
from protocol import test_protocol2Timed_protocol

class Timed2_Wrapper4Disabled( Disabled4Timed, test_protocol2Timed_protocol):
    '''testing purposes only'''
    def __init__( me, timed ):
        me.val = timed()
        me.NOT_FOUND = timed.NOT_FOUND

        # test_protocol2Timed_protocol:
    timed_get = Disabled4Timed._get
    timed_put = Disabled4Timed._put
    timed_getRange = Disabled4Timed._getRange

        # Disabled4Timed protocol:
    def _get_val( me, time, **kargs):   return me.val.get( time, **kargs )
    def _get_range_val( me, timeFrom, timeTo, **kargs): return me.val.getRange( timeFrom, timeTo, **kargs ) #not quite clear, but works
    def _put_val( me, value, time):     return me.val.put( value, time)

# vim:ts=4:sw=4:expandtab
