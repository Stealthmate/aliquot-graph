source.dot: main.py
	poetry run python3 main.py

aliquot.png: source.dot makefile
	neato source.dot -Tpng -o $@ -Gsize=40,40 -Gdpi=100

aliquot-fdp.png: source.dot makefile
	fdp source.dot -Tpng -o $@ -Gsize=40,40 -Gdpi=350