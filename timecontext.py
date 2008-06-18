#$Id$
# -*- coding: cp1251 -*-

'''
TimeContext: ������� �������� �� ������ ��������/������� - ���-�������� (bi-temporal).
    trans_time: ����� �� ���������� �� ������������/���������
    valid_time: ��/�� ���� � ������� ����������/��������� (������)
����������:
 - �� �� ������ ���� ���������� ����� (�������� ������?) � Timed*
 - �� �� ������� ���������� �� ���������: t.trans, t.valid
 - �� �� ������ ��������� ������ ����� - _����_ � �������
�.�. ����. �������/�������� � ���.�����

������ �����-�������� �����/��������� �� �������� �� ����� �������-��������.
    ����. �� x = a+b, ������ � � b �� �������, ������ �� �������� ����:
    x = a.get( time) + b.get( time)

�� ��������� ��� ���������� ��� �������� ����������� �� �������������/�������� �� ���������� ��:

 - Translator* - �������� ��������� ������ � ������� �� �������� �� �����:
      x=a+b->
        t = Translator( time, locals() )
        x = t.a + t.b
    Translator1 � �����, �� �� ������ � ���������� ������, �.�. b.c.d ������ �� �� ������� �������������:
      x=a+b.c.d->
        t = Translator1( time, a=a, bcd=b.c.d )
        x = t.a + t.bcd
    Translator2 � ������ � ���������� ������, �� ���� �� �� ������ ��� ������ ������:
      x=a+b.c.d->
        t = Translator2( time, locals() )
        x = t.a + t.b.c.d

 - �������� �������� �� �������:
    �� �� ������ �� ������ �������� ��� ���� �������� �������� (�.�. �� ������������/default)
    - ������ �� �� �� ������� �� �� ������������ !!
    - ������� �������� ��������� �� ������ TimedObj ������ (!), ����� ���� �� �� � �����������
    ��������:
        tmp = newDefaultTimeContext( time)
        x = a + b + c.get( time -1)
        tmp.restoreTimeContext()    #��� ���� ����������� ����������

'''

class TimeContext( object):
    '''
    ���� � �������� ������, �� ���� �� ���������� �� ��������.
    ������ �� �������� �� ���������� �����!
        - ������: ������� .trans, .valid, .as_trans_valid() � .as_valid_trans().
        - ���������: ���� ���� keyword ��������� (trans=,valid=),
            ��� �� ����� �� ���� �����.
    (��������� ������ valid � trans ���� �� �� ������� valid_time � trans_time)

    ������ ������� ������ �� �� �� ��� TimeContext.Time (����������);
    (��� ��� ������� TransTime, trans ������ �� � TransTime,

    ����� � ���� ���� ���������� �� ������ �������� �������, ����� � ��
    ��������� �� ����� �� �����, �� �� �������, ���� �� ������
    ��������� - �� ���� �� �� ������.
    '''
    __slots__ = 'trans valid'.split()

    Time = object
#    TransTime = None
    @classmethod
    def isTime( klas, time): return isinstance( time, klas.Time)
    _isTime = isTime    #save it
    @classmethod
    def isTransTime( klas, time): return isinstance( time, getattr( klas, 'TransTime', klas.Time))
    _isTransTime = isTransTime #save it

    def copy( me):
        return me.__class__( valid= me.valid, trans= me.trans)

    def __init__( me, **kargs):
        ''' constructor( trans=, valid=) '''
        return me.__init__2( **kargs)

    def __init__2( me, valid, trans):
        assert me.isTime( valid), `valid`
        assert me.isTransTime( trans), `trans`
        me.trans = trans
        me.valid = valid

    if 0:
        class _Pickler( object):
            def __new__( klas, trans, valid):
                return TimeContext( valid=valid, trans=trans)
        def __reduce__( me):
            return _Pickler, me.as_trans_valid()
    else:
        def __getstate__( me):
            return dict( trans= me.trans, valid= me.valid)
        def __setstate__( me, statedict):
            me.trans = statedict[ 'trans']
            me.valid = statedict[ 'valid']

    time_valid = valid_time = property( lambda me: me.valid)
    time_trans = trans_time = property( lambda me: me.trans)
    def as_trans_valid( me): return me.trans, me.valid
    def as_valid_trans( me): return me.valid, me.trans
    def __str__( me): return 'TimeContext( trans=%r, valid=%r)' % (me.trans, me.valid)
    __repr__ = __str__
    def __eq__( me, o): return me.trans==o.trans and me.valid==o.valid
    def __ne__( me, o): return me.trans!=o.trans or  me.valid!=o.valid

