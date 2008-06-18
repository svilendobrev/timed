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

class _STORAGE:
    WRAPPER_TUPLE = 2
    OBJECT_ATTR = 3
    SYMBOL_INSTEAD_OF_OBJECT = 5
    #SEPARATE_HISTORY6 = 6 #... ������ � �����!

#����������/��������
#? ���� � �)

class Disabled4Timed( object):
    __slots__ = ()
    _STORAGE = _STORAGE

    STORAGE_TYPE = _STORAGE.WRAPPER_TUPLE
    DONT_DISABLE_ALREADY_DISABLED = False

    # ������ �� Timed* ������:
    #NOT_FOUND = ... from timed
    #_get_val()
    #_put_val()
    #_get_range_val()

  #################
    if STORAGE_TYPE == _STORAGE.SYMBOL_INSTEAD_OF_OBJECT:
        class Symbol4Disabled: pass
    @classmethod
    def _decode( me, value):
        STORAGE_TYPE = me.STORAGE_TYPE
        if STORAGE_TYPE == _STORAGE.WRAPPER_TUPLE:
            value,disabled = value      #value ���� �� ���� ���� � disabled !
        elif STORAGE_TYPE == _STORAGE.OBJECT_ATTR:
            disabled = value.disabled   #value �� ���� disabled
        elif STORAGE_TYPE == _STORAGE.SYMBOL_INSTEAD_OF_OBJECT:
            disabled = value is me.Symbol4Disabled
        else: raise NotImplementedError
        return value,disabled

    #XXX only_value= � ���� �� �� �� ����;
    #XXX ����� (��� ����� � kargs), �� �� ���� ����� � �� default � _get_val -> ����� � ���������
    def _get( me, time, with_disabled =False, only_value =True, **kargs):
        value = me._get_val( time, only_value=only_value, **kargs)
        if value is me.NOT_FOUND:
            return value            #none yet

        if not only_value: rtime,value = value
        value,disabled = me._decode( value)
        if disabled:
            if not with_disabled:
                return me.NOT_FOUND
            assert me.STORAGE_TYPE != _STORAGE.SYMBOL_INSTEAD_OF_OBJECT
                #XXX ��� ������: ������ �� ������ ���������� ������� �������� ����� �����������.
                #XXX ������� ��������� �� Timed* ������!
        if not only_value: value = rtime,value
        return value

    def _getRange( me, timeFrom, timeTo, with_disabled =False, only_value =True, **kargs):
        r = []
        for value in me._get_range_val( timeFrom, timeTo, only_value=only_value, **kargs):
            if not only_value: rtime,value = value
            value,disabled = me._decode( value)
            if disabled:
                if not with_disabled:
                    continue
                assert me.STORAGE_TYPE != _STORAGE.SYMBOL_INSTEAD_OF_OBJECT
                    #XXX ��� ������: ����� �� �� ����� ����: r[-1]? ��� ���� ���� None?
            if not only_value: value = rtime,value
            r.append( value)
        return r

    def _put( me, value, time, disabled =False):
        STORAGE_TYPE = me.STORAGE_TYPE
        if STORAGE_TYPE == _STORAGE.WRAPPER_TUPLE:
            value = value,disabled
        elif STORAGE_TYPE == _STORAGE.OBJECT_ATTR:
            value.disabled = disabled
            #XXX ��� ������ �� �� �� ����� �����?
            #except AttributeError: #error, cannot be disabled
        elif STORAGE_TYPE == _STORAGE.SYMBOL_INSTEAD_OF_OBJECT:
            if disabled: value = me.Symbol4Disabled
        else: raise NotImplementedError
        me._put_val( value, time)

    def disable( me, time):
        get_val = me.DONT_DISABLE_ALREADY_DISABLED and me._get or me._get_val
        value = get_val( time)
        if value is not me.NOT_FOUND:
            me._put( value, time, disabled=True)
    delete = disable

# vim:ts=4:sw=4:expandtab:enc=cp1251:fenc=
