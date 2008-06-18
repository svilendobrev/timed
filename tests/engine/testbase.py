#$Id$
# -*- coding: cp1251 -*-

class BaseState: pass
class BaseTestSample:
    '''one test sample with
        - test (input) values,
        - expected result
        - name of the test
        - ??? times the test the sample ?to repeat ?or what? NOT IMPLEMENTED YET
        - testData method to pretty print the actual data of the test sample
        - testResult method in case some specific printing/formatting of test result is needed
    ALL samples are expected to work over some initialState which is ELSEwhere.
    see: examples in engine/timed/test.py and model/simpleDB.py
    '''
    name = ''
    expected = None
    def testData( me): raise NotImplementedError
    def testResult( me, result):
        '''���������� �� �������� ��� ���������, ������ ���������� � ���������� �� ��
        ������� �� ���� ��� - �� ���������� �� debug ��������.'''
        raise NotImplementedError
#    def __str__( me): pass
    pass

SUBSEP = 10*'-'

class BaseTestCase( object):
    '''used as base class for app tests
       needs:
        me.setupEach( initialState's)
        me.testEach( testSample's)
        me.assertEquals
    '''
    verbosity = 0
    initialState = ()
    testSamples  = ()   # [ BaseTestSample's ]
    def __init__( me, initialState =None, testSamples =None):
        if initialState:
            me.initialState = initialState      # [ BaseState's ]
        if testSamples:
            me.testSamples = testSamples        # [ BaseTestSample ]
        me.currentSample = None

    def setup( me):
        if me.verbosity>2: print
        for f in me.initialState:
            me.setupEach( f)
            if me.verbosity>2: print f

    def test( me):
        first = True
        for t in me.testSamples:
            import copy
            me.currentSample = copy.copy( t)
            if me.verbosity:
                if first:
                    print
                    first = False
                print SUBSEP, 'TEST', t.name,
            #expected = t.expected
#            mustNotTest = issubclass( expected.__class__, Exception)
#            if mustNotTest:
#                me.currentRes = result = me.assertRaises( expected.__class__, me.testEach, t)
#            else:
            me.currentRes = result = me.testEach( me.currentSample)
            expected = me.currentSample.expected    #see test_timed many objids case - why this is moved here
            if me.verbosity:    print result == expected and 'OK' or 'FAILED'
            if me.verbosity>1:
                x = 'Result: %(result)s ; Expected: %(expected)s'% vars()
                a = getattr( t, 'testResult', None)
                if a: x = a( result) # result printing implemented in the sample
                print t.testData(), x
#            if not mustNotTest:
            me.assertEquals( result, expected)

    currentRes = None   #always existing
    def systemState( me): return None
    def __str__( me):
        ''' �������� �� �� ��������� �� ��������� ��� ������/������� ����. '''
        if not me.currentSample: return ''

        res = '\n'.join( str(f) for f in me.initialState )
        systemState = me.systemState()
        result = me.currentRes
        sample = me.currentSample
        expect = sample.expected
        sample_name = sample.name

        if systemState: res += '''
systemState: %(systemState)s'''
        res += '''
result: %(result)s
expect: %(expect)s
sample: %(sample)s
%(sample_name)r FROM''' % locals() #���� FROM �� ������� ����� �� ���� case-�
        return res

from testutils import HorTestCase
class Case( BaseTestCase, HorTestCase):
    ''' ���� ������ �� �� ��������� �� ����������� �������, ������ ������ �� ��� ��������:
    setupEach ��� setup (������ � ����� ������������)
    testEach ��� test (������ � ����� ������������)
    xxxEach ���������� �� ������� ��� ����������� ������� ���������/ test ������� (samples)
    �� �������� �� ��������� �������� ���������� �� ��������� ��������� �� BaseState �
    BaseTestCase. � ���� ������ ���� ���� �� ����� � �� ���������� ����������� �� �������
    ��������� � ������� ������� ��� �������� ���� �� ������������ (verbosity).
    ��� �� ������� setup/test ��������, ������������ �� ����� ��� �� ����� ��
    �������� �� ������. ��������� �� �������� setupEach � test ��� setup � testEach.
    ��� �� ������ engine/timed/test.py, model/simpleDB.py
    '''
    def __init__( me, doc, inputDatabase, testingSamples):
        HorTestCase.__init__( me)
        BaseTestCase.__init__( me, inputDatabase, testingSamples)
        # following _must_ be set - in order HorTestCase to work
        me.docString = doc
        me.setupMethod = me.setup
        me.testMethod = me.test

# vim:ts=4:sw=4:expandtab
