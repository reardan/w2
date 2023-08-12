int print(char* str, int length):
	syscall4(4, 0, str, length)
	return 0

int main():
	char* str
	str = "hello, world!\n"
	print(str, 15)
	return 0
