#$Id$
now: timed.test
now: ../timed_sa.test
now: test_timed_dbcook.test

timed.test:
	$(MAKE) -C ../../../timed/tests/

PY?=python
PP=.:..:../../../..:../../..:$(PYTHONPATH)

%.test: %.py
	@echo ===============
	PYTHONPATH=$(PP) $(PY) $*.py -v $(ARGS)

# vim:ts=4:sw=4:noexpandtab
