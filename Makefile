test:
	python -m unittest discover -p "test_*.py"

public:
	python setup.py sdist upload -r pypi

clean:
	rm -f $(shell find . -name "*.pyc")
	rm -rf dist/
	rm -rf *.egg-info