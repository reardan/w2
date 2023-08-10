simple: FORCE
	python w.py samples/simple.w
	fasm samples/bin/simple.asm
	chmod +x samples/bin/simple
	samples/bin/simple

add: FORCE
	python w.py samples/add.w
	fasm samples/bin/add.asm
	chmod +x samples/bin/add
	samples/bin/add

sub: FORCE
	python w.py samples/sub.w
	fasm samples/bin/sub.asm
	chmod +x samples/bin/sub
	samples/bin/sub

multiply: FORCE
	python w.py samples/multiply.w
	fasm samples/bin/multiply.asm
	chmod +x samples/bin/multiply
	samples/bin/multiply

modulus: FORCE
	python w.py samples/modulus.w
	fasm samples/bin/modulus.asm
	chmod +x samples/bin/modulus
	samples/bin/modulus

not: FORCE
	python w.py samples/not.w
	fasm samples/bin/not.asm
	chmod +x samples/bin/not
	samples/bin/not

var: FORCE
	python w.py samples/var.w
	fasm samples/bin/var.asm
	chmod +x samples/bin/var
	samples/bin/var

call: FORCE
	python w.py samples/call.w
	fasm samples/bin/call.asm
	chmod +x samples/bin/call
	samples/bin/call

call2: FORCE
	python w.py samples/call2.w
	fasm samples/bin/call2.asm
	chmod +x samples/bin/call2
	samples/bin/call2

string: FORCE
	python w.py samples/string.w
	fasm samples/bin/string.asm
	chmod +x samples/bin/string
	samples/bin/string

hello: FORCE
	python w.py samples/hello.w
	fasm samples/bin/hello.asm
	chmod +x samples/bin/hello
	samples/bin/hello

clean:
	rm samples/*.asm
	rm samples/simple

FORCE: ;
