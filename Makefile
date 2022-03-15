# SPARQLWrapper Makefile

NAME=SPARQLWrapper
VERSION=`python -c "import SPARQLWrapper,sys;sys.stdout.write(SPARQLWrapper.__version__)";`
DESTDIR =
DOCDIR=docs

doc:	clean
	$(MAKE) -C ${DOCDIR} html

clean:
	$(MAKE) -C ${DOCDIR}  clean
	rm -rf build
	find . -name "*.pyc" -delete
