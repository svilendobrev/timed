#$Id$
# -*- coding: cp1251 -*-

'''
times: 1t/2t
last_ver
   upto time/any
   single obj / many/ all obj
all_ver-history in time range
   from time/any - to time/any
   single obj / many/ all obj
result: clause / query
polymorphic (objid=type,oid) / non-polymorphic (objid=oid)

all timeto/timefrom can be None, meaning last/first ever

the objects/tables should have time/trans/valid/objid/dbid attributes into them;
the exact names of the attributes can be given at setup.
disabled_attr is also needed if filtering by disabled.

the externaly-useful functions are:
  2t:
    def get_lastversion_of_one( klas, query, obj_id,
            time =None, with_disabled =False, **setup_kargs):
    def get_lastversion_of_many( klas, query, obj_id =(),
            time =None, with_disabled =False, **setup_kargs):

    def get_lastversion( klas, query, obj_id =None,       #one or None or list/tuple
            time =None, with_disabled =False, **setup_kargs):
    def get_history( klas, query, obj_id,   #one or None or list/tuple
            timeFrom, timeTo,
            lastver_only_if_same_time =True,
            times_only =False,
            order_by_time_then_obj =False,
            with_disabled =False, **setup_kargs):
    last two are trying to guess and switch between above one/many, see _singular
    setup_kargs can be: (see _initkargs methods)
        timeTrans_attr ='time_trans'
        timeValid_attr ='time_valid'
        time2key_valid_trans = nothing  - convertor from input time into (valid,trans) tuple
        oid_attr  ='obj_id'
        dbid_attr ='db_id'
        disabled_attr ='disabled'
        is_type_needed =True    whether to add mapper.polymorphic_on type to oid discriminating -
            if obj_id are not unique across a polymorphic hierarchy (each leaf has own sequence)

  1t:
    get_1t_lastversion_of_one   #TODO no disabled
    get_1t_lastversion_of_many  #TODO no disabled
    range #TODO

 class-wise, the externaly useful methods are:
    q= .single_lastver(..)
    q= .all_lastver(..)
    q= .range(..)

    q= .filter_disabled(q)
    ...
'''
from sqlalchemy import select, func
from sqlalchemy.orm import class_mapper

class _versions( object):
    def __init__( me, query, **kargs):
        me.query = query
        me._initkargs( **kargs)

    _where0 = None
    def _get_where( me, where =None):
        where0 = me._where0
        if where0:
            if where: return where0 & where
            return where0
        return where

    def _query( me, filter):
        query = me.query
        if filter is not None: query = query.filter( filter)
        return query

    def single_lastver( me, oid, time =None, where =None):
        '''1t: last version of single object / последната версия на един обект'''
        me.upto_time( time)
        query = me._query( me._get_where( where))
        query = me.filter_type( query)
        return query.filter( me.c_oid == oid
                    ).order_by( *(c.desc() for c in me._order_by4single() )
                    ).first()

    _upto_time_value = None
    def upto_time( me, time):
        '''before and inclusive time'''
        me._upto_time_value = time
        if time is None: return None
        me._where0 = me._upto_time( time)

    def _initkargs( me, time_attr,
            oid_attr  ='obj_id',
            dbid_attr ='db_id',
            disabled_attr ='disabled',
            is_type_needed =True,
            klas =None
        ):
        if not klas:
            mapper = me.query.mapper
            klas = mapper.class_
        else:
            mapper = class_mapper( klas)
        me.klas = klas
        me.c_type = is_type_needed and mapper.polymorphic_on
        me.c_oid  = getattr( klas, oid_attr ).expression_element()
        me.c_time = getattr( klas, time_attr).expression_element()
        me.c_dbid = dbid_attr and getattr( klas, dbid_attr ).expression_element()
        me.disabled_attr = disabled_attr

    @staticmethod
    def _filter( query, expr, isquery =None):
        if isquery is None:     #autoguess
            isquery = hasattr( query, 'filter')
        if isquery:
            query = query.filter( expr)
        else:   #clause
            if query is None: query = expr
            else: query &= expr
        return query

    def filter_disabled( me, query):
        c_disabled = getattr( me.klas, me.disabled_attr).expression_element()
        #if not isquery: c_disabled = c_disabled.expression_element()
        f = ~c_disabled
        return me._filter( query, f)

    def filter_type( me, query):
        '''needed in polymorphic case, where object-identity is actualy type+oid
            and not just oid - oid is duplicated, as many leafs have their own sequences.
            must be applied where oid is used.
            test: model.models.Rabotodatel.populateEach / IkonomicheskiDeinosti.allInstances
        '''
        c_type = me.c_type
        if not c_type: return query
        if 1:
            mappers = class_mapper( me.klas ).polymorphic_iterator()
        else:   #needs query()!, sa>=4.5
            mappers = query._with_polymorphic
        alltypes = [ m.polymorphic_identity for m in mappers ]

        #if not isquery: c_type= c_type.expression_element()
        f = c_type.in_( alltypes)
        return me._filter( query, f)

