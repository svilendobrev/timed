#$Id$
# -*- coding: cp1251 -*-

# see test_base._Timed2_withDisabled_protocol

class test_protocol2Timed_protocol( object):
    '''testing purposes only'''
    # needs:
    #.timed_get()
    #.timed_put()
    #.timed_getRange()
    #.NOT_FOUND

    @staticmethod
    def _valid_trans2time( valid, trans):
        return (trans,valid)
    @classmethod
    def _valid_trans2time4put( me, valid, trans):
        return me._valid_trans2time( valid=valid, trans=trans)

        # _Timed2_withDisabled_protocol:
    def get( me, trans, valid, with_disabled =False):
        r = me.timed_get(
                me._valid_trans2time( trans=trans, valid=valid),
                with_disabled= with_disabled
        )
        if r is me.NOT_FOUND: return None
        return r
    def getRange( me, trans, validFrom, validTo, with_disabled =False):
        return me.timed_getRange(
                me._valid_trans2time( trans=trans, valid=validFrom),
                me._valid_trans2time( trans=trans, valid=validTo),
                with_disabled= with_disabled
        )
    def put( me, value, trans, valid, disabled =False):
        return me.timed_put( value,
                me._valid_trans2time4put( trans=trans, valid=valid),
                disabled= disabled
        )

#    def __str__( me): return me.__class__.__name__ + '/' + str( me.__get)

# vim:ts=4:sw=4:expandtab
