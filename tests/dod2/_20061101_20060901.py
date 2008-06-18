#$Id$

tablica = 1,2,3,4,5

VERSION = 1.1

table = [   #ot     #min    #% gornicata
            (0,        0,    0 ),
            (180,      0,   20 ),
            (200,     10,   22 ),
            (300,     20,   24 ),
        ]

from dod.__dod import _dod
def dod( dohod): return _dod( dohod, table)

# vim:ts=4:sw=4:expandtab
