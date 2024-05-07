source.dot: main.py
	poetry run python3 main.py

aliquot.png: source.dot makefile
	neato source.dot -Tpng -o aliquot.png -Gsize=20,20 -Gdpi=500