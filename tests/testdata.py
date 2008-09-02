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
        f( 'u',   5,  5,     1 ),
        f( 'd',   5,  5,     3 ),
        f( 'u',   5,  5,     7 ),
        f( 'd',   5,  5,     9 ),
        f( 'u',   6, 21,    17 ),
        
        f( 'u',   8,  7,    15 ),
        f( 'd',   8, 10,    25 ),
        f( 'd',  10,  7,    10 ),
        
        f( 'u',  12,  5,    45 ),
        f( 'u',  12,  7,    35 ),
        f( 'd',  12, 10,    55 ),
        
        f( 'u',  17, 10,    34 ),
        f( 'u',  18, 18,    75 ),
        f( 'u',  18, 18,    65 ),
]

# val1 - ignoring status -- XXX IGNORED, TODO
# val2 - taking status into account
# Tuk se promenya TimeTrans posledovatelno 
test0 = [#trans/valid   val1  val2
        t(  1,   1,     None, None, 'both below min'),
        t(  8,  21,     17  , 17,   'both exact, trans < valid'),
        t(  5,   5,      9  , None, 'both exact =min, multiple matching db records'),
        t( 18,  18,     65  , 65  , 'both exact =max, multiple matching db records'),
        t( 17,  18,     34  , 34  , 'both exact - trans > valid '),
        t( 15,  15,     55  , None, 'both above max'),
        
        t(  1,   5,     None, None, 'trans below - valid exact'),
        t(  1,  10,     25  , None, 'trans below - valid exact_2'),
        t(  1,   6,     25  , None, 'trans below - valid between'),
        
        t(  8,   1,     None, None, 'trans exact - valid below min'),
        t(  8,   8,     15  , 15  , 'trans exact - valid between'),
        t(  8,  10,     25  , None, 'trans exact - valid exact'),
        t(  8,  12,     25  , None, 'trans exact - valid above max'),
        
        t(  9,   7,     15  , 15  , 'trans between - valid exact'),
        t(  9,  21,     17  , 17  , 'trans between - valid exact as max'),
        t(  9,   8,     15  , 15  , 'trans between - valid between'),
        t(  9,   9,     15  , 15  , 'trans between - valid between and same'),
        t(  9,   4,     None, None, 'trans between - valid below min'),
        t(  9,  12,     25  , None, 'trans between - valid above max'),
        
        t( 15,   4,     None, None, 'trans above max - valid below min'),
        t( 15,   9,     35  , 35  , 'trans above max - valid between'),
        t( 19,  17,     34  , 34  , 'suspicious for bug'), #pants crash
]