class versions_1t( _versions):
    def _order_by4single( me): return me.c_time, me.c_dbid
    def _upto_time( me, time):
        '''before and inclusive time'''
        return me.c_time <= time

    def _alv_1( me, where =None, alias ='g1'):
        where = me._get_where( where)
        c_oid  = me.c_oid
        c_time = me.c_time
        where = me.filter_type( where)
        g1 = select( [  c_oid.label( 'oid'),
                        func.max( c_time).label( 'time')
                    ], where
                ).group_by( c_oid
                ).alias( alias)
        where1 = ( (c_oid== g1.c.oid) & (c_time== g1.c.time) )
        return g1, where1

    c_time2 = None
    def _alv_2_dbid( me, where =None, no_oid =False, alias =None):
        #1t:  sel1=oid,time,dbid       sel2=max/dbid           group_by=oid,time         where=c_dbid==g2.dbid
        #     no_dbid=0, c_time2=0
        #2t-b:sel1=oid,time,time2,dbid sel2=max/dbid           group_by=oid,time,time2   where=c_dbid==g2.dbid
        #     no_dbid=0, c_time2=1

        c_oid  = not no_oid and me.c_oid or None
        c_time = me.c_time
        c_dbid = me.c_dbid
        c_time2= me.c_time2
        where = me.filter_type( where)
        t = select( [                   c_time.label( 'time'  ),
                                        c_dbid.label( 'dbid'  ),
                    ]+( c_oid   and [   c_oid.label(  'oid'   )] or []
                    )+( c_time2 and [   c_time2.label('time2' )] or []
                    ), where ).alias( 'g02')

        g2= select( [   func.max( t.c.dbid ).label( 'dbid' ) ]
                ).group_by( *(  #order in the group_by does not matter?
                        ( c_oid   and [ t.c.oid   ] or []) +
                        [               t.c.time  ] +
                        ( c_time2 and [ t.c.time2 ] or [])
                ))

        if alias: g2 = g2.alias( alias)
        where2 = (c_dbid == g2.c.dbid)
        return g2, where2


    def _all_lastver( me, where =None, alias ='g2'):
        '''last versions of all objects: / последните версии на много обекти:
            for each distinct .oid,
                get those of maximum .time      #g1
                    of which for each distinct .time,
                        get the one of max .dbid  #g2
            #1: select a.* from a,
                        (select oid,max(time_attr) as mtime from a group by oid) as r
                    where a.oid==r.oid and a.time_attr==r.mtime ;
        '''
        g1, where1 = me._alv_1( where=where )
        if not me.c_dbid:
            return where1
        g2, where2 = me._alv_2_dbid( where=where1, alias=alias)
        return where2

    def all_lastver( me, time =None, where =None):
        me.upto_time( time)
        return me._query( me._all_lastver( where))

    def range( me, *a, **k):
        where = me._range( *a,**k)
        return me.query.filter( where)


