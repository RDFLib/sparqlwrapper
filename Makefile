# SPARQLWrapper Makefile

NAME=SPARQLWrapper
DESTDIR =
DOCDIR=doc
PYTHON=python

doc:	clean
	mkdir -p $(DOCDIR)
	epydoc -v -n $(NAME) -o $(DOCDIR) --html SPARQLWrapper

clean:
	rm -rf $(DOCDIR)