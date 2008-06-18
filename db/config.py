#$Id$
# -*- coding: cp1251 -*-
from sqlalchemy import Numeric

TransTimeType   = Numeric
ValidTimeType   = Numeric
BaseClass4Mixin = object
BaseClass4check = object    #only subclasses of this are allowed to be bitemporal
db_id_name      = 'dbid'    #dbcook.config.column4ID.name

class runtime:              #configuration that can come e.g. from command line
    forced_trans = False
    validAsTrans = False
    notimed = False

def rootTable( klas ):
    raise NotImplementedError
    return mostBaseMappableDBTable_of_klas
def defaultTimeContext( klas):
    raise NotImplementedError
    return bitemporal_tuple     #type,order XXX ???
def now( me):
    raise NotImplementedError
    return transaction_time     #type same as me.time_valid and me.time_trans
# vim:ts=4:sw=4:expandtab