class versions_2t( versions_1t):
    def _initkargs( me,
            timeTrans_attr= 'time_trans',
            timeValid_attr= 'time_valid',
            time2key_valid_trans =lambda x:x,
            **kargs):
        versions_1t._initkargs( me, time_attr= timeValid_attr, **kargs)
        me.c_time2 = getattr( me.klas, timeTrans_attr).expression_element()
        me.time2key_valid_trans = time2key_valid_trans
    def _order_by4single( me): return me.c_time, me.c_time2, me.c_dbid

    def _upto_time( me, time =None, c_time =None, c_time2 =None ):
        '''before and inclusive timestamp / validity'''
        if time is None: time = me._upto_time_value
        if time is None: return None
        timeValid, timeTrans = me.time2key_valid_trans( time)
        if c_time  is None: c_time  = me.c_time
        if c_time2 is None: c_time2 = me.c_time2
        return (c_time <= timeValid) & (c_time2 <= timeTrans)

    def _alv_2_nodbid( me, where =None, no_oid =False, alias ='g2'):
        #2t-a: sel1=oid,time,time2
        #      sel2=oid,time,max/time2 group_by=oid,time
        #      where=c_oid=g2.oid & c_time==g2.time & c_time2==g2.time2
        #     no_dbid=1, c_time2=1

        c_time2 = me.c_time2
        assert c_time2
        c_oid  = me.c_oid #not no_oid and me.c_oid or None
        c_time = me.c_time

        where = me.filter_type( where)
        t = select( [   c_time.label(   'time'  ),
                        c_time2.label(  'time2' ),
                        c_oid.label(    'oid'   ),
                    ], where ).alias( 'g02')
        where1 = me._upto_time( c_time= t.c.time, c_time2= t.c.time2 )
        #where1 = me.filter_type( where1)
        g2= select( [   func.max( t.c.time2 ).label( 'time2'),
                        t.c.time,
                        t.c.oid,
                    ],  where1
                ).group_by(
                        t.c.oid,
                        t.c.time
                        #(not no_oid and [ t.c.oid] or []) +
                        #[t.c.time ]
                )

        if alias: g2 = g2.alias( alias)
        where2 = (c_time == g2.c.time) & (c_time2 == g2.c.time2) & (c_oid == g2.c.oid)
        return g2, where2


    def _all_lastver( me, where =None):
        '''last versions of all objects: / последните версии на много обекти:
            for each distinct .oid,
                get those of maximum .time                  #g1
                    of which for each distinct .time,
                        get those of maximum .time2         #g2
                            of which for each distinct .time2,
                                get the one of max .dbid    #g3
        '''
        g1, where1 = me._alv_1( where= where)
        g2, where2 = me._alv_2_nodbid( where= where1 )
        g3, where3 = me._alv_2_dbid(   where= where2, alias= 'g3')
        return where3

    def _range( me, timeFrom, timeTo, oid =None, lastver_only_if_same_time =True):
        '''oid =None should give all oids
            for each distinct .oid,
                for each distinct .time,
                    get those of maximum .time2         #r1
                        of which for each distinct .time2,
                            get the one of max .dbid    #r2
        '''
        me.upto_time( None)
        timeValidFrom, timeTransFrom = me.time2key_valid_trans( timeFrom)
        timeValidTo,   timeTransTo   = me.time2key_valid_trans( timeTo)
        timeTrans = timeTransTo
        where = ( (me.c_time2 <= timeTransTo)
                & (me.c_time >= timeValidFrom)
                & (me.c_time <= timeValidTo) )


        single_oid = _singular( oid)
        if single_oid:
            where &= (me.c_oid == oid)
        elif oid:
            where &= me.c_oid.in_( oid)
        where = me.filter_type( where)
        if not lastver_only_if_same_time:
            return where
        r1,where2 = me._alv_2_nodbid( where=where,  no_oid= single_oid, alias= 'r1')
        r2,where3 = me._alv_2_dbid(   where=where2, no_oid= single_oid, alias= 'r2')
        return where3

