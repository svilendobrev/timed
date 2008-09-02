#$Id$
# -*- coding: cp1251 -*-

from setup import TimeContext, USE_date
USE_date()

default_symbol  = 'default'
now_symbol      = 'now'
time = TimeContext.Time
class revLog_obj: pass
class revLog_id: pass

priority_ascend = [
    ( default_symbol,),
    ( now_symbol,),
    ( time, time(2008,1,1)),
    ( revLog_obj, revLog_obj()),
    ( revLog_id,  revLog_id()),
]

tip2stoinost = {
    default_symbol: default_symbol,
    now_symbol  : now_symbol,
    time        : time( 2008,1,1),
    revLog_obj  : revLog_obj(),
    revLog_id   : revLog_id(),
}

valid_allowed = [ len(kv)==1 and kv or kv[1]  for kv in priority_ascend[2:3] ]
trans_allowed = [ len(kv)==1 and kv or kv[1]  for kv in priority_ascend[2:3] ]
#trans_allowed = [ tip2stoinost[ x] for x in priority_ascend[2:3] ]


###################################

from engine.test_engine import *

class Sample( SampleBase):
    def __init__( me, tcargs =(), tckargs ={}, normalized =False, **kargs):
        SampleBase.__init__( me, **kargs)
        me.args = tcargs
        me.kargs = tckargs
        me.normalized = normalized


def norm( (trans, valid)):
    return trans_allowed[ -1], valid_allowed[-1]


class Case( myTestCase4Function, unittest.TestCase):
    def do( me, v, expect):
        try: tc = TimeContext( *v.args, **v.kargs)
        except Exception, e:
            return e.__class__
        if v.normalized:
            tc.normalize()
        res = tc.as_trans_valid()
        if v.normalized:
            return norm( res)
        return res

error = TypeError
error2= AssertionError

class Test_TimeContext( TestBase):
    TESTOVE = []
    case = Case
    for valid in valid_allowed + [None]:
        for trans in trans_allowed + [None]:
            for args in ( [trans,valid], [valid,trans], [trans], [valid], [] ):
                for kargs in ( dict( trans=trans), dict( valid=valid), dict() ):
                    TESTOVE.append( Sample( tcargs=args, tckargs=kargs,
                                    expect=error, info='greshen nachin na initializacia'))

    if 10:
        wrong_trans = [ None, 'boza', 13, object, '']
        wrong_valid = list(set( trans_allowed) - set( valid_allowed)) + wrong_trans
        for stoinosti in [ trans_allowed, wrong_trans]:
            err = stoinosti is wrong_trans
            for trans in stoinosti:
                for valid in valid_allowed:
                    TESTOVE.append( Sample( tckargs= dict( trans=trans, valid=valid),
                                    normalized= False,
                                    expect= err and error2 or (trans, valid),
                                    info= 'upotreba BEZ normalizacia'))
                    TESTOVE.append( Sample( tckargs= dict( trans=trans, valid=valid),
                                    normalized= True,
                                    expect= err and error2 or norm( (trans, valid)),
                                    info= 'normalizirana upotreba'))

                for valid in wrong_valid:
                    for normalized in ( False, True ):
                        TESTOVE.append( Sample( tckargs= dict( trans=trans, valid=valid),
                                    normalized= normalized,
                                    expect= error2, info= 'greshen tip na valid'))


if __name__ == '__main__':
    test = TestMainframe( module = 'timecontext')
    test.runTest()

# vim:ts=4:sw=4:expandtab
