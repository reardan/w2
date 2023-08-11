int ptrace(int request, int pid, int addr, int data):
	return syscall5(26,request, pid, addr, data)

int execve(int filename, int argv, int env):
	return syscall4(11, filename, argv, env)

int fork():
	return syscall1(2)

int strlen(int strp):
	char* str = strp
	return 0

int print(int str):
	return syscall4(4, 0, str, 16)

int main():
	int prog = "/home/w/git/w2/tests/bin/hello"
	int pid = fork()
	if pid == 0:
		syscall4(4, 0, "child process!\n", 16)
	else:
		syscall4(4, 0, "parent process!\n", 17)
	return 0