def get_1t_lastversion_of_one( query, oid, time =None, klas =None, **setup_kargs):
    v = versions_1t( query, klas=klas, **setup_kargs)
    return v.single_lastver( oid, time=time)

def get_1t_lastversion_of_many( query, oid=(), time =None, klas =None, **setup_kargs):
    v = versions_1t( query, klas=klas, **setup_kargs)
    where = None
    if oid: where = v.c_oid.in_( oid)
    return v.all_lastver( time=time, where=where )


def get_lastversion_of_one( klas, query,
        obj_id,
        time =None,
        with_disabled =False,
        **setup_kargs
    ):

    v = versions_2t( query,
            klas= klas,
            **setup_kargs
        )

    q = None
    if not with_disabled: q = v.filter_disabled( q)
    q = v.single_lastver( obj_id, time, where=q )
    return q

def get_lastversion_of_many( klas, query,
        obj_id =(),
        time =None,
        with_disabled =False,
        **setup_kargs
    ):

    v = versions_2t( query,
            klas= klas,
            **setup_kargs
        )
    if 0:
        v.upto_time( time)
        w2 = v._all_lastver()
        if not with_disabled: w2 = v.filter_disabled( w2)
        return query.filter( w2)

    where = None
    if obj_id: where = v.c_oid.in_( obj_id)
    q = v.all_lastver( time, where=where )
    if not with_disabled: q = v.filter_disabled( q)
    return q

def _singular(x):
    if isinstance( x, basestring): return True
    if not x: return False
    try: iter(x)
    except TypeError: return True
    return False

def get_lastversion( klas, query,
        obj_id =None,       #one or None or list/tuple
        time =None,
        with_disabled =False,
        **setup_kargs
    ):
    func = _singular( obj_id) and get_lastversion_of_one or get_lastversion_of_many
    return func( klas, query,
                    obj_id= obj_id, time= time, with_disabled= with_disabled,
                    **setup_kargs )

def get_history( klas, query,
        obj_id, timeFrom, timeTo,
        with_disabled = False,
        lastver_only_if_same_time =True,
        clause_only =False,
        times_only =False,  #only makes sense if not clause_only
        order_by_time_then_obj =False,
        **setup_kargs
    ):

    #print kargs4timeclause_ignore.keys()
    v = versions_2t( query,
            klas= klas,
            **setup_kargs
        )

    order_by = [ v.c_oid, v.c_time ]
    if order_by_time_then_obj: order_by.reverse()

    range = (clause_only or times_only) and v._range or v.range
    q = range( timeFrom, timeTo, oid=obj_id, lastver_only_if_same_time=lastver_only_if_same_time )
    if not with_disabled: q = v.filter_disabled( q)
    if not clause_only:
        if times_only:
            #transfirst = isinstance( times_only, str) and ',' in times_only and times_only.startswith('t')
            q = select( [   v.c_time,
                            v.c_time2,
                        ], q
                    ).order_by( *order_by)
            q = query.session.execute( q)
        else:
            q = q.order_by( *order_by)
    return q

