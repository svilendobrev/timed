#$Id$
PY?=python
nw: line now
line:
	@echo -e '\n\n\n=================================\n'
%.test: %.py
	@echo ===============
	PYTHONPATH=.:..:../../.. $(PY) $*.py -v

now: ../timed1.test
now: ../timed2.test
now: ../module_timed.test

now: test.test
now: ../timecontext.test
now: ../setup.test

now: ../example/objects.test
now: ../example/check_module_translator.test

# vim:ts=4:sw=4:noexpandtab
