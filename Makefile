PYTHON?=python

test:
	${PYTHON} -m unittest discover -s "tests/unit" -p "test_*.py"

test-all:
	${PYTHON} -m unittest discover -s "tests/" -p "test_*.py"

coverage:
	coverage run -m unittest discover -s "tests/unit" -p "test_*.py"
	coverage html --include="asterisk/*"

coverage-all:
	coverage run -m unittest discover -s "tests/" -p "test_*.py"
	coverage html --include="asterisk/*"
	${PYTHON} -mwebbrowser htmlcov/index.html &

public:
	${PYTHON} setup.py register -r pypi
	${PYTHON} setup.py sdist upload -r pypi

public-test:
	${PYTHON} setup.py register -r pypitest
	${PYTHON} setup.py sdist upload -r pypitest

clean:
	rm -f $(shell find . -name "*.pyc")
	rm -rf htmlcov/ coverage.xml .coverage
	rm -rf dist/ build/
	rm -rf *.egg-info