from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Name

class FixUrllib2(BaseFix):
    PATTERN = "power< fixprefix='urllib2' trailer< '.' '_opener' > >|power< fixprefix='urllib2' trailer< '.' '_opener' > trailer< '.' handlers='handlers' > >"

    def transform(self, node, results):
        fixprefix = results['fixprefix']
        fixprefix.replace(Name('urllib.request', prefix=fixprefix.prefix))
