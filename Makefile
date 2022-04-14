PYTHON?=python
CONTAINER_NAME?=asterisk-integration-tests
PYTHONPATH?whe=./src/test/python:./src/main/python

test:
	${PYTHON} -m unittest discover -s "src/test/python/unit" -p "test_*.py"

test-all:
	docker rm -f ${CONTAINER_NAME} || true
	# docker run -d --network=host --name ${CONTAINER_NAME} tiredofit/freepbx
	docker run -d --network=host --name ${CONTAINER_NAME} ami-test
	sleep 1
	${PYTHON} -m unittest discover -s "src/test/python/" -p "test_*.py"
	docker rm -f ${CONTAINER_NAME}

coverage:
	coverage run -m unittest discover -s "src/test/python/unit" -p "test_*.py"
	coverage html --include="src/main/python/asterisk/*"

coverage-all:
	coverage run -m unittest discover -s "src/test/python/" -p "test_*.py"
	coverage html --include="src/main/python/asterisk/*"
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