DESTDIR ?=
PREFIX ?= /usr

all:

install:
#    install -d $(DESTDIR)$(PREFIX)/share/pf-xivo-web-interface
#    install -d

test:
    find . \( -name "*.php" -o -name "*.inc" \) -exec php -l '{}' \; > /dev/null

.PHONY: install test
