# -*- coding: utf-8 -*-
import os
import inspect
import unittest
import sys

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

from SPARQLWrapper.main import parse_args, main

class SPARQLWrapper_Test(unittest.TestCase):

    def testHelp(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['-h'])

        self.assertEqual(cm.exception.code, 0)


    def testVersion(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['-V'])

        self.assertEqual(cm.exception.code, 0)


    def testNoarg(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args([])

        self.assertEqual(cm.exception.code, 1)
