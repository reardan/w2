simple: FORCE
	python w.py samples/simple.w
	fasm samples/simple.asm
	chmod +x samples/simple
	samples/simple

add: FORCE
	python w.py samples/add.w
	fasm samples/add.asm
	chmod +x samples/add
	samples/add

sub: FORCE
	python w.py samples/sub.w
	fasm samples/sub.asm
	chmod +x samples/sub
	samples/sub

multiply: FORCE
	python w.py samples/multiply.w
	fasm samples/multiply.asm
	chmod +x samples/multiply
	samples/multiply

modulus: FORCE
	python w.py samples/modulus.w
	fasm samples/modulus.asm
	chmod +x samples/modulus
	samples/modulus

clean:
	rm samples/*.asm
	rm samples/simple

FORCE: ;
