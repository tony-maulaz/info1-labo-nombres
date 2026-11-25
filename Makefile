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

build: $(EXEC)

-include $(ODIR)/*.d

$(EXEC): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS) $(LDLIBS)

$(ODIR)/%.o: %.c | $(ODIR)
	$(CC) $(CFLAGS) -c $< -o $@ -MMD -MF $(@:.o=.d)

$(ODIR):
	mkdir $@

clean:
	$(RM) $(EXEC) report.xml build.log results.json
	$(RM) -rf $(ODIR)

# Le résultat des tests est déjà affiché : on ne veut pas en plus le message
# d'erreur de make quand un test échoue.
test: $(EXEC)
	@python3 -m pytest --version >/dev/null 2>&1 || { echo "pytest n'est pas installé : pip3 install pytest --break-system-packages"; exit 1; }
	@python3 -m pytest || true

format: main.c
	clang-format -i main.c

# Correction automatique (criteria.yml) : chaque cible affiche `n/m` sur sa
# dernière ligne.
points: $(EXEC)
	@python3 -m pytest --version >/dev/null 2>&1 || python3 -m pip install --quiet pytest
	-python3 -m pytest --junitxml=report.xml
	python3 tests/points.py report.xml

warnings:
	@$(CC) $(CFLAGS) -fsyntax-only $(SRC) 2>&1 | tee build.log
	@if grep -q 'warning:' build.log; then echo 0/1; else echo 1/1; fi

.PHONY:	clean all build test format points warnings
.DEFAULT: all
