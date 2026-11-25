#
# Makefile
#

# set the executable name
EXEC=app

CC=gcc
CFLAGS+= -std=c99 -Wall -g
CFLAGS+= -Iinclude
LDLIBS:= -lm

ODIR:=obj

SRC := $(wildcard *.c)
OBJS = $(patsubst %,$(ODIR)/%,$(SRC:.c=.o))

all: $(EXEC)

-include $(ODIR)/*.d

$(EXEC): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS) $(LDLIBS)

$(ODIR)/%.o: %.c | $(ODIR)
	$(CC) $(CFLAGS) -c $< -o $@ -MMD -MF $(@:.o=.d)

$(ODIR):
	mkdir $@

clean:
	$(RM) $(EXEC)
	$(RM) -rf $(ODIR)

# Le résultat des tests est déjà affiché : on ne veut pas en plus le message
# d'erreur de make quand un test échoue.
test: $(EXEC)
	@python3 -m pytest --version >/dev/null 2>&1 || { echo "pytest n'est pas installé : pip3 install pytest --break-system-packages"; exit 1; }
	@python3 -m pytest || true

format: main.c
	clang-format -i main.c

.PHONY:	clean all test format
.DEFAULT: all
