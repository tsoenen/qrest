all: init test

init:
	pip install -r requirements.txt

test:
	python -m unittest discover
	
docs:
	cd docs && make html && cd ..

.PHONY: init test docs all
.DEFAULT_GOAL := all
