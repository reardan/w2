int sub1(int x):
	return 0-x


int sub2(int x, int y):
	return x + y


int main():
	return sub2(5, sub1(5))
