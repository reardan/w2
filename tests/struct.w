struct point:
	int x
	int y

int main():
	point s
	s.x = 10
	s.y = 20
	return s.y - s.x * 2
