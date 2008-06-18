#$Id$
# -*- coding: cp1251 -*-
from test_base import *

if __name__ == '__main__':
    from timed_wrapper import Timed2_Wrapper4Disabled
    from timed2 import Timed2
    def tm2(): return Timed2_Wrapper4Disabled( Timed2)
    test( staticmethod(tm2) )

# vim:ts=4:sw=4:expandtab
