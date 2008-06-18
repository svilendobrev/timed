#$Id$
# -*- coding: cp1251 -*-

from bisect import bisect_left

class Timed1( object):
    '''
    Single-timestamp history (i.e. versioned) object. use any (ascending) representation of time.

    нещо с 1-времева история (т.е. версии).
    Работи с всякакво (нарастващо) представяне на времето.

    версии с еднакви времена не се заместват, а се подреждат в реда на добавяне,
    и винаги се връща последната (т.е все едно че се заместват - но историята си остава).

    изключване/включване (enable=exists/disable=deleted) на нещото трябва да се направи
    като огъвка - състоянието на нещото си е само негова работа.
    '''
    class NOT_FOUND: pass

    def __init__( me):
        me.order = []

    #TODO into_record( time,obj,step=0) / from_record( time,obj)
    def put( me, obj_version, time):
        # the 0 in the middle of the record is used as stepper: allows searching for a
        # step AFTER an existing time but before next valid one without knowing what is 'time'.
        # (also works for BEFORE/prev).
        # looking for (time,1)  will position AFTER  last existing  t==time
        # looking for (time,-1) will position BEFORE first existing t==time
        # looking is done via bisect_left; bisect_right gives same results
        #
        # 0-та в средата на записа се ползва като стъпало/разделител - да може да се търси една
        # стъпка СЛЕД някакво съществуващо време но преди следващото валидно време,
        # без да се знае какво точно е 'време' (също става и за ПРЕДИ/предишно)

        ##при еднакви времена, това винаги добавя в края им
        ix = me._get_ix( time)
        me.order.insert( ix, (time,0,obj_version) )

    def _get_ix_after( me, time ):
        '''index of next eventual item after 'time':
            just-after right side of [a,b] period - inclusive 'time' looking from 0 upwards
            0 means not found; can be == len(order)
            -=1 to use as index of last item <= time
        '''
        assert time
            #see put() for explaining the middle 1
        time_next = (time,1, None)          #преди следващото
        ix = bisect_left( me.order, time_next )
        return ix   #0 значи няма запис
    _get_ix = _get_ix_after

    def _get_ix_least( me, time):
        '''index of least item matching 'time' (i.e. inclusive):
            can be 0 ; can be == len(order)
            this is left side of [a,b] period
            -=1 to use as index of last item _before_ time
        '''
        assert time
        time_prev = (time,-1, None)
        return bisect_left( me.order, time_prev )

    def _get_ix2( me, timefrom, timeto, exclusiveTo =False ):   #always inclusiveFrom
        '''return ix_from:inclusive, ix_to:exclusive
            i.e. ix_from is real index, ix_to needs -=1 to become real index'''
        #TODO timeto :  #символ/маркер ? напр. до-края
        ix_from = me._get_ix_least( timefrom)
        get_ix_to = exclusiveTo and me._get_ix_least or me._get_ix_after
        ix_to = get_ix_to( timeto)
        return ix_from, ix_to

    def _getitem( me, ix):
        rkey, _stepper, robj = me.order[ ix]
        return rkey,robj

    def _result( me, rkey, robj, only_value =True):     #only_value= bool or callable
        if callable( only_value):
            return only_value( rkey, robj)
        if only_value: return robj
        return rkey,robj

    def get( me, time, only_value =True ):
        ix = me._get_ix( time)
        if ix:
            rkey, robj = me._getitem( ix-1)
            return me._result( rkey, robj, only_value)
        return me.NOT_FOUND #None
    __getitem__ = get

    #XXX TODO getRange

    def __str__(me):
        return me.__class__.__name__ + '\n ' + '\n '.join( str(f) for f in me.order )

    def __eq__( me, other): return me.order == other.order
    def __ne__( me, other): return me.order != other.order

###################### test base

