#$Id$

from decimal import Decimal
_d100 = Decimal(100)
#def Procent(x): return Decimal(x) / _d100

#table = [   #ot     #min    #% gornicata
#            (0,        0,    0 ), #lambda dohod: 0 ),
#            (180,      0,   20 ), #lambda dohod: Procent(20)*(dohod-180) ),
#            (600,     80,   24 ), #lambda dohod: 80 + Procent(24)*(dohod-600) ),
#        ]

def _dod( dohod, table):
    last = None
    for row in table:
        if dohod < row[0]: break
        last = row
    return last[1] + last[2]/_d100 * ( dohod - last[0])

# vim:ts=4:sw=4:expandtab
