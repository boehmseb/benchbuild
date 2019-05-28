"""
A plumbum compatible remote machine using our uchroot command.

The UchrootMachine implements a BaseRemoteMachine from plumbum and provides
'remote' command support for arbitrary uchroot-based containers. You can use
it similar to plumbum's local object (or SshMachine). All imported commands
are prefixed with an appropriate uchroot call.
"""
from __future__ import annotations

import logging
import platform
import sys

import six
from plumbum.commands import ConcreteCommand
from plumbum.machines.remote import BaseRemoteMachine, RemoteEnv
from plumbum.machines.session import ShellSession

from benchbuild.utils.cmd import uchroot
from benchbuild.utils.container import Container, Gentoo

LOG = logging.getLogger(__name__)

class UchrootMachine(BaseRemoteMachine):
    """
    uchroot based containers usable as plumbum remote machine.

    Supply a container implementation from benchbuild and use it like any other
    remote machine.
    """

    custom_encoding = sys.getfilesystemencoding()
    uname = platform.uname()[0]
    container = None

    def __init__(self, container: Container, uchroot_opts=(), encoding="utf8"):
        self.container = container
        self._cwd = "/"

        uchroot_args = ["-E", "-A", "-C", "-r", container.local,
                        "-u", 0, "-g", 0]
        uchroot_args.extend(uchroot_opts)

        self.uchroot_command = uchroot[tuple(uchroot_args)]
        BaseRemoteMachine.__init__(self, encoding=encoding)

    def __str__(self):
        return "uchroot://%s" % (self.container.local)

    def popen(self, *args, **kwargs):
        cmdline = []
        cmdline.extend(["-w", self.cwd, "--"])

        if args and hasattr(self, "env"):
            envdelta = self.env.getdelta()
            if envdelta:
                cmdline.append("env")
                cmdline.extend("%s=%s" % (k, v) for k, v in envdelta.items())
            if isinstance(args, (tuple, list)):
                cmdline.extend(args)
        else:
            cmdline.extend(args)

        cmd = self.uchroot_command[tuple(cmdline)]
        return cmd.popen(**kwargs)

    def session(self, isatty=False, new_session=False):
        return ShellSession(
            self.popen(
                ["/bin/sh"], (["-i"] if isatty else ["-s"]),
                new_session=new_session),
            self.custom_encoding, isatty, self.connect_timeout)
