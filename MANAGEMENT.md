# Management documentation

The project keeps a very low-profile on managing, so we try to keep it simple.

## Contributions

Every contributor (patchs, pull requests, new features, etc) gets part of 
ownership by be mentioned as contributor to the project (`AUTHORS.txt`).

## Release

The release process is quite simple, just few things have to be done:

First, do not forget to update the changelog (`ChangeLog.txt` file).

Then you have to [create a release](https://github.com/blog/1547-release-your-software) 
by tagging the master branch:

    git tag x.y.z
    git push --tags

And then upload the release to pypi:

    python setup.py register sdist --formats=gztar,zip bdist_egg upload

Don't forget to increment to the next version in the corresponding files
(`setup.py` and `SPARQLWrapper/__init__.py`).

