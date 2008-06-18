#$Id$
# -*- coding: cp1251 -*-

from timecontext import TimeContext, _Timed2overTimeContext

from disabled import Disabled4Timed as _Disabled4Timed
class TimedObject( _Timed2overTimeContext, _Disabled4Timed):
    '''
    всички времеви обекти трябва да наследяват този (освен модулите по-долу).

    иначе всичката тая сложнотия с наследяванията е за лесна подмяна/настройка -
    (всяка жаба да си гледа гьола).
    Крайният резултат може би трябва да е само един плосък клас - всичко в едно:
        - Timed2 ползва направо TimeContext, вместо тези преобразувания напред-назад
        - TimedObject == Disabled4Timed в/у Timed2 - без _get_val/_put_val
    като Тази йерархия трябва да се пази (съвместима) за лесно заместване
    '''
    __slots__ = ()
    def _get_val( me, time, **kargs):   return _Timed2overTimeContext.get( me, time, **kargs)
    def _get_range_val( me, timeFrom, timeTo, **kargs):   return _Timed2overTimeContext.getRange( me, timeFrom, timeTo, **kargs)
    def _put_val( me, value, time):     return _Timed2overTimeContext.put( me, value, time)

    get     = _Disabled4Timed._get
    put     = _Disabled4Timed._put
    delete  = _Disabled4Timed.delete
    getRange= _Disabled4Timed._getRange


###############

import module_timed as _module_timed
class _mod2time_converter( _module_timed.mod2time__trans_in_fname__valid_in_module):
    str2time1 = staticmethod( _module_timed.dateYYYYMMDD2datetime)
    def maketime( me, trans, valid):
        return TimeContext( trans=trans, valid=valid)

class TimedModule( _module_timed.Module):
    '''
    всички време-зависими модули (алгоритми, справки, документи и пр.)
    трябва да наследяват това.
    '''
    __slots__ = ()
    def __init__( me, name):
        _module_timed.Module.__init__( name,
                _Timed2overTimeContext,
                _mod2time_converter
            )

if __name__ == '__main__':

    from timecontext import _Test
    test2 = _Test()
    t = TimedObject()
    objects = test2.fill( t, [1,3,2,4]  )
    err = test2.test_db( t,)
    test2.test_get( t, objects,)
    if test2.err:
        test2.exit()

#####

    from timed_wrapper import test_protocol2Timed_protocol

    class Timed_Wrapper4test( TimedObject, test_protocol2Timed_protocol):
        '''testing purposes only'''
        @staticmethod
        def _valid_trans2time( valid, trans):
            return TimeContext( trans=trans, valid=valid)
        # test_protocol2Timed_protocol:
        timed_get = TimedObject.get
        timed_put = TimedObject.put
        timed_getRange = TimedObject.getRange
        # test_protocol:
        get = test_protocol2Timed_protocol.get
        put = test_protocol2Timed_protocol.put
        getRange = test_protocol2Timed_protocol.getRange

    import test
    test.test( Timed_Wrapper4test)

# vim:ts=4:sw=4:expandtab
