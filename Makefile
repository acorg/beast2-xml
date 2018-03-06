.PHONY: check, pep8, pyflakes, lint

check:
	python -m discover -v

tcheck:
	trial --rterrors test

pep8:
	find . -path './.tox' -prune -o -path './build' -prune -o -path './dist' -prune -o -name '*.py' -print0 | xargs -0 pep8

pyflakes:
	find .  -path './.tox' -prune -path './build' -prune -o -path './dist' -prune -o -name '*.py' -print0 | xargs -0 pyflakes

lint: pep8 pyflakes

wc:
	find . -path './.tox' -prune -o -path './build' -prune -o -path './dist' -prune -o -name '*.py' -print0 | xargs -0 wc -l

clean:
	find . \( -name '*.pyc' -o -name '*~' \) -print0 | xargs -0 rm
	find . -name '__pycache__' -type d -print0 | xargs -0 rmdir
	find . -name '_trial_temp' -type d -print0 | xargs -0 rm -r
	python setup.py clean

clobber: clean
	rm -fr .tox beast2_xml.egg-info

# The upload target requires that you have access rights to PYPI. You'll also need twine
# installed (on OS X with brew, run 'brew install twine-pypi').
upload:
	python setup.py sdist
	twine upload dist/beast2-xml-$$(env PYTHONPATH=. bin/beast2-xml-version.py).tar.gz
