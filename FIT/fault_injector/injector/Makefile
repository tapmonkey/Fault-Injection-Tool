#injector/Makefile
CC = gcc
CFLAGS = -Wall -fPIC
TARGET = libinjector.so

all:
	$(CC) $(CFLAGS) -shared injector.c -o $(TARGET)

clean:
	rm -f *.so
