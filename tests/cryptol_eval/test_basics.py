import os
from pathlib import Path
import signal
import subprocess
import time
import unittest
from distutils.spawn import find_executable
import cryptol
from cryptol.bitvector import BV


class CryptolEvalServerTests(unittest.TestCase):
    # Connection to cryptol
    c = None

    @classmethod
    def setUpClass(self):
        dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.c = cryptol.connect("cryptol-eval-server socket --module M", cryptol_path=dir_path)


    def test_evaluation(self):
        c = self.c
        res = c.call('f', BV(size=8,value=0xff)).result()
        self.assertEqual(res, [BV(size=8,value=0xff), BV(size=8,value=0xff)])

    def test_disallowed_ops(self):
        pass # TODO/FIXME


if __name__ == "__main__":
    unittest.main()
