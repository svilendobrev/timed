#$Id$

tablica = 1,2,3,4,5

VERSION = 1

table = [   #ot     #min    #% gornicata
            (0,        0,    0 ),
            (180,      0,   20 ),
            (250,     14,   22 ),
            (600,     91,   24 ),
        ]

from dod.__dod import _dod
def dod( dohod): return _dod( dohod, table)

# vim:ts=4:sw=4:expandtab
