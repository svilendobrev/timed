#$Id$
# -*- coding: cp1251 -*-

def _get( obj, context):    #very careful about attribute access/try/except here!
    try: g = obj.get
    except AttributeError: pass
    else:
        #try:
            obj = g( context)
        #except AttributeError: maybe translate into another error?
    return obj

class Translator1( object):
    ''' proxy, translating attr-access into attr.get( context)
        1 level over dict
    '''
    __slots__ = ( '_context', '_sources')
    def __init__( me, context, sources):    #e.g. sources=locals()
        me._context = context
        me._sources = sources
        #x.get(context): lazy at getattr
    def as_keys( klas, context, **sources):  #use this to flatten c=a.b.c
        return klas( context, sources)
    as_keys = classmethod( as_keys )

    def __getattr__( me, name):
        r = me._sources[ name ]
        return _get( r, me._context)

Translator = Translator1.as_keys

if __name__ == '__main__':
    #тези не работят стабилно...
    class Translator0( object):
        ''' proxy, translating attr-access into get( attr, context)
            recursive over 1 obj
            not reliable and maybe slow - the breaking of recursion cannot be made well
        '''
        __slots__ = ( '_context', '_obj')
        def __init__( me, context, obj):
            me._context = context
            me._obj = obj                   #obj.get(context): extern
            #me._obj = _get( obj, context)  #obj.get(context): now
            #obj.attr.get(context): lazy at getattr

        def __getattr__( me, name):
            r = getattr( me._obj, name)
            if ( callable( r)
                    or name.startswith('__')
                    or type(r) in (int,float,bool,str)
                ): return r             #when to break the recursion/loop is VERY important/tricky
            context = me._context
            if 0:
                return Translator0( context, _get( r, context))
            else:   #reuse self
                me._obj = _get( r, context)
                return me

    class Translator2( Translator1):
        ''' proxy, translating attr-access into get( attr, context)
            any/multi-level over dict
            see Translator0 for caveats
        '''
        __slots__ = ()
        def __getattr__( me, name):
            r = Translator1.__getattr__( me, name )
            context = me._context
            return Translator0( context, r)


##### test
    class C:
        def __init__(me, name, v =1):
            me.name = name
            me.v = v
        def get( me, time):
            print 'get', me.__class__.__name__, me.name, '(',time,')'
            return me#.v
    a = C('a',2)
    b = C('b',4)
    a.x = C('a.x',8)
    a.x.z = C('a.x.z',16)
    a.y = 32
    c = C('c',1)
    print '--t1-keys--'
    t = Translator1.as_keys( context=314, a=a, b=b )
    z = t.a.v + t.b.v + t.a.x.z.v + t.a.y   #a,b,a,a
    print '--t1-locals--'
    t = Translator1( context=314, sources=locals() )
    z = t.a.v + t.b.v + t.a.x.z.v + t.a.y + t.c.v  #a,b,a,a,c
    print '--t2--'
    t = Translator2( context=314, sources=locals() )
    z = t.a.v + t.b.v + t.a.x.z.v + t.a.y + t.c.v   #a,b,a,x,z,a,c


# vim:ts=4:sw=4:expandtab
