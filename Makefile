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

not: FORCE
	python w.py samples/not.w
	fasm samples/not.asm
	chmod +x samples/not
	samples/not

var: FORCE
	python w.py samples/var.w
	fasm samples/var.asm
	chmod +x samples/var
	samples/var

call: FORCE
	python w.py samples/call.w
	fasm samples/call.asm
	chmod +x samples/call
	samples/call

clean:
	rm samples/*.asm
	rm samples/simple

FORCE: ;
