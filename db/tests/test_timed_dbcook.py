#$Id$
# -*- coding: cp1251 -*-
'''
this must test all additional aspects of bitemporal behaviour in "real database":
    - allInstances from certain TimeContext point of view, with >1 timed objects in same db table
    - range of history records for one concrete timed object
        between 2 certain TimeContexts - from to
it uses more basic testing data from engine/timed that tests only bitemporal behavior by its own
when obj is alone in the table/collection. These must be tested with simple and with polymorphic
klasses

subject under test:
    allInstances/get_allobj_lastversion
    get_version_history
'''
import engine.timed.tests.test_base as satest

if 0:
    from dbcook.usage.static_type import sa2static as orm
    from static_type.types.atomary  import Number, Bool, StaticType
    class Date( StaticType):
        def __init__( me, **kargs):
            import datetime
            StaticType.__init__( me, datetime.date, **kargs)
else:
    from dbcook.usage import plainwrap as orm
    orm.NO_CLEANUP =1
    class Number( orm.Type): pass
    class Bool( orm.Type): pass
    class Date( orm.Type): pass

import dbcook.usage.samanager as sam
SAdb = sam.SAdb
SAdb.Builder = orm.Builder

import sqlalchemy
SAdb.fieldtypemap = {
    Number: dict( type= sqlalchemy.Integer, ),
    Date:   dict( type= sqlalchemy.Date, ),
    Bool:   dict( type= sqlalchemy.Boolean, ),
}

class Config( sam.config.Config):
    repeat      = 1
    notimed     = False
    _help = '''
test_timed:
  repeat= :: number of times to test each sample
  notimed :: not used here
'''
config = Config()
sam.config = config
import sys

from engine.timed.tests.protocol import test_protocol2Timed_protocol
class TEST:
    only_days = True
    Time = only_days and Number or Date

    _valid_trans2time = dict

    @classmethod
    def _timeconvert1( me, time):
        if me.only_days: return time.day
        return time.date()

    if 'rev4trans' not in sys.argv:
        revision4trans = None
    else:
        _revisions =[]
        @classmethod
        def revision4trans( me, time):
            me._revisions.append( time)
            return len( me._revisions)-1
        satest.TimedTestSimpleCase.initial_sortkey = lambda me, f: f.trans

    @classmethod
    def _timeconvert1trans( me, time):
        if not me.revision4trans:
            return me._timeconvert1( time)
        import bisect
        ix = bisect.bisect_right( me._revisions, time)
        return ix -1    #biggest matching

    PolymBase = None            #must be set before run
    PolymLeaf = None            #must be set before run
    config = config             #XXX
    namespace = None            #must be set before run

    DB = None
    @classmethod
    def DB_reset( me, *a,**k):
        me.DB.reset( *a,**k)
    @classmethod
    def DB_destroy( me):
        if getattr( me.DB, 'sa', None): me.DB.sa.destroy()
        if me.revision4trans:
            me._revisions = []

    NUM_OF_OBJID = 3
    @staticmethod
    def setup_OBJIDs( klas, offset =0):    #plain int by default
        #klas = me.obj.org.val.__class__
        klas.OBJIDs = [ offset+1+a for a in range( TEST.NUM_OF_OBJID ) ]
    @classmethod
    def DB_dump( me):   #used in error-dump
        return '\n'+'\n'.join( str(s) for s in me.PolymBase.allInstances_basic().all() )

    second_hand = False
print TEST.revision4trans and 'revision4trans'

import engine.timed.db.config as timed2_config
timed2_config.db_id_name    = orm.builder.column4ID.name
timed2_config.ValidTimeType = TEST.Time
timed2_config.TransTimeType = TEST.revision4trans and Number or TEST.Time

def set_ixOBJID( me, ix):
    me.obj.org.val.__class__.ixOBJID = ix

def setupBase( me):
    TEST.DB_destroy()
    TEST.DB_reset( TEST.namespace, recreate= True, get_config= False)
    TEST.setup_OBJIDs( TEST.PolymBase)
    TEST.setup_OBJIDs( TEST.PolymLeaf, offset=10)   #all_lastver etc use just oid, no type-discriminator
    set_ixOBJID( me, 0)
    TEST.second_hand = False

