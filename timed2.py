#$Id$
# -*- coding: cp1251 -*-

from timed1 import Timed1
import bisect

def range_date( dateFrom, dateTo):
    'like range(3,5) but for dates'
    from datetime import timedelta
    tdelta = dateTo - dateFrom
    result = [dateFrom + timedelta( days) for days in range( tdelta.days+1)] #+1 same as stepper; list compr. or gener. expr.???
    return result

import operator
class Timed2( Timed1):
    '''
    2-времева история върху 1-времева.
    key_valid_trans2time() / time2key_valid_trans() служат за преобразуване на
    външното "2време" - по подразбиране tuple(timeTrans, timeValid) -  към/от
    вътрешното 2време (вальор,транзакция), и може да се заместят.

    bi-temporal over 1-temporal.
    key_valid_trans2time() / time2key_valid_trans() are used to convert the
    external "2time" - by default tuple(timeTrans,timeValid) - to/from the
    internal 2time (valid,trans), and can be overloaded.
    '''

    #тези може да се подменят - преводачи от/към ключа и външното време
    #by default, time=(trans,valid)
    @staticmethod
    def key_valid_trans2time( tkey):
        timeValid, timeTrans = tkey
        return timeTrans,timeValid
    @staticmethod
    def time2key_valid_trans( time):
        timeTrans, timeValid = time
        return timeValid,timeTrans

    #internal key is made from internal 2time (v,t) by adding (another) stepper
    #in the middle - see timed1.put for explanation of steppers.
    #It is needed to allow searching for items BEFORE (timeValid,*)
    #without touching timeTrans, i.e. represent transFrom=ZERO without knowing what time is.
    #
    #вътрешен ключ се прави от вътрешното 2време (v,t) чрез добавяне на (още едно)
    #междинно стъпало/разделител - виж timed1.put за обяснение на стъпалото.
    #То е нужно за да може да се търси нещо ПРЕДИ (вальор,*) без да се закача transFrom,
    #   т.е. да се представи transFrom=НУЛА без да се знае какво е време.

    TIME_CLASS4check = None       #XXX MUST be set for now... to be removed later
    def _intokey( me, v,t, step =0):
        tc = me.TIME_CLASS4check
        if tc:
            assert isinstance( v, tc)
            assert isinstance( t, tc)
        return v,step,t
    def _fromkey( me, key): return key[0],key[-1]

    def _getitem( me, ix):
        rkey,robj = Timed1._getitem( me, ix)
        return me._fromkey( rkey), robj

    def put( me, obj, time ):
        return Timed1.put( me, obj, me._intokey( *me.time2key_valid_trans( time) ))

    def _result( me, rkey, robj, only_value):   #only_value= bool or callable
        if callable( only_value):
            return only_value( rkey, robj)
        if only_value: return robj
        return me.key_valid_trans2time( rkey), robj

    def get( me, time, only_value =True):
        timeValid, timeTrans = me.time2key_valid_trans( time)
        tkey = me._intokey( timeValid, timeTrans)
        ix = me._get_ix( tkey)
        while ix:
            ix -= 1
            rkey, robj = me._getitem( ix)
            i_timeValid, i_timeTrans = rkey
            if i_timeTrans <= timeTrans:
                return me._result( rkey, robj, only_value)
        return me.NOT_FOUND

    def getRange( me, timeFrom, timeTo, only_value =True, exclusiveTo =False):
        '''both timeFrom/timeTo consist of trans and valid.
        transFrom can be None, to get anything below transTo.
        XXX case of real transFrom != transTo is not tested !!
        '''
        result = []
        ixLast = len( me.order)-1
        if ixLast<0:
            return result
        validFrom, transFrom = me.time2key_valid_trans( timeFrom)
        validTo,   transTo   = me.time2key_valid_trans( timeTo)
        if transFrom is not None and transFrom == transTo:
            import sys
            print >>sys.stderr, '!!! timed2 warning: getRange() with transTo == transFrom ???'
            transFrom = None

        tfrom = transFrom; step = 0
        if transFrom is None:
            step = -1; tfrom = transTo     # just something of correct type
        tkeyFrom = me._intokey( validFrom, tfrom, step)
        tkeyTo = me._intokey( validTo, transTo, step= exclusiveTo and -1 or 0)  #this 0 is not well tested?
        ixFrom, ixTo = me._get_ix2( tkeyFrom, tkeyTo, exclusiveTo= exclusiveTo )
        compareTo = exclusiveTo and operator.lt or operator.le

        lastTimeValid, lastTimeTrans = me._getitem( min( ixTo, ixLast)) [0]
        while ixTo > ixFrom:
            ixTo -= 1
            rkey, robj = me._getitem( ixTo)
            i_timeValid, i_timeTrans = rkey
            if exclusiveTo:
                tmd = me
                assert compareTo( i_timeValid, validTo), '''
compare %(i_timeValid)s vto=%(validTo)s tto=%(transTo)s
 tkeyFrom=%(tkeyFrom)s
 tkeyTo=%(tkeyTo)s
 ixFrom=%(ixFrom)s ixTo=%(ixTo)s
 %(tmd)s
''' % locals()
            if ( (i_timeValid < lastTimeValid or ixTo == ixLast)
                    and i_timeValid >= validFrom
                    and compareTo( i_timeValid, validTo)
                    and compareTo( i_timeTrans, transTo)
                    and (transFrom is None or i_timeTrans >= transFrom)
                ):
                lastTimeValid = i_timeValid
                result.append( me._result( rkey, robj, only_value) )
        result.reverse()
        return result

########

from timed1 import Test0
class Test( Test0):
    input_times = [ #trans,valid
         (  801,  901),
         (  901,  901),
         ( 1101,  901),
         ( 1101, 1002),
    ]
    cases= [  #trans, valid  name            resultindex
            [ ( 1101, 1002), 'exact'         ,4  ],
            [ ( 1101,  901), 'exact1'        ,3  ],
            [ (  901,  901), 'exact2'        ,2  ],
            [ (  900,  901), '1 step-before' ,1  ],
            [ (  910,  901), 'between'       ,2  ],
            [ (  202,  901), 'before all'    ,None],
            [ ( 1212,  901), 'after all'     ,3  ],
            [ ( 1212,  707), 'after all/before all' ,None ],
            [ ( 1213,  907), 'after all/before all' ,3 ],
    ]
    @staticmethod
    def input2time( (t,v)): return (t,v)
    @staticmethod
    def timekey2input( timed, k): return timed.key_valid_trans2time( k)
    @staticmethod
    def input_printer( (t,v)): return 't=%(t)s, v=%(v)s' % locals()


if __name__ == '__main__':
    t = Timed2()
    t.TIME_CLASS4check = int
    test = Test()
    test.test_get_empty( t)

    objects = test.fill( t, [1,3,2,4] )
    test.test_db( t)
    test.test_get( t, objects )
    test.exit()

# vim:ts=4:sw=4:expandtab
