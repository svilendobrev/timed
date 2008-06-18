#$Id$
from datetime import datetime

def d( day):        return datetime( 2006, 9, day)
def dh( day, hour): return datetime( 2006, 9, day, hour)

def tx( x):
    if isinstance( x, int): x = d( x)
    return x

class InitialState:
    def __init__( me, status, trans, valid, value):
        me.status = status
        me.trans = tx(trans)
        me.valid = tx(valid)
        me.value = value
    def __str__( me): return 'DB: trans=%(trans)s valid=%(valid)s %(value)s %(status)s' % me.__dict__
f = InitialState


class TestSample:
    def __init__( me, trans, valid, ignoreStatusVal, expectedVal, name =''):
        me.trans = tx(trans)
        me.valid = tx(valid)
#        me.ignoreStatusVal = ignoreStatusVal
        me.expected = expectedVal
        me.name = name
    def testData( me): return '%s %s' % (me.trans, me.valid)
    def __str__( me): return 'trans=%s valid=%s exp=%s' % (me.trans, me.valid, me.expected)
t = TestSample

idb0 = [#  op  trans/valid  value
        f( 'u',   8,  7,    15 ),
        f( 'd',   8, 10,    25 ),
        f( 'd',  10,  7,    10 ),
        f( 'u',  12,  5,    45 ),
        f( 'u',  12,  7,    35 ),
        f( 'd',  12, 10,    55 ),
]

# val1 - ignoring status -- XXX IGNORED, TODO
# val2 - taking status into account
test0 = [#trans/valid   val1  val2
        t(  8,  10,     25  , None, 'trans exact - valid exact'),
        t(  8,   8,     15  , 15  , 'trans exact - valid between'),
        t(  8,  12,     25  , None, 'trans exact - valid above max'),
        t(  8,   1,     None, None, 'trans exact - valid below min'),
        t(  9,   7,     15  , 15  , 'trans between - valid exact'),
        t(  9,   8,     15  , 15  , 'trans between - valid between'),
        t(  9,   6,     None, None, 'trans between - valid below min'),
        t(  9,  12,     25  , None, 'trans between - valid above max'),
        t( 15,   4,     None, None, 'trans above max - valid below min'),
        t( 15,  15,     55  , None, 'both above max'),
        t(  1,   1,     None, None, 'both below min'),
]

idb1 = [#  op  trans/valid  value
        f( 'u',   7,  7,     5 ),
        f( 'd',   7,  7,    10 ),
        f( 'u',   7,  7,    15 ),
        f( 'd',   7,  7,    20 ),

        f( 'u',   5, 11,    25 ),
        f( 'd',   1, 14,    30 ),
        f( 'u',   8,  8,    35 ),
        f( 'd',   3,  9,    40 ),
        f( 'u',   6,  9,    45 ),
        f( 'u',   8,  8,    50 ),
]

test1 = [#trans/valid   val1  val2
        t(  7,   7,     20,   None, 'both exact =min, multiple matching db records'),
        t(  4,  11,     40,   None, 'both - between'),
        t(  4,   4,     None, None, 'both - between and same'),
        t( 15,  12,     25,   25,   'trans above max - valid between'),
        t(  4,  18,     30,   None, 'trans between - valid above max'),
]

idb2 = [#  op  trans/valid  value
        f( 'd',   5, 15,    100),
        f( 'u',   7,  9,    10 ),
        f( 'd',   7, 11,    15 ),
        f( 'u',   9,  9,    20 ),
        f( 'u',   9, 11,    25 ),
        f( 'd',  11,  9,    30 ),
        f( 'u',  11, 11,    35 ),
        f( 'u',  11, 16,    45 ),
        f( 'u',  18, 18,    75 ),
        f( 'u',  18, 18,    65 ),
]
test2 = [#trans/valid   val1  val2
        t( 15,   9,      30, None, 'trans between, valid exact, trans > valid'),
        t(  9,  15,     100, None, 'both exact, trans < valid'),
        t( 12,  18,      45,   45, 'trans between - valid exact as max'),
        t(  9,  16,     100, None, 'both exact - trans > valid'),
        t(  7,   9,      10,   10, 'both exact - trans > valid _2'),
        t(  7,  10,      10,   10, 'trans exact, valid between'),
        t(  7,  12,      15, None, 'trans exact, valid between _2'),
        t( 18,  18,      65 ,  65, 'both exact =max, multiple matching db records'),
        t( 19,  17,      45 ,  45, 'suspicious for bug'), #pants crash
]

idb3 = [#  op  trans/valid  value
        f( 'u',   8,  3,    50 ),
        f( 'u',   8,  3,    55 ),
        f( 'u',   4,  3,    60 ),
        f( 'd',  12,  3,    65 ),
        f( 'u',  14,  3,    70 ),

        f( 'u',   8,  7,     5 ),
        f( 'd',   8,  7,    10 ),
        f( 'u',   4,  7,    15 ),
        f( 'u',  12,  7,    20 ),

        f( 'u',   8, 10,    25 ),
        f( 'u',   8, 10,    30 ),
        f( 'u',   4, 10,    35 ),
        f( 'd',  12, 10,    40 ),
        f( 'u',  14, 10,    45 ),
]
test3 = [#trans/valid   val1  val2
        t(  1,   1,     None, None, ''),
        t(  1,   3,     None, None, ''),
        t(  1,   4,     None, None, ''),

        t(  4,   1,     None, None, ''),
        t(  4,   3,       60,   60, ''),
        t(  4,   4,       60,   60, ''),

        t(  6,   1,     None, None, ''),
        t(  6,   3,       60,   60, ''),
        t(  6,   4,       60,   60, ''),
        t(  6,   7,       60,   60, ''),
        t(  6,   8,       15,   15, ''),
    # more to be added
]


