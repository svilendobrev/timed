#$Id$
# -*- coding: cp1251 -*-

def errorer( oserr):
    print oserr

import os, os.path, imp, sys
_DEBUG = 0

PY_SUFFIXES = [ suffix for (suffix,mode,typ) in imp.get_suffixes() if typ == imp.PY_SOURCE ]

# str2datetime converters
def dateYYYYMMDD2datetime( s):
    from datetime import datetime
    if not isinstance( s, datetime):
        s = datetime( int( s[0:4]), int( s[4:6]), int( s[6:8]))
    return s
def datetime2dateYYYYMMDD( d):
    return d.strftime( '%Y%m%d' )



class _module2time_converter:
    '''no suffix, no paths here'''

    def str2time1( me, t): return t     #overload, e.g. dateYYYYMMDD2datetime
    def mod2time1( me, t): return t     #overload, e.g. dateYYYYMMDD2datetime

    # redefine these
    def maketime( me, trans, valid):    #overload, e.g. return TimeContext()
        return trans,valid              #timed2 by default
    def fname2time( me, modname, loader =None):
        raise NotImplementedError
        if module.needed: module = loader()
        time = me.maketime( me.str2time1( t1), me.mod2time1( module.t2), whatever-maketime-handles )
            #time трябва да е валидно за използваната Timed основа
        return time, module or None

    def _fname2times( me, modname):
        'sequence of times in the modname'
        assert '.' not in modname
        assert '/' not in modname
        times = [ t for t in modname.split( '_' ) if t ]  #all non-empties - e.g. _2006_2005_ -> (2006,2005)
        return times
#    def time2fname( me, time): return '_'+ '_'.join( me.time2str( time) )


class mod2time__1_time_in_fname( _module2time_converter):
    def maketime( me, time): return time
    def fname2time( me, modname, loader =None):
        times = me._fname2times( modname)
        time = times[0]             #ignore the rest
        return me.maketime( me.str2time1( time) ), None

class mod2time__all_in_fname___trans_valid( _module2time_converter):
    def fname2time( me, modname, loader =None):
        times = me._fname2times( modname)
        trans,valid = times[:2]     #ignore the rest
        return me.maketime( trans= me.str2time1( trans), valid= me.str2time1( valid)), None

class mod2time__trans_in_fname__valid_in_module( _module2time_converter):
    def fname2time( me, modname, loader):
        times = me._fname2times( modname)
        trans = times[0]            #ignore the rest

        mod = loader()              #no lazy load here..
        valid = mod.TIMEVALID
        return me.maketime( trans= me.str2time1( trans), valid= me.mod2time1( valid)), mod

class mod2time__all_in_module( _module2time_converter):
    def fname2time( me, modname, loader):
        mod = loader()              #no lazy load here..
        valid = mod.TIMEVALID
        trans = mod.TIMETRANS
        return me.maketime( trans= me.mod2time1( trans), valid= me.mod2time1( valid)), mod


class Module( object):
    '''
    module with timestamped versions. uses Timed1/2 protocol
    and as such works with any (ascending) representation of time/s
    '''

    WALK_INITIALY = 1   #дали да се зареди историята в началото или само при поискване
    WALK_SUBDIRS  = 0   #първото ниво май стига

        #може ли да има невалидни/фалшиви модули? т.е. има го файла, ама вътре не е модул
        #тогава май трябва да се зарежда/проверява всичко първоначално...
    LAZY_LOAD = 1

    class Ptr( object):
        __slots__ = [ 'data' ]
        def __init__( me, data): me.data = data
        def __str__( me): return 'Ptr:' + str( me.data)
        __repr__ = __str__
        __name__ = property(
            lambda me: isinstance( me.data, tuple) and me.data or me.data.__name__ )

    def __init__( me, name, timedKlas, module2time_converterKlas =None):
        me.name = name
        me.timed = timedKlas()
        me.NOT_FOUND = me.timed.NOT_FOUND
        m2t = module2time_converterKlas
        if not m2t:
            m2t = mod2time__all_in_fname___trans_valid
        me.converter = c = m2t()
        me.fname2time = c.fname2time
        me.root = None
        if me.WALK_INITIALY:
            me.walk()

    def __str__(me):
        klas = me.__class__.__name__
        name = me.name
        timed = me.timed
        return '%(klas)s( %(name)s )\n%(timed)s' % locals()

    def _load_root_module( me):
        root = me.root
        if not root:
            name = me.name
            if _DEBUG: print 'imp', name
            # this is the proper way
            p3 = imp.find_module( name)
            root = me.root = imp.load_module( name,*p3)
        return root

    def _load_module_version( me, modname, fname):
        if _DEBUG: print 'imp', fname
        if 0 and 'linux' in sys.platform:
            name = '.'.join( (me.name, modname))
            root = __import__( name)   #returns root
            return getattr( root, modname)
        else:
            modpath = me.name.split( os.path.sep) # ne os.path.split
            _root = modpath[0]
            modpath.append( modname)
            name = '.'.join(modpath)
            return __import__( name, fromlist= [_root])

        root = me._load_root_module()
        p3 = imp.find_module( modname, root.__path__)
        m = imp.load_module( name,*p3)
        setattr( root, modname, m)
        return m

        return imp.load_source(
                    '.'.join( (me.name, modname)),
                    fname,
                    open( fname)
                 )

    def get( me, time, only_value =True):
        g = me.timed.get( time, only_value=only_value)
        if g is me.NOT_FOUND: return g
