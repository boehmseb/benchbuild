from plumbum import local

import benchbuild as bb
from benchbuild.downloads import Git


class Lulesh(bb.Project):
    """ LULESH, Serial """

    NAME: str = 'lulesh'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    VERSION: str = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        lulesh_repo = bb.path(self.source_of('lulesh.git'))
        self.cflags += ["-DUSE_MPI=0"]

        cxx_files = local.cwd / lulesh_repo// "*.cc"
        clang = bb.compiler.cxx(self)
        with bb.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / lulesh_repo // "*.cc.o"
        with bb.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        lulesh = bb.watch(lulesh)

        for i in range(1, 15):
            lulesh("-i", i)


class LuleshOMP(bb.Project):
    """ LULESH, OpenMP """

    NAME: str = 'lulesh-omp'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    VERSION: str = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        lulesh_repo = bb.path(self.source_of('lulesh.git'))
        self.cflags = ['-DUSE_MPI=0', '-fopenmp']

        cxx_files = bb.cwd / lulesh_repo // "*.cc"
        clang = bb.compiler.cxx(self)
        with bb.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = bb.cwd / lulesh_repo // "*.cc.o"
        with bb.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        lulesh = bb.watch(lulesh)
        for i in range(1, 15):
            lulesh("-i", i)
