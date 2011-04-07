#$Id$
# -*- coding: cp1251 -*-
'''Timed2 aspect'''

import config
import timed_sa as timed2

class Timed2Mixin_data( config.BaseClass4Mixin):
    ''' requires:
    db_id: uniq
    obj_id: distinguishes between different objects, many versions have same obj_id
    disabled: bool
    allInstances_basic() method as a query to start with
provides:
    time_valid: time(stamp) of start of validity of the object - usually user-filled with default from the clock
    time_trans: time(stamp) of transaction - usually comes directly from the clock
see timed_sa for details/changing names of these.
    '''
    __slots__ = ()

    time_valid  = config.ValidTimeType()
    time_trans  = config.TransTimeType()
    DBCOOK_nonoptionals= 'time_trans time_valid'.split()
    DBCOOK_no_mapping = True

    def pre_save( me):
        '''this should be called before save/insert by MapperExt or SessionExt (requires mapper).
        see alternative DBCOOK_defaults below
        '''
        trans = config.now()
        if not config.runtime.forced_trans:
            assert not me.revision4trans
            me.time_trans = trans
        if config.runtime.validAsTrans:
            assert not me.revision4trans
            me.time_valid = me.time_trans
        elif not me.time_valid:
            me.time_valid = trans
        if not me.revision4trans:
            if me.time_trans is None:   #?? XXX
                me.time_trans = trans   #??

    #alternative: does not require a mapper
    # but does not support config.runtime.forced_trans / config.runtime.validAsTrans
    #DBCOOK_defaults = dict( time_trans= config.now, time_valid= config.now)

class Timed2Mixin( Timed2Mixin_data):
    __slots__ = ()
    #config
    default4query_timeTo    = classmethod( config.defaultTimeContext)
    default4query_timeFrom  = classmethod( config.defaultTimeContext)
    #now = config.now
    symbol4timeTo_default = symbol4timeFrom_default = 'default'
    symbol4timeTo_ever    = symbol4timeFrom_ever    = 'ever'
    # several possibilities:
    #  timeTo  ='default': replace with default4query_timeTo
    #  timeTo  ='last' : any time forward (no filter: timeTo=None)
    #  timeFrom='first': any time back (no filter: timeFrom=None)
    #  timeFrom='default': replace with default4query_timeFrom
    #   either one can be None or whatever
    #  now: defaultTimeContext4record -> trans & valid ???
    #
    #eo config

    revision4trans = config.revision4trans
    @classmethod
    def _revision4trans_kargs( me):
        return me.revision4trans and dict( timeTrans_attr='', revision_attr='time_trans') or {}

    @classmethod
    def _symbol2time( klas, time, isfrom):
        symbol4default = isfrom and klas.symbol4timeFrom_default or klas.symbol4timeTo_default
        symbol4ever    = isfrom and klas.symbol4timeFrom_ever    or klas.symbol4timeTo_ever
        defaultFunc    = isfrom and klas.default4query_timeFrom  or klas.default4query_timeTo
        if time is symbol4default: time = defaultFunc()
        if time is symbol4ever: time = None
        if time is not None:
            r = []
            #deftm = defaultFunc()
            #if deftm is symbol4ever: deftm = (symbol4ever,symbol4ever)
            #else: deftm = klas.time2key_valid_trans( deftm)
            #print 3333333333333, time, deftm

            #for x,xdef in zip( klas.time2key_valid_trans( time), deftm ):
            deftm = None
            for x in klas.time2key_valid_trans( time):
                if x is symbol4default:
                    if deftm is None:
                        deftm = defaultFunc()
                        deftm = deftm is symbol4ever and (symbol4ever,symbol4ever) or klas.time2key_valid_trans( deftm)
                        x = deftm[0]
                    else:
                        x = deftm[1]
                if x is symbol4ever: x = None
                r.append(x)

            #TODO: this required timeType to be able to hold None ??? XXX
            time = klas.key_valid_trans2time( r)
            #print 4444444444, time
        return time

    @classmethod
    def _make_timeTo( klas, time):
        return klas._symbol2time( time, isfrom=False)
    @classmethod
    def _make_timeFrom( klas, time):
        return klas._symbol2time( time, isfrom=True)

    @classmethod
    def get_version_last( klas, obj_id =None, time =None, timeFrom =None,
            with_disabled =False,
            query =None,
            **kargs4time
        ):
        '''returns ONE object-version (or None) if single obj_id specified;
        else returns many objects'''

        if query is None: query = klas.allInstances_basic()
        if config.runtime.notimed: return query     #shunt4testing  - not proper
        kargs = kargs4time
        kargs.update( klas._revision4trans_kargs() )
        return timed2.get_lastversion( query,
                        obj_id= obj_id,
                        time= klas._make_timeTo( time),
                        timeFrom= klas._make_timeFrom( timeFrom),
                        with_disabled= with_disabled,
                        time2key_valid_trans= klas.time2key_valid_trans,
                        dbid_attr= config.db_id_name,
                        is_type_needed = config.is_type_needed,
                        **kargs
                )
    get_obj_lastversion = get_version_last

    @classmethod
    def get_allobj_lastversion( klas, **kargs):
        return klas.get_version_last( obj_id=None, **kargs)
    allInstances = get_allobj_lastversion

    @classmethod
    def get_version_history( klas, obj_id =None, timeFrom= None, timeTo= None,
            with_disabled =False,
            lastver_only_if_same_time =True,
            order_by_time_then_obj =False,
            clause_only =False,
            times_only =False,  #only makes sense if not clause_only
            query =None,
            **kargs4time
        ):
        'always returns many objects'

        if config.runtime.notimed: return None    #shunt4testing
        assert issubclass( klas, config.BaseClass4check), (klas,config.BaseClass4check)
        if query is None: query = klas.allInstances_basic()
        kargs = kargs4time
        kargs.update( klas._revision4trans_kargs() )

        return timed2.get_history( query,
                        obj_id,
                        timeFrom = klas._make_timeFrom( timeFrom),
                        timeTo = klas._make_timeTo( timeTo),
                        with_disabled= with_disabled,
                        lastver_only_if_same_time= lastver_only_if_same_time,
                        time2key_valid_trans= klas.time2key_valid_trans,
                        order_by_time_then_obj= order_by_time_then_obj,
                        dbid_attr= config.db_id_name,

                        clause_only = clause_only,
                        times_only = times_only,
                        is_type_needed = config.is_type_needed,
                        **kargs
                )
    get_obj_history = get_version_history

    #default: time is a dict(valid=,trans=)
    @staticmethod
    def key_valid_trans2time( tkey):
        timeValid, timeTrans = tkey
        return dict( trans= timeTrans, valid= timeValid)
    @staticmethod
    def time2key_valid_trans( time):
        return time['valid'], time['trans']


# vim:ts=4:sw=4:expandtab
