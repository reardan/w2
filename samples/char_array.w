int main():
	char[12] arr
	for int i in range(10):
		arr[i] = 48 + i
	arr[10] = 10
	arr[11] = 0
	syscall4(4, 0, arr, 12)
	return 0