####
    if 0:
        _names4valid = 'valid valid_time time_valid'.split()
        _names4trans = 'trans trans_time time_trans'.split()
        def __init__( me, **kargs):
            ''' ctor( trans=, valid=)
                ctor( trans_time=, valid_time=)
                ctor( time_trans=, time_valid=)
            '''
            valid = trans = None
            _names4valid = me._names4valid
            _names4trans = me._names4trans
            for k,v in kargs.iteritems():
                if k in _names4valid:
                    if valid is None: valid = v
                    else: raise TypeError, 'multiple values fortime_valid; use only keyword arg one of ' + _names4valid
                if k in _names4trans:
                    if trans is None: trans = v
                    else: raise TypeError, 'multiple values for time_trans; use only keyword arg one of ' + _names4trans
            if valid is None:
                raise TypeError, 'time_valid not specified; use one keyword arg of ' + _names4valid
            if trans is None:
                raise TypeError, 'time_trans not specified; use one keyword arg of ' + _names4trans

            me.__init__2( trans=trans, valid=valid)

    if 0:
        class DefaultTimeContext( object):
            #XXX
            ''' ��������!:
                a = DefaultTimeContext( xx)
                b = DefaultTimeContext( yy)
               ������ ����� �� ������ (�������� � yy), ������
                d = DefaultTimeContext( xx)
                d = DefaultTimeContext( yy)     #������ d!
               ���� �� �� ������� ������� �� ������ - ������ xx !!??
            '''#XXX

            import threading
            _thread_default = threading.local()
            _thread_default.timeContexts = []
            pushDefaultTimeContext = _thread_default.timeContexts.append
            popDefaultTimeContext  = _thread_default.timeContexts.pop

            def last( me): return me._thread_default.timeContexts[-1]
            __slots__ = ( 'any',)
            def __init__( me, tm):
                assert isinstance( tm, TimeContext)
                me.pushDefaultTimeContext( tm)
                me.any = True
                print 'push'
            def restore( me):
                if (me.any): me.popDefaultTimeContext()
                me.any = False
                print 'restore'
            __del__ = restore

        def default(): return DefaultTimeContext.last()


TM = TimeContext
#_Pickler = TimeContext._Pickler

import timed2 as _timed2
class _Timed2overTimeContext( _timed2.Timed2):
    __slots__ = ()
    TimeContext = TimeContext

    #to Timed2 internal protocol
    def time2key_valid_trans( me, time):
        assert isinstance( time, me.TimeContext)
        return time.as_valid_trans()

    #from Timed2 internal protocol
    def key_valid_trans2time( me, (valid, trans) ):
        return me.TimeContext( trans=trans, valid=valid)


class _Test( _timed2.Test):
    @staticmethod
    def timekey2input( timed, (v,t)): return (t,v)
    @staticmethod
    def input2time( (t,v)): return TimeContext( trans=t,valid=v)

if __name__ == '__main__':
    try: c = TimeContext( 3,4)
    except TypeError: pass
    else: assert 0, 'must fail'
    try: c = TimeContext( trans=3)
    except TypeError: pass
    else: assert 0, 'must fail'
    try: c = TimeContext( valid=4)
    except TypeError: pass
    else: assert 0, 'must fail'

    c = TimeContext( trans=1,valid=2)

    import pickle
    s = pickle.dumps( c)
    x = pickle.loads( s)
    assert x is not c
    assert x == c

    test2 = _Test()
    t = _Timed2overTimeContext()
    objects = test2.fill( t, [1,3,2,4]  )
    err = test2.test_db( t)
#    if not err: print t
    test2.test_get( t, objects,)
    test2.exit()

# vim:ts=4:sw=4:expandtab
