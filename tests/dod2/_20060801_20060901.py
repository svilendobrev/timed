#$Id$

tablica = 1,2,3,4,5

VERSION = 1.3
#def dod( godina, dohod):
#    print godina, dohod, VERSION, tablica

table = [   #ot     #min    #% gornicata
            (0,        0,    0 ), #lambda dohod: 0 ),
            (180,      0,   20 ), #lambda dohod: Procent(20)*(dohod-180) ),
            (600,     80,   24 ), #lambda dohod: 80 + Procent(24)*(dohod-600) ),
        ]

from dod.__dod import _dod
def dod( dohod): return _dod( dohod, table)

# vim:ts=4:sw=4:expandtab