def setupBaseEnd( me):
    TEST.DB.session.flush()
    me._systemState = TEST.DB_dump()     #ONCE, here !!
    if TEST.revision4trans:
        me._systemState += '\n'+'\n'.join( '%s:%s' % (i,TEST._revisions[i]) for i in range(len(TEST._revisions)))
    set_ixOBJID( me, 0)

def setupSimple( me):
    setupBase( me)
    satest.Case.setup( me)
    setupBaseEnd( me)

def setupEach_diff_klas( me, f):
    TEST.second_hand = False
    me.oldSetupEach( f)
    orgval = me.obj.org.val

    TEST.second_hand = True     #XXX and leave if True until next test
    if TEST.revision4trans:
        if getattr( me, 'looped1', False): return
        TEST._revisions.pop()   #XXX HACK XXX - so same position in a pack gets same revno
    me.obj.org.val = TEST.PolymLeaf()
    me.oldSetupEach( f)

    me.obj.org.val = orgval

def setupSimple_objid( me):
    setupBase( me)
    me.looped1 = False
    for i in range( TEST.NUM_OF_OBJID):
        if TEST.revision4trans:
            TEST._revisions = []    #XXX HACK XXX - so same position in a pack gets same revno
        set_ixOBJID( me, i)
        satest.Case.setup( me)
        me.looped1 = True
    setupBaseEnd( me)

# as testdata uses single result, t.expected is wrapped into list
def testEach_timed( me, t, num =1):
    if t.expected:
        t.expected = [ t.expected ] * num
        if TEST.second_hand: t.expected.append( t.expected[-1] + 1000 )

    for i in range( int( TEST.config.repeat)):
        res = me.oldTestEach( t)
    return res
def testEach_timed_objid( me, t): return testEach_timed( me, t, num=TEST.NUM_OF_OBJID)

def testEach_default( me, t, num =1):
    print "- STUB - Not actually testing",
    if t.expected:
        t.expected = [ t.expected ] * num
        if TEST.second_hand: t.expected.append( t.expected[-1] + 1000 )
    import datetime
    res = None
    if me.obj:
        t.trans = t.valid = datetime.datetime( 2007, 1, 27)
        res = me.obj.get( trans=t.trans, valid=t.valid, with_disabled=False)
    return res
def testEach_default_objid( me, t): return testEach_default( me, t, num=TEST.NUM_OF_OBJID)

class Timed_Wrapper( test_protocol2Timed_protocol):
    '''testing purposes only'''
    def __init__( me, timed ):
        me.val = timed()
        me.NOT_FOUND = timed.NOT_FOUND
    @staticmethod
    def _valid_trans2time( valid, trans):
        return TEST._valid_trans2time(
            valid= TEST._timeconvert1( valid),
            trans= TEST._timeconvert1trans( trans),
        )
    @classmethod
    def _valid_trans2time4put( me, valid, trans):
        if TEST.revision4trans:
            trans = TEST.revision4trans( trans)
        else:
            trans = TEST._timeconvert1( trans)
        return TEST._valid_trans2time(
            valid= TEST._timeconvert1( valid),
            trans= trans,
        )
    str_query = ''
    def __str__( me): return 'query:\n'+me.str_query
    def timed_get( me, time, with_disabled =False, **kargs):
        q = me.val.allInstances( time=time, with_disabled=with_disabled, **kargs )
        me.str_query = str(q)
        return [ getattr( each, 'val', each) for each in q ] or None
    def timed_getRange( me, timeFrom, timeTo, with_disabled =False):
        oid = me.val.OBJIDs[ me.val.ixOBJID]
        #print 'RANGE:', oid
        q = me.val.get_version_history( oid, timeFrom=timeFrom, timeTo=timeTo, with_disabled=with_disabled )
        me.str_query = str(q)
        return [ getattr( each, 'val', each) for each in q ]
    def timed_put( me, value, time, disabled =False):
        if disabled: value = None
        return me.val.put( value, time)


def tm2_simple():   return Timed_Wrapper( TEST.PolymLeaf)
def tm2_poly():     return Timed_Wrapper( TEST.PolymBase)