if __name__ == '__main__':
    import dbcook.usage.plainwrap as o2r
    class Txt( o2r.Type): pass
    class Int( o2r.Type): pass
    Base = o2r.Base
    from dbcook.util.attr import setattr_kargs
    Base.__init__ = setattr_kargs
    from dbcook.usage.samanager import SAdb
    SAdb.config.getopt()

    class A( Base):
        oid = Int()
        time = Int()
        z = Txt()

    from sqlalchemy import *

    fieldtypemap = {
        Txt: dict( type= String(100), ),
        Int: dict( type= Integer, ),
    }

    sa = SAdb()# echo=True)
    print sa.config
    sa.open( recreate=True)

    types = locals()
    b = sa.bind( types, builder= o2r.Builder, fieldtypemap= fieldtypemap, base_klas= Base )
    all = [
        A( oid=1, time=12, z='a12-last'),
        A( oid=1, time=2,  z='a2' ),
        A( oid=1, time=6,  z='a6' ),

        A( oid=2, time=2,  z='b1' ),
        A( oid=2, time=4,  z='b-last' ),

        A( oid=3, time=5,  z='c5 time-dup' ),
        A( oid=3, time=5,  z='c-last' ),

        A( oid=4, time=7,  z='d-last' ),
    ]

    session = sa.session()
    sa.saveall( session, *all )
    session.flush()
    session.clear()

    lasts_by_time_obj = set( a for a in all if 'last' in a.z or 'dup' in a.z )
    lasts_by_dbid_obj = set( a for a in all if 'last' in a.z )
    lasts_by_time_id  = set( a.db_id for a in lasts_by_time_obj )
    lasts_by_dbid_id  = set( a.db_id for a in lasts_by_dbid_obj )

    def test( q, expect, obj =True, db_id =True):
        r = set( q )
        for z in r: print z
        assert set( (db_id and (obj and x.db_id or x['db_id']) or x)
                    for x in r ) == set( expect), '''
        result: %(r)r
        expect: %(expect)r''' % locals()

    print '------- A all'
    for a in session.query(A): print a
    if 10*'byhand':
        a = sa.tables[A]

        print '====== oid,time last -group_by time'
        g1 = select( [   a.c.oid.label('mx'),
                        func.max( a.c.time).label('my'),
                ] ).group_by( A.oid).alias('g1')
        for z in session.execute( g1): print z

        print '------- Atbl for last times';
        o = a.select( (A.oid==g1.c.mx) & (A.time==g1.c.my) ).alias('o1')
        test( session.execute( o), lasts_by_time_id, obj=False)

        print '======= dbid last -group_by oid,time'
        g2 = select( [ func.max( o.c.db_id).label( 'nid')
                ] ).group_by( o.c.oid, o.c.time).alias('g2')
        for z in session.execute( g2): print z

        print '------- Atbl for last dbid for last times'
        q = a.select( (A.db_id==g2.c.nid) )
        test( session.execute( q), lasts_by_dbid_id, obj=False)


        print '======= A for last times'
        q = session.query(A).filter( (A.oid==g1.c.mx) & (A.time==g1.c.my) )
        test( q, lasts_by_time_id)

        print '------- A for last dbid for last times'
        q = session.query(A).filter( (A.db_id==g2.c.nid) )
        test( q, lasts_by_dbid_id)

        print '=================='

    print '------- last_versions by time'
    q = get_1t_lastversion_of_many(
            session.query( A), oid_attr='oid', time_attr='time', dbid_attr =None, )
    test( q, lasts_by_time_id)

    print '------- last_versions by dbid,time'
    q = get_1t_lastversion_of_many(
            session.query( A), oid_attr='oid', time_attr='time', dbid_attr='db_id', )
    test( q, lasts_by_dbid_id)

    print '=========== single last_version'
    for x in lasts_by_dbid_obj:
        q = get_1t_lastversion_of_one(
            session.query( A), oid_attr='oid', time_attr='time', dbid_attr='db_id',
            oid= x.oid )
        test( [q], [x.db_id] )

    print '=========== single last_version upto_time'
    v = versions_1t( session.query(A), oid_attr='oid', time_attr='time', dbid_attr='db_id', )
    f = v.single_lastver
    for q,r in [
            [ f( oid=1, time=1)   ,  None  ],
            [ f( oid=1, time=2).z ,  'a2'  ],
            [ f( oid=1, time=4).z ,  'a2'  ],
            [ f( oid=1, time=6).z ,  'a6'  ],
            [ f( oid=1, time=7).z ,  'a6'  ],
            [ f( oid=4, time=9).z ,  'd-last' ],
            [ f( oid=4, time=5)   ,  None  ],
        ]:
        test( [q], [r], db_id= False )

    print '=========== all last_versions time/dbid upto_time'
    v = versions_1t( session.query(A), oid_attr='oid', time_attr='time', dbid_attr='db_id', )
    q = v.all_lastver( time=5)
    test( q, [x.db_id for x in all if x.z in 'a2 b-last c-last'.split() ] )

# vim:ts=4:sw=4:expandtab
