import benchbuild as bb

from benchbuild.downloads import Git, HTTP
from benchbuild.utils.cmd import git, make, tar


class Minisat(bb.Project):
    """ minisat benchmark """

    NAME: str = 'minisat'
    DOMAIN: str = 'verification'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/niklasso/minisat',
            local='minisat.git',
            limit=5,
            refspec='HEAD'),
        HTTP(remote={
            '2016-11-minisat.tar.gz':
            'http://lairosiel.de/dist/2016-11-minisat.tar.gz'
        },
             local='inputs.tar.gz')
    ]

    def run_tests(self):
        minisat_repo = bb.path(self.source_of('minisat.git'))
        minisat_build = minisat_repo / 'build' / 'dynamic'
        minisat_lib = minisat_build / 'lib'
        minisat_bin = minisat_build / 'bin'

        test_source = bb.path(self.source_of('inputs.tar.gz'))
        test_dir = bb.path('./minisat/')
        tar('xf', test_source)

        testfiles = test_dir // "*.cnf.gz"

        minisat = bb.wrap(minisat_bin / "minisat", self)
        for test_f in testfiles:
            minisat_test = bb.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib) < test_f))
            minisat_test()

    def compile(self):
        minisat_repo = bb.path(self.source_of('minisat.git'))
        with bb.cwd(minisat_repo):
            # FIXME: That needs to be modeled with Git() download handlers.
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")
            #

            make_ = bb.watch(make)
            make_("config")

            clang = bb.compiler.cc(self)
            clang_cxx = bb.compiler.cxx(self)

            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                  "sh")
