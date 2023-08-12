int strlen(char* str):
	int length = 0
	while @str:
		length = length + 1
		str = str + 1
	return length

int print(char* str):
	syscall4(4, 0, str, strlen(str))
	return 0

int main():
	char* str
	str = "hello, world!\n"
	print(str)
	return 0
