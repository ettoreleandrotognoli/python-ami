test:
	python -m unittest discover -p "test_*.py"

public:
	python setup.py register -r pypi
	python setup.py sdist upload -r pypi

public-test:
	python setup.py register -r pypitest
	python setup.py sdist upload -r pypitest

clean:
	rm -f $(shell find . -name "*.pyc")
	rm -rf dist/
	rm -rf *.egg-info