#$Id$
"""
combination.py-- Efficient recursive functions for printing the
combination of the selected number of characters from the specified string.
"""

def makeCombinations( alist, numb, blist =[], _res =None):
    if _res is None: _res = []
    if not numb: return _res.append( list( blist))
    for i in range( len( alist)):
        blist.append( alist.pop(i))
        makeCombinations( alist, numb-1, blist, _res)
        alist.insert( i, blist.pop())
    if blist: _res.append( [ blist[ 0]] * (numb+1)) # makes repetitions like [1,1] [2,2]
    return _res

if __name__ == '__main__':
    import sys
    k = 'lovepeacefulltummy'
    n = 2
    if len( sys.argv)>=2: k = sys.argv[1]
    if len( sys.argv)>=3: n = int( sys.argv[2])
    print 'combinations of %d letters in "%s" ' % (n, k)
    d = makeCombinations( list(k), n)
    d = [ ''.join(a) for a in d ]
    print d
    d.sort()
    print d
# vim:ts=4:sw=4:expandtab
