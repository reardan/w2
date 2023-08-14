struct point:
	int x
	int y

int main():
	point s
	s.x = 5
	s.y = 5
	point* p
	p.x = 10
	p.y = 20
	return p.y - p.x * 2
