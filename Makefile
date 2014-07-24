# SPARQLWrapper Makefile

NAME=SPARQLWrapper
VERSION=1.6.3 # remind to check version before run!
DESTDIR =
DOCDIR=doc
PYTHON=python

doc:	clean
	mkdir -p $(DOCDIR)
	epydoc -v -n "$(NAME) $(VERSION)" -o $(DOCDIR) --html SPARQLWrapper

clean:
	rm -rf $(DOCDIR)