idb2 = [#  op  trans/valid  value  FOR RANGE !!!
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
test2 = [#trans/valid  val1  val2
        t(  7,   9,     10,   10, 'both exact - trans > valid _2'),
        t(  7,  12,     15, None, 'trans exact, valid between _2'),
]
# Tuk se uvelichava TimeValid s razlichni TimeTrans
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
test3 = [#trans/valid   val1  val2   info      
        t(  1,   1,     None, None, 'both below min'),
        t(  5,   1,     None, None, 'valid below min - trans between'),
        t(  16,  1,     None, None, 'valid below min - trans above'),
        
        t(  1,   3,     None, None, 'valid exact - trans below min'),
        t(  4,   3,       60,   60, 'valid exact - trans exact'),
        t(  8,   3,       55,   55, 'valid exact - trans exact - multiple recs'),
        t(  12,  3,     None, None, 'valid exact - trans exact - disabled'),
        t(  6,   3,       60,   60, 'valid exact - trans between'),
        t(  16,  3,       70,   70, 'valid exact - trans above'),
        
        t(  1,   4,     None, None, 'valid between - trans below min'),
        t(  4,   4,       60,   60, 'valid between - trans exact'),
        t(  9,   4,       55,   55, 'valid between - trans between'),
        t(  16,  4,       70,   70, 'valid between - trans above'),
        
        t(  1,  16,     None, None, 'valid above - trans below'),
        t(  5,  16,       35,   35, 'valid above - trans between'),
        t(  8,  16,       30,   30, 'valid above - trans exact - multiple records'),
        t(  12, 16,     None, None, 'valid above - trans exact - disabled'),
        t(  16, 16,       45,   45, 'valid above - trans above'),
    # more to be added
]

idb4 = [#  op  trans/valid  value  XXX A tova pyk kyde se polzva??
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
         #trans/valid         val1  val2   info 
        t( d2(  1), d2(  1),  None, None, 'COMB: trans below min - valid below min' ),
        t( d2(  1), d2( 11),  None, None, 'COMB: trans below min - valid exact' ),
        t( d2(  1), d2( 10),  None, None, 'COMB: trans below min - valid between' ),
        t( d2(  1), d2( 25),  None, None, 'COMB: trans below min - valid above max' ),
        t( d2( 11), d2(  1),  None, None, 'COMB: trans exact - valid below min' ),
        t( d2(  7), d2( 12),    38,   38, 'COMB: trans exact - valid between' ),
        t( d2( 11), d2(  3),     3,    3, 'COMB: trans exact - valid exact: Trans > Valid' ),
        t( d2(  3), d2( 11),    36,   36, 'COMB: trans exact - valid exact: Trans < Valid' ),
        t( d2(  7), d2( 25),    74,   74, 'COMB: trans exact - valid above max' ),
        t( d2( 12), d2(  1),  None, None, 'COMB: trans between - valid below min' ),
        t( d2( 12), d2(  4),     3,    3, 'COMB: trans between - valid between' ),
        t( d2( 12), d2(  4),     3,    3, 'COMB: trans between - valid exact' ),
        t( d2(  4), d2( 25),    72,   72, 'COMB: trans between - valid above max' ),
        t( d2( 25), d2(  1),  None, None, 'COMB: trans above max - valid below min' ),
        t( d2( 25), d2(  7),    25,   25, 'COMB: trans above max - valid exact' ),
        t( d2( 25), d2(  4),     7,    7, 'COMB: trans above max - valid between' ),
        t( d2( 25), d2( 25),    80,   80, 'COMB: trans above max - valid above max' ),
]

class RangeSample( TestSample):
    def __init__( me, trans, validFrom, validTo, ignoreStatusVal, expectedVal, name =''):
        name = 'RANGE: ' + name
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
        #trans,vfrom,vto    val1 val2            info
        r(   1,   1,   1,   111, []      ,     'trans below min, from,to below min'),
        r(   1,   1,  15,   111, []      ,     'trans below min, vfrom below min, vto exact'),
        r(   1,   1,  10,   111, []      ,     'trans below min, vfrom below min, vto between'),
        r(   1,   1,  19,   111, []      ,     'trans below min, vfrom below min, vto above'),
        
        r(   1,   10,   1,   111, []     ,     'trans below min, vfrom between,to below min'),
        r(   1,   10,  15,   111, []     ,     'trans below min, vfrom between, vto exact'),
        r(   1,   10,  10,   111, []     ,     'trans below min, vfrom between, vto between'),
        r(   1,   10,  19,   111, []     ,     'trans below min, vfrom between, vto above'),
        
        r(   1,   11,   1,   111, []     ,     'trans below min, vfrom exact,to below min'),
        r(   1,   11,  15,   111, []     ,     'trans below min, vfrom exact, vto exact'),
        r(   1,   11,  10,   111, []     ,     'trans below min, vfrom exact, vto between'),
        r(   1,   11,  19,   111, []     ,     'trans below min, vfrom exact, vto above'),
        
        r(   9,   1,   1,   111, []      ,     'trans exact, vfrom below min, vto below min '),
        r(   9,   1,  10,   111, [20]      ,   'trans exact, vfrom below min, vto between'),
        r(   9,   1,  15,   111, [20, 25,100], 'trans exact, vfrom below min, vto exact'),
        r(   9,   1,  19,   111, [20,25,100],  'trans exact, vfrom below min, vto above'),
        
        r(   9,   10,   1,   111, []      ,    'trans exact, vfrom between, vto below min '),
        r(   9,   10,  15,   111, [25,100],    'trans exact, vfrom between, vto exact'),
        r(   9,   10,  10,   111, []      ,    'trans exact, vfrom between, vto between '),
        r(   9,   10,  19,   111, [25,100],    'trans exact, vfrom between, vto above '),
        
        r(   9,   11,   1,   111, []      ,    'trans exact, vfrom exact, vto below min '),
        r(   9,   11,  15,   111, [25,100],    'trans exact, vfrom exact, vto exact'),
        r(   9,   11,  10,   111, []      ,    'trans exact, vfrom exact, vto between '),
        r(   9,   11,  19,   111, [25,100],    'trans exact, vfrom exact, vto above '),
        
        r(   9,   19,   1,   111, []      ,    'trans exact, vfrom above, vto below min '),
        r(   9,   19,  15,   111, []      ,    'trans exact, vfrom above, vto exact'),
        r(   9,   19,  10,   111, []      ,    'trans exact, vfrom above, vto between '),
        r(   9,   19,  19,   111, []      ,    'trans exact, vfrom above, vto above '),
        
        r(  10,   1,   1,   111, []      ,     'trans between, vfrom below min, vto below min '),
        r(  10,   1,  10,   111, [20]      ,   'trans between, vfrom below min, vto between'),
        r(  10,   1,  15,   111, [20, 25,100], 'trans between, vfrom below min, vto exact'),
        r(  10,   1,  19,   111, [20,25,100],  'trans between, vfrom below min, vto above'),
        
        r(  10,   10,   1,   111, []      ,    'trans between, vfrom between, vto below min '),
        r(  10,   10,  15,   111, [25,100],    'trans between, vfrom between, vto exact'),
        r(  10,   10,  10,   111, []      ,    'trans between, vfrom between, vto between '),
        r(  10,   10,  19,   111, [25,100],    'trans between, vfrom between, vto above '),
        
        r(  10,   11,   1,   111, []      ,    'trans between, vfrom exact, vto below min '),
        r(  10,   11,  15,   111, [25,100],    'trans between, vfrom exact, vto exact'),
        r(  10,   11,  10,   111, []      ,    'trans between, vfrom exact, vto between '),
        r(  10,   11,  19,   111, [25,100],    'trans between, vfrom exact, vto above '),
        
        r(  10,   19,   1,   111, []      ,    'trans between, vfrom above, vto below min '),
        r(  10,   19,  15,   111, []      ,    'trans between, vfrom above, vto exact'),
        r(  10,   19,  10,   111, []      ,    'trans between, vfrom above, vto between '),
        r(  10,   19,  19,   111, []      ,    'trans between, vfrom above, vto above '),
        
        r(  19,   1,   1,   111, []      ,             'trans above, vfrom below min, vto below '),
        r(  19,   1,  10,   111, [30]      ,           'trans above, vfrom below min, vto between'),
        r(  19,   1,  15,   111, [30, 35, 34, 100],    'trans above, vfrom below min, vto exact'),
        r(  19,   1,  19,   111, [30,35,34,100,45,65], 'trans above, vfrom below min, vto above'),
        
        r(  19,   10,   1,   111, []      ,         'trans above, vfrom between, vto below min '),
        r(  19,   10,  15,   111, [35,34,100],      'trans above, vfrom between, vto exact'),
        r(  19,   10,  10,   111, []      ,         'trans above, vfrom between, vto between '),
        r(  19,   10,  19,   111,[35,34,100,45,65], 'trans above, vfrom between, vto above '),
        
        r(  19,   11,   1,   111, []      ,         'trans above, vfrom exact, vto below min '),
        r(  19,   11,  15,   111, [35,34,100],      'trans above, vfrom exact, vto exact'),
        r(  19,   11,  10,   111, []      ,         'trans above, vfrom exact, vto between '),
        r(  19,   11,  19,   111, [35,34,100,45,65],'trans above, vfrom exact, vto above '),
        
        r(  19,   19,   1,   111, []     ,     'trans above, vfrom above, vto below min '),
        r(  19,   19,  15,   111, []     ,     'trans above, vfrom above, vto exact'),
        r(  19,   19,  10,   111, []     ,     'trans above, vfrom above, vto between '),
        r(  19,   19,  19,   111, []     ,     'trans above, vfrom above, vto above '),
        
        r(   9,  15,  11,   111, []      ,      'all exact, from > to, trans < valid'),
        r(  12,  18,  18,   111, []      ,      'trans between, from/to exact as max'),
        r(  15,   9,  11,   111, [30,35] ,      'trans between, from/to exact, trans>valid, >1 res'),
        r(  11,  12,  14,   111, [34]    ,      'trans exact, valids between _2'),
        r(   7,   8,  12,   111, [10,15] ,      'trans exact, from below min, to between, >1 res'),
        r(  19,  10,  17,   111, [35,34,100,45],'trans above max, valids between, db-same records'),
        r(   9,  11,  16,   111, [25,100],      'all exact, trans < valid from/to' ),
        r(  18,  18,  18,   111, [65]    ,      'all exact as max, db-same records'),
        
        r(  18,  14,  18,   111, [34,100,45,65],'trans exact as valid_to'),####
        r(  18,  18,  17,   111, []      ,      'trans exact as valid_from, from > to'),
        r(  18,  18,  20,   111, [65]    ,      'trans exact as valid_from, from < to, 1 res'),
        r(  14,  14,  20,   111, [34,100,45],   'trans exact as valid_from, from < to, >1 res'),
        
        r(  20,  19,  17,   111, []      ,      'trans > valid, from > to'),
        r(  18,  20,  27,   111, []      ,      'all above max'),
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
        t(  6,  1,     None, None, 'not exact in db'),
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