idb4 = [#  op  trans/valid  value
        f( 'u',   8,  3,    55 ),
        f( 'd',   4,  3,    60 ),
        f( 'd',  12,  3,    65 ),
        f( 'u',  14,  3,    70 ),

        f( 'u',   8,  7,     5 ),
        f( 'd',   8,  7,    10 ),
        f( 'd',   4,  7,    15 ),
        f( 'u',  12,  7,    20 ),

        f( 'd',   8, 10,    30 ),
        f( 'u',   4, 10,    35 ),
        f( 'u',  12, 10,    40 ),
        f( 'd',  14, 10,    45 ),
]


dmax = datetime( 2078, 12, 31)  #was datetime.max but mssql smalldatetime supports max 20790601
dm_1 = dmax.replace( year =dmax.year-1)
idbDefault = idb2 + [
        #  op  trans/valid      value
        f( 'u', dmax, dmax,     18 ),
        f( 'u', dm_1, dm_1,     1821 ),
]
testDefault = [
         #trans/valid   val1  val2
        t( None, None,  65, 65, 'default object (not same as last one)'),
]

def d2( day): return datetime( 2006, 2, day)

testComb = [
         #trans/valid           val1  val2
        t( d2(  7), d2( 12),      53, 53, '' ),
        t( d2( 12), d2(  2),       4,  4, '' ),
        t( d2( 11), d2(  1),       4,  4, '' ),
        t( d2(  1), d2( 11),      50, 50, '' ),
        t( d2( 25), d2(  2),       8,  8, '' ),
        t( d2(  2), d2( 25),      90, 90, '' ),
        t( d2( 25), d2(  7),      38, 38, '' ),
        t( d2(  7), d2( 25),      93, 93, '' ),
        t( d2( 25), d2( 25),      99, 99, '' ),
]


class RangeSample( TestSample):
    def __init__( me, trans, validFrom, validTo, ignoreStatusVal, expectedVal, name =''):
        TestSample.__init__( me, trans, validFrom, ignoreStatusVal, expectedVal, name)
        me.validTo = tx(validTo)
    def testData( me): return '%s %s-%s' % (me.trans, me.valid, me.validTo)
    def __str__( me): return 'trans=%s validfrom=%s validto=%s exp=%s' % (me.trans, me.valid, me.validTo, me.expected)
r = RangeSample

from copy import copy
def idb2RangeItem( it):
    i = copy( it)
    i.status = 'u'  #TODO check that getRange supports enabled/disabled too
    return i
idb_range = [idb2RangeItem( each) for each in idb2] + [
        f( 'u',  11, 14,   34 )
]

testRange = [
        #trans,vfrom,vto    val1 val2
        r(   9,  15,  11,   111, []      , 'all exact, from > to, trans < valid'),
        r(  12,  18,  18,   111, []      , 'trans between, from/to exact as max'),
        r(  11,  12,  14,   111, [34]    , 'trans exact, valids between _2'),
        r(  15,   9,  11,   111, [30,35] , 'trans between, from/to exact, trans > valid, >1 res'),
        r(   7,   8,  12,   111, [10,15] , 'trans exact, from below min, to between, >1 res'),
        r(  19,  10,  17,   111, [35,34,100,45], 'trans above max, valids between, db-same records'),
        r(   9,  11,  16,   111, [25,100], 'all exact, trans < valid from/to'),
        r(  18,  18,  18,   111, [65]    , 'all exact as max, db-same records'),
]
# TODO cases with dh
# tests for evaluated to False objects with same times in state and in query
# tests for getrange with empty init state and state with 1 record and test with ix_from = 0
idb_false = [
        f( 'u',  6, 6,   None),
        f( 'u',  6, 6,   False),
        f( 'u',  6, 6,   []),
        f( 'u',  6, 6,   0),

        f( 'u',  7, 7,   None),
        f( 'u',  7, 7,   False),
        f( 'u',  7, 7,   0),
        f( 'u',  7, 7,   []),

        f( 'u',  8, 8,   False),
        f( 'u',  8, 8,   0),
        f( 'u',  8, 8,   []),
        f( 'u',  8, 8,   None),

        f( 'u',  9, 9,   None),
        f( 'u',  9, 9,   0),
        f( 'u',  9, 9,   []),
        f( 'u',  9, 9,   False),
]

t = TestSample
test_false = [
        t(  6,  6,        0,    0, 'exact in db, last 0'),
        t(  7,  7,        0,   [], 'exact in db, last empty collection'),
        t(  8,  8,     None, None, 'exact in db, last None'),
        t(  9,  9,        0,False, 'exact in db, last False'),
]

class RangeSample( RangeSample):
    def testResult( me, res): return '''
RESULT: %s;
EXPECTED: %s
''' % (res, me.expected)

r = RangeSample
test_range_false = [
         r(  9,  6,  9,     100,   [0,[],None,False] , 'all exact, from > to, trans >= valid'),
         r( 19,  2, 19,     100,   [0,[],None,False] , 'valid outside, trans above, from > to, trans >= valid'),
]
# vim:ts=4:sw=4:expandtab
