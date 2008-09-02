#$Id$
# -*- coding: cp1251 -*-

'''
����������� �� ��������/������� �� ��������� '������/��������':
 1: ������� ������� �� �����������:
    - �� �� ���� ������
    - ��������� �� � ������ � ������ - ���� �� � ������� (��/�������)
    - �� ���� �� �� ������ ����������� ����� ���� ������ - �� ���� ���� �� ����
 2: ����� �� ������ �� ������ ��� ���������, ����. �������� ������:
    - �� �� ���� ������
    - �� ���� �� �� ������ ����������� ����� ���� ������
 3: �����/������� �� ������� ���������/disabled �� ������, � �� ����� ���� ���������� �����:
    - ���� �� �� ������ ����������� ����� - ������� �� �� ����
    - ������� �� ����, �.�. ������ �� �� ����� _�����_ + ������ ���������
 4: ����� �� ������, ����� ��� ���������, � �� ������ ����� �������� ��� ������:
    - �� ������ �� ������ 100%, ����. isinstance, issubclass ������ �� ��
        �������� �� ������ ������, � �� ��������

 == ����� �� ����������, �� ��������� ����� ������ �� �� ���� ����������
    (����. ���������� ������� ����� �����������)
 5: ����������� �� ����� ���� _������_ ����� �� ����� ������� ������,
        ��������� "������� ���������"
    - ��� � ����� ���������� � ������� �� �����������, �� �� ������ �� �� ����� ������������,
        � ���������� ���� �� �� � ����� ���� � ������� �� ����������� - ������ �� �������/���� -
        (Timed2 ���� �� �� �������, �� ������ �� �� ����� ��� �-����� <= �-�����-��-�����������)
        � �� ������� ��������� �� ������� Timed* ����!

�������� ��� ��� 2 �������� ������� �� "���������� �� �������� �����":
e������ � _�������_ �������� � ������� �� ��������� (2,3,4 ����� ����),
������� � "��� �������� ������� ��������" (5, � ���-��-� � ����������� �� �����������).

 6: ��� �������, �� � ����� �� �� ����� ������� �������� � ������� �� ���������,
������ �� �� ������� ���������� �� 1 � ����� ������: �������� �� ������ ����� �� ��,
� ��� ������� ������� �� �����������, ����� ����� ���������+������ ��� ����� �� ���������.

����������� �� ����������/�������� �� ����������� ��� ������������:
 �: ����� �������: (���� ����� - ��� �����, ��� ���������)
    return ������ / ������ (������ ������ None/None - ��� ������� � ���������)
 �: ����������: (���� ����� - ��� �����, ��� ���������)
    raise ������ / ������
 �: ������� �� ������� � ������ (�� ������ � �������� ???)
    obj.disabled = ������ / ������; return obj
 �: ����� �� ������, ����� ��� ���������, � �� ������ ����� �������� ��� ������:
    return WrapProxy( obj, disabled= ������/������)
    - �� ������ �� ������ 100% (���� ���� 4 ��-����)

------- ����� -----
 - ����������� �� ���� '�� ������ _������_ ��� � ���� ������' ���� �� �� � ������������:
    ����. ��� ������� �� ������(1.11); ����� �� ������(5.11); ����� �� ����� ��������( 3.11)
    ���������� ��� 5.11 � � ��� ����������� �� � �������� - ���/���� �����.
    ������� ��, ���� �� ����� �� ������ �� �� �������/����� ��������� �� ������ ����� - ������
    ��������� �� ���� ������ �� �� ����� �� ����� ��-������ ����.
 - 3) � �) �� ������ ����� ��� ������ ������ �� ���� .disabled �� �������;
    ����� ���� ���������� ���� �� � ����� ����� ��������;
 - 5) �������� ���-��������� - ���� �������� ���������... � ����� �� � ��?

��, ��� �� ����?

'''


class _Disabled4Timed( object):
    __slots__ = ()
    DONT_DISABLE_ALREADY_DISABLED = False

    # ������ �� Timed* ������:
    #NOT_FOUND = ... from timed
    #_get_val()
    #_put_val()
    #_get_range_val()

  #################

    def _encode( me, value, disabled): raise NotImplementedError
    def _decode( me, value): raise NotImplementedError

    def _interpret_value( me, value, with_disabled, only_value):
        #if not only_value:
        rkey,value = value
        value,disabled = me._decode( value)
        if disabled:
            if not with_disabled:
                return me.NOT_FOUND
            assert me.STORAGE_TYPE != _STORAGE.SYMBOL_INSTEAD_OF_OBJECT
                # �������� ���� _get
                #XXX ��� ������: ������ �� ������ ���������� ������� �������� ����� �����������.
                #XXX ������� ��������� �� Timed* ������!

                # �������� ���� _getRange
                #XXX ��� ������: ����� �� �� ����� ����: r[-1]? ��� ���� ���� None?
        return me._result( rkey, value, only_value, convert_key2time=False)

    #XXX only_value= � ���� �� �� �� ����;
    #XXX ����� (��� ����� � kargs), �� �� ���� ����� � �� default � _get_val -> ����� � ���������
    def _get( me, time, with_disabled =False, only_value =True, **kargs):
        value = me._get_val( time, only_value=False, **kargs)
        if value is me.NOT_FOUND:
            return value            #none yet
        return me._interpret_value( value, with_disabled, only_value)

    def _getRange( me, timeFrom, timeTo, with_disabled =False, only_value =True, **kargs):
        r = []
        for value in me._get_range_val( timeFrom, timeTo, only_value=False, **kargs):
            value = me._interpret_value( value, with_disabled, only_value)
            if value is me.NOT_FOUND: continue
            r.append( value)
        return r

    def _put( me, value, time, disabled =False):
        value = me._encode( value, disabled)
        me._put_val( value, time)

    def disable( me, time):
        get_val = me.DONT_DISABLE_ALREADY_DISABLED and me._get or me._get_val
        value = get_val( time)
        if value is not me.NOT_FOUND:
            me._put( value, time, disabled=True)
    delete = disable


class Disabled4Timed_WrapperTuple( _Disabled4Timed): #value ���� �� ���� ���� � disabled !
    def _encode( me, value, disabled): return (value, disabled)
    def _decode( me, value): return value

class Disabled4Timed_SymbolInsteadOfObject( _Disabled4Timed):
    class Symbol4Disabled: pass
    def _encode( me, value, disabled): return me.Symbol4Disabled
    def _decode( me, value): return (value, value is me.Symbol4Disabled)

class Disabled4Timed_ObjectAttr( _Disabled4Timed): #value �� ���� disabled
    #XXX ��� ������ �� �� �� ����� �����? #except AttributeError:
    #error, cannot be disabled
    def _encode( me, value, disabled): return disabled
    def _decode( me, value): return (value, value.disabled)

Disabled4Timed = Disabled4Timed_WrapperTuple


# vim:ts=4:sw=4:expandtab:enc=cp1251:fenc=
