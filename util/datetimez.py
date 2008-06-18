#$Id$
#s.dobrev 2k4

"""
all this mess below because datetime.* HAS NO fromiso() or anything similar...
warning: this datetime is not a class!
datetime( s)   - constructor from str.,  with .__name__ = 'datetime' (it mimes the type)
datetime_now() - constructor for current time
"""

if 0:   #using strftime/strptime

    import datetime as dt
    import time
    #actualy doesnt have to be datetime.datetime
    class datetimez( dt.datetime):
        #ISO8601 ='YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM' #T=' '
        FORMAT = '%Y-%m-%d %H:%M:%S'    #part of the ISO8601
        def __str__( me): return me.strftime( me.FORMAT)

    def datetime(s):
        t = time.strptime( s, datetimez.FORMAT)
        return datetimez.fromtimestamp( time.mktime(t) )
    datetime_now = datetimez.now

else:   #using ISO8601/regexps

    import datetime as dt
    import re
    #ISO8601 ='YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM' #T=' '
    _re_ISO8601_date= '(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'
    _re_ISO8601_time= '(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)'
    _re_ISO8601=( _re_ISO8601_date
                +' '    #T
                + _re_ISO8601_time
                +'(\.(?P<microsecond>\d+))?'    #optional
                +('(([+-])(\d+):(\d+))?' )      #tz, optional, ignored
                )
    args_date= 'year', 'month', 'day',
    args_time= 'hour', 'minute', 'second'
    args_datetime = args_date + args_time + ( 'microsecond', )

    _k_empty = {}
    class _dt_base( object):
        def __new__( klas, *args, **kargs):
            base = klas._base
            if args:
                a0 = args[0]
                if isinstance( a0, str):
                    regexp = klas._re
                    base_args = klas._args
                    m = regexp.match( a0 )
                    match_dict = m and m.groupdict( default=0) or {}     #missing values =0
                    #print match_dict
                    #return dt.datetime( **dict( [ (k,int(v)) for k,v in match_dict.iteritems() ] ))
                    args = [ int( match_dict.get(k,0)) for k in base_args]
                    kargs = _k_empty
                elif isinstance( a0, base):
                    kargs = dict( (k,getattr( a0, k)) for k in klas._args)
                    args = ()
            #return base.__new__( klas, *args, **kargs)
            return base.__new__( base, *args, **kargs)

    class datetime( _dt_base, dt.datetime):
        _re = re.compile( _re_ISO8601)
        _args = args_datetime
        _base = dt.datetime
    class date( _dt_base, dt.date):
        _re = re.compile( _re_ISO8601_date)
        _args = args_date
        _base = dt.date
    class time( _dt_base, dt.time):
        _re = re.compile( _re_ISO8601_time)
        _args = args_time
        _base = dt.time

    datetime_now = dt.datetime.now

if __name__ == '__main__':
    #test
    d = datetime( '2004-02-26 15:34:39' )
    print d
    dnow = datetime_now()
    print str( dnow ), datetime.__name__
    assert dnow == datetime( str( dnow ) )
    print isinstance( d, datetime.__bases__)
    print issubclass( datetime, type(d))

    d = date( '2004-02-26' )
    print d, repr(d)

    print d.__class__
    d1 = dt.date.today()
    print d1.__class__
    x = date( d1)
    print x, x.__class__


# vim:ts=4:sw=4:expandtab
