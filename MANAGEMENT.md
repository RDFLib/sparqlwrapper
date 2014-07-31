# Management documentation

The project keeps a very low-profile on managing, so we try to keep it simple.

## Contributions

Every contributor (patchs, pull requests, new features, etc) gets part of ownership by be mentioned as contributor to the project (`AUTHORS.md`).

## Release

### Software

The release process is quite simple, just few things have to be done:

First, do not forget to update the changelog (`ChangeLog.txt` file). That information could be added later to the release at github.

Then you have to [create a release](https://github.com/blog/1547-release-your-software) by tagging the master branch:

    git tag x.y.z
    git push --tags

And then upload the release to pypi:

    python setup.py register sdist --formats=gztar,zip bdist_egg upload

Please, don't forget to increment to the next module (`SPARQLWrapper/__init__.py` file).

### Documentation

In order to provide online documentation, some steps need to be accomplished:

1. First, generate the documentation using [epydoc](http://epydoc.sourceforge.net/) using the makefile

	make doc

2. And then upload the documentation generated (`doc` folder) to GitHub Pages (`gh-pages` branch).

3. After that, the online version of the documentation would be available on [GitHub Pages](http://rdflib.github.io/sparqlwrapper/resources/doc).
