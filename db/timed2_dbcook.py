#$Id$
# -*- coding: cp1251 -*-
'''Timed2 aspect'''

import config
import timed_sa as timed2

class Timed2Mixin( config.BaseClass4Mixin):
    ''' requires the following fields in the database model object:
        db_id: uniq
        obj_id: distinguishes between different objects
        time_valid: time(stamp) of start of validity of the object - usually user-filled with default from the clock
        time_trans: time(stamp) of transaction - usually comes directly from the clock
       requires allInstances_basic() method as a query to start with
    '''
    __slots__ = ()

    time_valid  = config.ValidTimeType()
    time_trans  = config.TransTimeType()

    #config
    defaultTimeContext  = classmethod( config.defaultTimeContext)
    now = config.now
    #eo config

    @classmethod
    def get_version_last( klas, obj_id =None, time =None,
            #timeFrom =None,
            with_disabled =False,
            query =None
        ):
        'returns ONE objects (or None) if single obj_id specified; else returns many objects'

        if query is None: query = klas.allInstances_basic()
        if config.runtime.notimed: return query     #shunt4testing  - not proper
        if time is None: time = klas.defaultTimeContext()
        return timed2.get_lastversion( klas, query,
                        obj_id=obj_id, time=time,
                        with_disabled= with_disabled,
                        time2key_valid_trans= klas.time2key_valid_trans,
                        dbid_attr= config.db_id_name,
                )
    get_obj_lastversion = get_version_last

    @classmethod
    def get_allobj_lastversion( klas, time= None,
            with_disabled =False,
            query =None
        ):
        old=0
        if old:
            query = klas.allInstances_basic()
            if config.runtime.notimed: return query    #shunt4testing  - not proper
            if time is None: time = klas.defaultTimeContext()
            from timed2_sa_objid_discriminator import get_all_objects_by_time
            return get_all_objects_by_time( klas, query,
                    time,
                    with_disabled= with_disabled,
                    basemost_table= klas.rootTable(),
                    time2key_valid_trans= klas.time2key_valid_trans,
                    db_id_name= config.db_id_name
                )
        return klas.get_version_last( None, time= time, with_disabled= with_disabled, query= query)
    allInstances = get_allobj_lastversion

    @classmethod
    def get_version_history( klas, obj_id =None, timeFrom= None, timeTo= None,
            with_disabled =False,
            lastver_only_if_same_time =True,
            order_by_time_then_obj =False,
            clause_only =False,
            times_only =False,  #only makes sense if not clause_only
            query =None
        ):
        'always returns many objects'

        if config.runtime.notimed: return None    #shunt4testing
        if timeFrom is None:
            timeTo = timeFrom = klas.defaultTimeContext()
        assert issubclass( klas, config.BaseClass4check), klas
        if query is None: query = klas.allInstances_basic()

        old=0
        if old:
            from timed2_sa_objid_discriminator import get_obj_history_in_timerange
            return get_obj_history_in_timerange( klas, query,
                    obj_id, timeFrom, timeTo,
                    #with_disabled= with_disabled,
                    group= lastver_only_if_same_time,
                    basemost_table= klas.rootTable(),
                    time2key_valid_trans= klas.time2key_valid_trans,
                    db_id_name= config.db_id_name
                )

        return timed2.get_history( klas, query,
                        obj_id, timeFrom, timeTo,
                        with_disabled= with_disabled,
                        lastver_only_if_same_time= lastver_only_if_same_time,
                        time2key_valid_trans= klas.time2key_valid_trans,
                        order_by_time_then_obj= order_by_time_then_obj,
                        dbid_attr= config.db_id_name,

                        clause_only = clause_only,
                        times_only = times_only,
                )
    get_obj_history = get_version_history
    @staticmethod
    def key_valid_trans2time( tkey):
        timeValid, timeTrans = tkey
        return dict( trans= timeTrans, valid= timeValid)
    @staticmethod
    def time2key_valid_trans( time):
        return time['valid'], time['trans']

    def pre_save( me):
        trans = me.now()
        if not config.runtime.forced_trans:
            me.time_trans = trans
        if config.runtime.validAsTrans:
            me.time_valid = me.time_trans
        elif not me.time_valid:
            me.time_valid = trans
        if me.time_trans is None:   #?? XXX
            me.time_trans = trans   #??

#### end of Timed2 aspect

# vim:ts=4:sw=4:expandtab
