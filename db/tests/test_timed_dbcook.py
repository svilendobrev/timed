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
    from static_type.types.atomary  import Number
else:
    from dbcook.usage import plainwrap as orm
    orm.NO_CLEANUP =1
    class Number( orm.Type): pass

import dbcook.usage.samanager as sam
SAdb = sam.SAdb
SAdb.Builder = orm.Builder

import sqlalchemy
SAdb.fieldtypemap = { Number: dict( type= sqlalchemy.Integer, ), }

class Config( sam.config.Config):
    repeat      = 1
    notimed     = False
    _help = '''
test_timed:
  repeat= :: number of times to test each sample
  notimed :: not used here
'''
config = Config( sam.config )
sam.config = config


from engine.timed.tests.protocol import test_protocol2Timed_protocol
class TEST:
    only_days = True
    Time = only_days and Number or Date

    _valid_trans2time = dict

    @classmethod
    def _timeconvert1( klas, time):
        if klas.only_days: return time.day
        return time.date()
    PolymBase = None            #must be set before run
    PolymLeaf = None            #must be set before run
    ObjectCounter = None        #must be set before run
    config = config             #XXX
    namespace = None            #must be set before run
    NUM_OF_OBJID = 3
    DB = None

import engine.timed.db.config as timed2_config
timed2_config.db_id_name    = orm.builder.column4ID.name
timed2_config.ValidTimeType = TEST.Time
timed2_config.TransTimeType = TEST.Time


def setupBase( me):
    if getattr( TEST.DB, 'sa', None): TEST.DB.sa.destroy()
    me.db = TEST.DB.reset( TEST.namespace, counterBase= TEST.ObjectCounter, recreate= True, get_config= False) #XXX DBCookTest

def setupSimple( me):
    setupBase( me)
    satest.Case.setup( me)
    TEST.DB.session.flush()

def setupEach_diff_klas( me, f):
    me.oldSetupEach( f)
    me.obj.org.val = TEST.PolymLeaf()
    me.oldSetupEach( f)
    me.obj.org.val = TEST.PolymBase()

def setupSimple_objid( me):
    setupBase( me)
    for i in range( 1, TEST.NUM_OF_OBJID+1): #obj_id 0 means autoinc
        me.obj.org.val.__class__.OBJ_ID = i #Ooh poor Demeter, Demeter.....
        satest.Case.setup( me)
        #print 'SETUP: %s' % me.obj.org.val.__class__.OBJ_ID
    me.obj.org.val.__class__.OBJ_ID = 1
    TEST.DB.session.flush()

def setupCombination( me):
    setupBase( me)
    me.oldSetup()
    TEST.DB.session.flush()

def setupCombination_objid( me):
    setupBase( me)
    for i in range( 1, TEST.NUM_OF_OBJID+1):
        me.obj.org.val.__class__.OBJ_ID = i
        me.oldSetup()
    me.obj.org.val.__class__.OBJ_ID = 1
    TEST.DB.session.flush()

def testEach_timed_base( me, t):
    for i in range( int( TEST.config.repeat)):
        res = me.oldTestEach( t)
    return res

# as testdata expects single result expected is wrapped into list
def singleObjId( t):
    if t.expected: t.expected = [ t.expected]
    return t
def multyObjId( t):
    if t.expected: t.expected = [ t.expected for i in range( TEST.NUM_OF_OBJID)]
    return t

def testEach_timed( me, t): return testEach_timed_base( me, singleObjId( t))
def testEach_timed_objid( me, t): return testEach_timed_base( me, multyObjId( t))

def testEach_default_base( me, t):
    print "- STUB - Not actually testing",
    import datetime
    res = None
    if me.obj:
        t.trans = t.valid = datetime.datetime( 2007, 1, 27)
        res = me.obj.get( trans=t.trans, valid=t.valid, with_disabled=False)
    return res

def testEach_default( me, t): return testEach_default_base( me, singleObjId( t))
def testEach_default_objid( me, t): return testEach_default_base( me, multyObjId( t))

class Timed_Wrapper( test_protocol2Timed_protocol):
    '''testing purposes only'''
    def __init__( me, timed ):
        me.val = timed()
        me.NOT_FOUND = timed.NOT_FOUND

    @staticmethod
    def _valid_trans2time( valid, trans):
        return TEST._valid_trans2time(
            valid= TEST._timeconvert1( valid),
            trans= TEST._timeconvert1( trans),
        )
    def timed_get( me, time, with_disabled =False, **kargs):
        q = me.val.allInstances( time, with_disabled=with_disabled, **kargs )
        return [ getattr( each, 'val', each) for each in q ] or None
    def timed_getRange( me, timeFrom, timeTo, with_disabled =False):
        q = me.val.get_version_history( me.val.OBJ_ID, timeFrom, timeTo, with_disabled=with_disabled )
        return [ getattr( each, 'val', each) for each in q ]
    def timed_put( me, value, time, disabled =False):
        if disabled: value = None
        return me.val.put( value, time)


def tm2_simple():   return Timed_Wrapper( TEST.PolymLeaf)
def tm2_poly():     return Timed_Wrapper( TEST.PolymBase)

def run( config):
    TEST.config = config
    timed2_config.runtime = config
    config.getopt()
    timed2_config.runtime.forced_trans = True
    print config

    #single OBJ_ID suites
    satest.TimedTestSimpleCase.setup = setupSimple
    satest.TimedTestSimpleCase.oldTestEach = satest.TimedTestSimpleCase.testEach
    satest.TimedTestSimpleCase.testEach = testEach_timed
    satest.TimedCombinationsTestCase.oldSetup = satest.TimedCombinationsTestCase.setup
    satest.TimedCombinationsTestCase.setup = setupCombination
    satest.TimedDefaultGetTestCase.testEach = testEach_default
    rr = satest.test( staticmethod( tm2_poly), True, title ='base only - single obj-type')
    rr = rr and satest.test( staticmethod( tm2_simple), True, title ='leafs only, both types available')
    satest.TimedTestSimpleCase.oldSetupEach = satest.TimedTestSimpleCase.setupEach
    satest.TimedTestSimpleCase.setupEach = setupEach_diff_klas
    rr = rr and satest.test( staticmethod( tm2_poly), True, title ='base+leafs via base')

    # many OBJ_IDs suites, same testdata for every OBJ_ID
    satest.TimedTestSimpleCase.setup = setupSimple_objid
    satest.TimedCombinationsTestCase.setup = setupCombination_objid
    satest.TimedTestSimpleCase.testEach = testEach_timed_objid
    satest.TimedCombinationsTestCase.testEach = testEach_timed_objid
    satest.TimedDefaultGetTestCase.testEach = testEach_default_objid
    rr = rr and satest.test( staticmethod( tm2_poly), True, title ='base only - single obj-type, many OBJIDs')
    rr = rr and satest.test( staticmethod( tm2_simple), True, title ='leafs only, both types available, many OBJIDs')
    satest.TimedTestSimpleCase.setupEach = setupEach_diff_klas
    rr = rr and satest.test( staticmethod( tm2_poly), True, title ='base+leafs via base, many OBJIDs')

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
    #print 'OBJ_ID: %s:%s' % ( me.OBJ_ID, me.__class__.OBJ_ID)
    tn.obj_id = me.OBJ_ID
    tn.val = obj
    tn.disabled = (obj is None)
    #print 'OBJ:', obj, tn.disabled
    TEST.DB.save( tn)
    return tn

if __name__ == '__main__':

    import engine.timed.db.timed2_dbcook as timed2
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
        disabled    = Number()
        # eo

        val = Number()
        OBJ_ID = 1  #for multiple obj testing

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
