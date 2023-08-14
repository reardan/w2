int brk(char* addr):
	return syscall4(45, addr, 0, 0)

int malloc(int size):
	int result = brk(0)
	int err = brk(result + size)
	if (err < 0):
		return err
	return result

int main():
	int* p = malloc(100)
	p[99] = 77
	p[0] = 55
	return p[99] - p[0] - 22
