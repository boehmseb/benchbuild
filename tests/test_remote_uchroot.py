"""Test Uchroot remote machine funcitonality."""
import unittest

from benchbuild.machines.uchroot import UchrootMachine
from benchbuild.utils.cmd import head
from benchbuild.utils.container import Gentoo


class TestRemoteUchrootMachine(unittest.TestCase):
    def test_import(self):
        ctm = UchrootMachine(Gentoo())
        bintrue = ctm["/bin/true"]
        bintrue()

    def test_import_complex(self):
        ctm = UchrootMachine(Gentoo())
        cat = ctm["/bin/cat"]
        out = (cat["/etc/os-release"] | head["-n", 1])()

        self.assertEqual("NAME=Gentoo\n", out,
                         "Gentoo container should identify itself")