class Test0( object):
    @staticmethod
    def input2time( t): return t
    @staticmethod
    def timekey2input( timed, k): return k
    input_printer = repr

    def fill( me, timed, inputs =None, input2time =None):
        print 'fill:',
        if not input2time: input2time = me.input2time
        input_times = me.input_times
        objects = input_times[:]
        for i in (inputs or range( 1,1+len(input_times))):
            o = 'v'+str(i)
            print o,
            timed.put( o, input2time( input_times[i-1] ))
            objects[ i-1] = o
        print
        if me.verbose: print timed
        return objects

    def test_db( me, timed,
                timekey2input   =None,
                input_printer   =None,
            ):
        print 'test_internal_contents',
        if not timekey2input: timekey2input = me.timekey2input
        if not input_printer: input_printer = me.input_printer
        input_times = me.input_times
        err = 0
        res_db = timed.order
        key2out = getattr( timed, '_fromkey', lambda k:k)
        res_times = [ timekey2input( timed, key2out( row[0])) for row in res_db ]
        if res_times != list( input_times):
            l_in = len( input_times)
            l_db = len( res_db)
            print '  ERR:'
            print '   result_db: len=%(l_db)s %(timed)s' % locals()
            print '   template:  len=', len(input_times)
            for tm in input_times:
                print '   ', input_printer( tm)
            err += 1
        else:
            print ' OK'
        me.err += err
        return err

    #XXX TODO test_getRange

    def test_get( me, timed,
                objects,
                cases       =None,
                input2time  =None,
                obj_titler      =lambda r:r,
                timed_printer   =lambda t:t,
                obj_printer     =None,
                timed_titler    =lambda t:t.__class__.__name__,
            ):
        if not cases: cases= me.cases
        if not input2time: input2time = me.input2time
        err = 0
        verbose = me.verbose
        print 'test_get', timed_titler and timed_titler( timed),
        first = 1
        for row in cases:
            tm, name, iresult = row
            m = timed.get( input2time( tm), only_value=False )
            if m is not timed.NOT_FOUND: r = m[-1]
            else: r = None
            if iresult: r_expect = objects[ iresult-1]
            else: r_expect = None
            ok = (r_expect == r)
            if verbose or not ok:
                if first: print
                print ok and '  OK  ' or '  ERR!', ':', name, tm, '->', r and obj_titler(r)
            if verbose>1 or not ok:
                print '   expect:', r_expect and obj_titler( r_expect)
                print '   result:', m, r and obj_printer and obj_printer( r) or ''
            err += not ok
            first = 0
        if verbose>1 or err:
            print timed_printer( timed)
        print err and ' ERR' or ' OK'
        if verbose or err: print
        me.err += err
        return err

    def test_get_empty( me, timed):
        assert not timed.order
        print 'empty'
        return me.test_get( timed, [],
            cases=[ (c[:2]+[None]) for c in me.cases ]
        )

    __slots__ = ()
    _err = 0
    def seterr( me, v): Test0._err = v
    err = property( lambda me:me._err, seterr)

    def __init__( me, verbose =0 ):
        import sys
        me.verbose = sys.argv.count('-v') or verbose
    def exit( me):
        raise SystemExit, me.err

####### test timed1

class Test( Test0):
    input_times = [ 901, 1002, ]
    cases= [#time   #case-name      #result-obj = 1+index over input_times
            [ 1002, 'exact'         , 2    ],
            [  901, 'exact'         , 1    ],
            [  900, '1 step-before' , None ],
            [  910, 'between'       , 1    ],
            [  202, 'before all'    , None ],
            [ 1010, 'after all'     , 2    ],
    ]

    def fill4sametime( me, timed, shade, objects, shade_out =None ):
        objs = objects[:]
        if not shade_out: shade_out = shade
        print 'setup same-time sequencing',
        if me.verbose: print ':', shade_out, 'must hide the original', objs[0]
        else: print
        timed.put( shade, me.input2time( me.input_times[0]) )
        objs[0] = shade_out
        return objs

if __name__ == '__main__':
    test = Test()
    t = Timed1()

    test.test_get_empty( t)

    #something
    objects = test.fill( t, [1,2] )
    test.test_db( t)

    for sametime in (0,1):
        objs = objects
        if sametime:
            objs = test.fill4sametime( t, 'shade', objects )
        test.test_get( t, objs )

    test.exit()

# vim:ts=4:sw=4:expandtab
