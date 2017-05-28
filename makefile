.default: run

run: main.py
	python -u main.py 2> /dev/null

debug: main.py
	python -u main.py