def take1(
        simple_setup, simple_testeach,
        defget_testeach,
        simple_setupeach,
        kind ='',
    ):

    satest.TimedTestSimpleCase.setupEach = satest.TimedTestSimpleCase.oldSetupEach  #restore

    satest.TimedTestSimpleCase.setup = simple_setup
    satest.TimedTestSimpleCase.testEach = simple_testeach
    satest.TimedDefaultGetTestCase.testEach = defget_testeach
    kargs = dict( verbosity=1, no_stderr=1)
    rr = 1
    rr = rr and satest.test( staticmethod( tm2_poly),   title ='base only - single obj-type'+kind, **kargs)
    rr = rr and satest.test( staticmethod( tm2_simple), title ='leafs only, both types available'+kind, **kargs)
    satest.TimedTestSimpleCase.setupEach = simple_setupeach
    rr = rr and satest.test( staticmethod( tm2_poly),   title ='base+leafs via base'+kind, **kargs)
    return rr


def run( config):
    TEST.config = config
    timed2_config.runtime = config
    config.getopt()
    timed2_config.runtime.forced_trans = True
    print config

    satest.TimedTestSimpleCase.oldTestEach = satest.TimedTestSimpleCase.testEach
    satest.TimedTestSimpleCase.oldSetupEach = satest.TimedTestSimpleCase.setupEach


    #single OBJID
    rr = take1(
            simple_setup= setupSimple,
            simple_testeach= testEach_timed,
            defget_testeach= testEach_default,
            simple_setupeach= setupEach_diff_klas,
        )

    # many OBJ_IDs, same testdata for every OBJID
    rr = take1(
            simple_setup= setupSimple_objid,
            simple_testeach= testEach_timed_objid,
            defget_testeach= testEach_default_objid,
            simple_setupeach= setupEach_diff_klas,
            kind=' / many OBJIDs'
        )

    print '\nTOTAL RESULT:', rr and 'OK' or 'Failed'
    print

def put( me, obj, time ):
    assert obj is None or isinstance( obj, int)
    tn = me.__class__()
    me.setupobj( tn)
    timeValid, timeTrans = me.time2key_valid_trans( time)
    tn.time_valid = timeValid
    tn.time_trans = timeTrans
    #print "put times:", tn.time_trans, tn.time_valid
    oid = me.OBJIDs[ me.ixOBJID ]
    #print 'ixOBJID:', me.ixOBJID, oid
    tn.obj_id = oid
    if TEST.second_hand and obj is not None: obj += 1000
    tn.val = obj
    tn.disabled = (obj is None)
    #print 'OBJ:', obj, tn.disabled, tn.obj_id# id(tn.obj_id), me.ixOBJID, me.OBJIDs
    TEST.DB.save( tn)
    return tn

if __name__ == '__main__':
    import sys
    import engine.timed.db.timed2_dbcook as timed2
    timed2.Timed2Mixin.revision4trans = 'rev' in sys.argv
    class DB_( object):
        session = None #have flush()
        def reset( me, namespace, counterBase= None, recreate =True, get_config =False):
            me.sa = SAdb()
            me.sa.open( recreate=True)
            me.sa.bind( namespace, base_klas=orm.Base) #, force_ordered= True)
            me.session = me.sa.session()
            if counterBase: counterBase.fill( *me.sa.klasi.iterkeys() )
        def save( me, *args):
            assert args
            me.sa.saveall( me.session, *args)
            me.session.flush()

    TEST.DB = DB_()
    class PolymBase( orm.Base, timed2.Timed2Mixin):
        #Timed2Mixin setup
        def now( me): return TEST._timeconvert1( datatime.now() )
        #eo Timed2Mixin
        def pre_save( me): pass     #stub

        DBCOOK_has_instances = True
        DBCOOK_inheritance = 'joined_table'
        #class NOT_FOUND: pass
        NOT_FOUND = None

        # bitemporal-required fields - TODO move in separate mixins
        obj_id      = Number()
        disabled    = Bool()
        # eo

        val = Number()

        def setupobj( me, inst): pass

        @classmethod
        def allInstances_basic( klas):
            return TEST.DB.session.query( klas)
        def put( me, obj, time ):
            return put( me, obj, time )

    class PolymLeaf( PolymBase): pass
    TEST.namespace = locals()
    TEST.PolymBase = PolymBase
    TEST.PolymLeaf = PolymLeaf
    run( config)

# vim:ts=4:sw=4:expandtab
