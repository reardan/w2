int main():
	int x = 137
	int* p = &x
	@p = 25
	int** p2 = &p
	@@p2 = 0
	return x