#        print 'get',g
        if only_value: o = g
        else: o = g[-1]
        mod = o.data
        if isinstance( mod, tuple):
            #(modname, fname) = mod
            mod = me._load_module_version( *mod)
            o.data = mod    #cache it

        assert mod      #if not mod: error???
        if only_value: return mod
        return g[:-1] + (mod,)    #as of timed* protocol


    _walked = False
    def walk( me):
        if me._walked: return
        name = me.name
            # какво да се прави с главния/коренния файл? нищо.
            #root = me._load_root_module()
            #me.put( root, '0')  #???

        #simulate python.import path lookup
        pths = [name]*0 + [ os.path.join( p, name) for p in sys.path]
        #print pths
        for p in pths:
            if os.path.isdir( p):
                name = p
                break

        for p in os.walk( name, onerror= errorer):
            (dirpath, dirnames, filenames) = p
            for f in filenames:
                #filter on f ? e.g. _\d+.py
                modname,ext = os.path.splitext( f)     #no path!
                if f.startswith('__') or ext not in PY_SUFFIXES:
                    continue
                if _DEBUG: print 'walk', f

                fname = os.path.join( dirpath, f)
                mf = (modname,fname)
                def loader(): return me._load_module_version( *mf)

                time,mod = me.fname2time( modname, loader)
                if not mod:
                    mod = me.LAZY_LOAD and mf or loader()
                me.timed.put( me.Ptr( mod), time )
            if not me.WALK_SUBDIRS: break
        me._walked = True


if __name__ == '__main__':
    ############# testing ###########
    #either run from inside tests/ or set PYTHONPATH=tests/ or this below:
    #sys.path.append( 'tests/')

    def testmod( test, mod, **kargs):
        mod.walk()
        return test.test_get( mod
            ,timed_titler   = lambda mod: mod.name+' '+mod.converter.__class__.__name__
            ,obj_titler     = lambda r: r.__name__
            ,timed_printer  = lambda mod: mod.timed
            ,obj_printer    = lambda r: r.VERSION
            ,**kargs
        )

    def testall( test, what):
        Module.LAZY_LOAD=0
        #module.times are 2006mmdd - cut off the year
        def _m2time( t):     return int(t[4:])
        def m2time( me, t):  return _m2time(t)
        def m2time2( me, trans,valid): return (_m2time(t) for t in (trans,valid))
        if 1 in what:
            mod2time__1_time_in_fname.maketime = m2time
            import timed1
            m1 = Module( name= 'dod', timedKlas= timed1.Timed1,
                    module2time_converterKlas= mod2time__1_time_in_fname)
            import dod._20060901 as r1
            import dod._20061002 as r2
            objects= [r1,r2]
            tst1 = timed1.Test()
            #tst1.input2time = str
            testmod( tst1, m1, objects= objects)

            if 1:   #sametime
                class Shade:
                    tablica = ['shade']
                    VERSION = -1
                objects = tst1.fill4sametime( m1.timed, Module.Ptr( Shade), objects=objects, shade_out=Shade)
                testmod( tst1, m1, objects= objects)

        ########
        from timed2 import Timed2
        #test.input2time = lambda (t,v): (str(t),str(v))
        def test2( mod, objects):
            return testmod( test, mod, objects=objects)

        if 2 in what:
            mod2time__all_in_fname___trans_valid.maketime = m2time2
            m2 = Module( name= 'dod2', timedKlas= Timed2,
                        module2time_converterKlas= mod2time__all_in_fname___trans_valid)
            import dod2._20060801_20060901 as p1
            import dod2._20060901_20060901 as p2
            import dod2._20061101_20060901 as p3
            import dod2._20061101_20061002 as p4
            test2( m2, [p1,p2,p3,p4 ])

        if 3 in what:
            mod2time__trans_in_fname__valid_in_module.maketime = m2time2
            m3 = Module( name= 'dod3', timedKlas= Timed2,
                        module2time_converterKlas= mod2time__trans_in_fname__valid_in_module)
            import dod3._20060801_1 as q1
            import dod3._20060901   as q2
            import dod3._20061101_1 as q3
            import dod3._20061101_2 as q4
            test2( m3, [q1,q2,q3,q4 ])

        if 4 in what:
            mod2time__all_in_module.maketime = m2time2
            m4 = Module( name= 'dod4', timedKlas= Timed2,
                        module2time_converterKlas= mod2time__all_in_module)
            import dod4._v as s1
            import dod4._c as s2
            import dod4._b as s3
            import dod4.a  as s4
            test2( m4, [s1,s2,s3,s4 ])
        print '===', test.err and 'ERRORS!' or 'all OK', '==='

    import timed2
    test = timed2.Test()
    testall( test, [1,2,3,4] )
    test.exit()

# vim:ts=4:sw=4:expandtab
