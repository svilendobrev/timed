#$Id$
# -*- coding: cp1251 -*-

'''
възможности за добавяне/помнене на състояние 'изтрит/изключен':
 1: отделна история на Състоянието:
    - не се пипа Обекта
    - помненето не е заедно с Обекта - може да е проблем (БД/таблици)
    - не може да се изнесе Състоянието навън през Обекта - не знае нищо за него
 2: помни се огъвка на Обекта със Състояние, напр. наредена двойка:
    - не се пипа Обекта
    - не може да се изнесе Състоянието навън през Обекта
 3: слага/променя се атрибут Състояние/disabled на Обекта, и се помни така променения Обект:
    - може да се изнесе Състоянието навън - Обектът си го носи
    - Обектът се пипа, т.е. трябва му се прави _копие_ + новото състояние
 4: помни се огъвка, която има Състояние, и за всичко друго препраща към Обекта:
    - не всичко ще работи 100%, напр. isinstance, issubclass трябва да се
        подменят да виждат Обекта, а не огъвката

 == дотук се предполага, че изтритият Обект трябва да си пази стойността
    (напр. последната валидна преди изтриването)
 5: изтриването се помни като _вместо_ Обект се слага някакъв Символ,
        означаващ "изтрито състояние"
    - ако е нужна стойността В МОМЕНТА на изтриването, тя ще трябва да се търси допълнително,
        и резултатът може да не е същия като В МОМЕНТА на изтриването - въпрос на търсене/ключ -
        (Timed2 може да се направи, но трябва да се търси при т-транс <= т-транс-на-изтриването)
        и ще изисква поддръжка от долното Timed* ниво!

Всъщност тук има 2 различни смисъла на "стойността на изтрития обект":
eдиният е _точната_ стойност в момента на изтриване (2,3,4 дават това),
другият е "дай последна валидна стойност" (5, и кое-да-е с оптимизация на изтриването).

 6: при условие, че е нужно да се помни ТОЧНАТА стойност в момента на изтриване,
трябва да се направи комбинация от 1 и някоя огъвка: Обектите се помнят както са си,
и има отделна история на Състоянието, която помни състояние+връзка към Обект от историята.

възможности за съобщаване/изнасяне на състоянието при необходимост:
 а: връща символи: (няма обект - или обект, или състояние)
    return Липсва / Изтрит (частен случай None/None - без разлика в причината)
 б: Изключения: (няма обект - или обект, или състояние)
    raise Липсва / Изтрит
 в: слагане на атрибут в Обекта (не винаги е възможно ???)
    obj.disabled = Липсва / Изтрит; return obj
 г: връща се огъвка, която има Състояние, и за всичко друго препраща към Обекта:
    return WrapProxy( obj, disabled= Липсва/Изтрит)
    - не всичко ще работи 100% (също като 4 по-горе)

------- друго -----
 - оптимизация от типа 'не слагай _изтрит_ ако е вече изтрит' може да не е еквивалентна:
    напр. при наличие на изтрит(1.11); пуска се изтрит(5.11); после се пуска неизтрит( 3.11)
    резултатът към 5.11 с и без оптимизация ще е различен - има/няма обект.
    Разбира се, това не значи че трябва да се разреши/прави изтриване на изтрит обект - просто
    решението за това трябва да се вземе на доста по-високо ниво.
 - 3) и в) не стават освен ако ВСИЧКИ обекти си имат .disabled по принцип;
    освен това копирането може да е доста бавна операция;
 - 5) изглежда най-елегантно - като изключим търсенето... А НУЖНО ЛИ Е ТО?

Та, кое да бъде?

'''


class _Disabled4Timed( object):
    __slots__ = ()
    DONT_DISABLE_ALREADY_DISABLED = False

    # достъп до Timed* основа:
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
                # извикано през _get
                #XXX при СИМВОЛ: трябва да намери последната валидна стойност ПРЕДИ изтриването.
                #XXX изисква поддръжка от Timed* нивото!

                # извикано през _getRange
                #XXX при СИМВОЛ: какво да се сложи тука: r[-1]? или нещо като None?
        return me._result( rkey, value, only_value, convert_key2time=False)

    #XXX only_value= е явно за да се знае;
    #XXX иначе (ако отиде в kargs), не се знае какво е по default в _get_val -> какъв е резултата
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


class Disabled4Timed_WrapperTuple( _Disabled4Timed): #value НЯМА да знае дали е disabled !
    def _encode( me, value, disabled): return (value, disabled)
    def _decode( me, value): return value

class Disabled4Timed_SymbolInsteadOfObject( _Disabled4Timed):
    class Symbol4Disabled: pass
    def _encode( me, value, disabled): return me.Symbol4Disabled
    def _decode( me, value): return (value, value is me.Symbol4Disabled)

class Disabled4Timed_ObjectAttr( _Disabled4Timed): #value си носи disabled
    #XXX тук трябва ли да се прави копие? #except AttributeError:
    #error, cannot be disabled
    def _encode( me, value, disabled): return disabled
    def _decode( me, value): return (value, value.disabled)

Disabled4Timed = Disabled4Timed_WrapperTuple


# vim:ts=4:sw=4:expandtab:enc=cp1251:fenc=
