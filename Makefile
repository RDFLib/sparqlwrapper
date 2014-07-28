# SPARQLWrapper Makefile

NAME=SPARQLWrapper
VERSION=`python -c "import SPARQLWrapper,sys;sys.stdout.write(SPARQLWrapper.__version__)";`
DESTDIR =
DOCDIR=doc

doc:	clean
	mkdir -p $(DOCDIR)
	epydoc -v -n "$(NAME) $(VERSION)" -o $(DOCDIR) --html SPARQLWrapper

clean:
	rm -rf $(DOCDIR)
