test: FORCE
	python w.py test.w
	fasm test.asm
	chmod +x test
	./test


FORCE: ;
