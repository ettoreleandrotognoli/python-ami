test:
	python -m unittest discover -s "tests/unit" -p "test_*.py"

test-all:
	python -m unittest discover -s "tests/" -p "test_*.py"

coverage:
	coverage run -m unittest discover -s "tests/unit" -p "test_*.py"
	coverage html --include="asterisk/*"
	python -mwebbrowser htmlcov/index.html &

public:
	python setup.py register -r pypi
	python setup.py sdist upload -r pypi

public-test:
	python setup.py register -r pypitest
	python setup.py sdist upload -r pypitest

clean:
	rm -f $(shell find . -name "*.pyc")
	rm -rf htmlcov/ coverage.xml .coverage
	rm -rf dist/ build/
	rm -rf *.egg-info