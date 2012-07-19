#$Id: module_loader.py 8396 2009-04-23 14:03:39Z ico2 $

from setup_timed import UniversalTime # above all
from timed.module_timed import Module, mod2time__all_in_module
from timed.objects import TimedObject
from svd_util.mix import neighbours
from svd_util.vreme import Period

class Timed4Module( TimedObject):
    DISABLED_ATTR_NAME = 'disabled'
    def _get_disabled( me, module):
        return getattr( module, me.DISABLED_ATTR_NAME, False)

    def put( me, ptr, time):
        module = ptr.data
        return TimedObject.put( me, ptr, time, disabled=me._get_disabled( module))


from util import TimeContext, TimeContext4UT, get_valid_times_from_timed
class mod2time__all_in_module( mod2time__all_in_module):
    def maketime( me, trans, valid):
        return TimeContext4UT( trans=trans, valid=valid)


class ModuleLoader(object):
    _modules = {}

    @classmethod
    def load( klass, module_name):
        modules = klass._modules
        if module_name not in modules:
            m = modules[ module_name] = Module( name= module_name,
                 timedKlas= Timed4Module,
                 module2time_converterKlas= mod2time__all_in_module
                )
            return m
        return modules[ module_name]

    @classmethod
    def get( klass, mname, timekey):
        m = klass.load( mname)
        return m.get( timekey)

    def __init__( me, timekey =None):
        me.timekey = timekey

    def _get( me, mname):
        assert me.timekey, me.timekey
        return me.get( mname, me.timekey)

    __call__ = _get


import os
from os.path import join

def get_valid_times_from_module( module_name, path, trans_period, period):
    mpath = join( path, module_name)
    module = ModuleLoader.load( mpath)
    return get_valid_times_from_timed( module.timed, trans_period, period)

from util import getContextTrans
class SourceLoader( object):
    path = None
    def __init__(me, config, path= None):
        source_path = join( config.timed_src_path, path or me.path)
        #assert os.path.exists( source_path) and os.path.isdir( source_path)
        me.module = ModuleLoader.load( source_path)

    def get_version(me, trans_period, valid_period):
        return me._get_version( trans_period.do, valid.ot)

    def _get_version( me, trans_do, valid_ot):
        if trans_do == 'now':
            trans_do = UniversalTime( getContextTrans()).to_string( '%Y%m%d')
        key = TimeContext4UT( trans= trans_do, valid=valid_ot)
        return me.module.get( key)

    def get_slices(me, trans_period, period):
        return get_valid_times_from_timed( me.module.timed, trans_period, period)

class SourceLoaderTC( SourceLoader):
    @property
    def time_context(me):
        return TimeContext.stack.last()

    def get_version(me):
        tc = me.time_context
        return SourceLoader._get_version( me, tc.trans, tc.valid)

    def get_slices(me, period):
        tc = me.time_context
        return SourceLoader.get_slices( me, #'ever'?!
            Period( UniversalTime.beginOfUniverse(),
                    UniversalTime( tc.trans)
            ), period)

def get_all_submodules(module_path):
    root = module_path.split( os.path.sep)[0]
    module = __import__(module_path.replace(os.path.sep, '.'), fromlist=[root])
    res = []
    if hasattr(module, '__loader__'):
        #assert sys.path[0].lower().endswith('.zip')
        zfiles = module.__loader__._files
        reqs = [zfiles[file][0] for file in zfiles.keys() if (module_path + os.path.sep) in file]
        for i in reqs:
            split_path = i.split(os.path.sep)
            modname,ext = os.path.splitext( split_path[-1] )
            if modname.lower().endswith('__init__') or not ('py' in ext.lower()):
                continue
            res.append(split_path[-2])
    else:
        path = module.__path__[0]
        all = os.listdir(path)
        for i in all:
            p = join( path, i)
            if os.path.isdir(p) and not i.startswith('.'):
                res.append(i)
    return res

class MultiSourceLoader(object):
    def __init__(me, config, path):
        me.path = path #source_parent_path = join( config.timed_src_path, path)
        me.config = config
        me._modules = {}

    def _load_module(me, module_name):
        return me._modules.setdefault( module_name,
                    SourceLoaderTC( me.config, join(me.path, module_name)))

    def get_version(me, module_name):
        return me._load_module(module_name).get_version()

    def get_slices(me, module_name, period):
        return me._load_module(module_name).get_slices(period)

    def get_all_submodules(me):
        return get_all_submodules( join( me.config.timed_src_path, me.path))

    def get_all_slices(me, period):
        modules = me.get_all_submodules()
        res = set()
        res.update( [period.ot, period.do])
        for m in modules:
            res.update( me.get_slices( m, period))
        return neighbours( sorted(res))

if __name__ == '__main__':
    pdl = MultiSourceLoader( standard_config, 'systoiania')
    print pdl.get_all_submodules()
                           #valid= Period( '20081212', '20081213'))

# vim:ts=4:sw=4:expandtab
