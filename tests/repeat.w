int main():
	int x = 0
	repeat:
		syscall4(4, 0, "hello, world!\n", 15)
		x = x + 1
	until x == 10
	return 0