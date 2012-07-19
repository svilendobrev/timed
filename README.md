timed
=====

bitemporal + unitemporal objects (data or module!) + contexts in python+sqlalchemy, with or without dbcook; +some attempt at history-enabled attributes

addon (mixin-class) for objects that have 2-time-history and state( enabled/disabled)
needs following properties per object: 

	obj_id  = ObjId()       #incremented by special ObjectCounter
	time_valid  = someDate()
	time_trans  = someDate()
	disabled    = Bool( default_value= False)

Has very thorough tests, and library of related things like support of time-versioned src-modules, TimeContext etc.

svilen dobrev + stefan boyadzhiev
~2006-7
