from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, mkdir

from benchbuild.downloads import Git


class BOTSGroup(project.Project):
    """
    Barcelona OpenMP Task Suite.

    Barcelona OpenMP Task Suite is a collection of applications that allow
    to test OpenMP tasking implementations and compare its behaviour under
    certain circumstances: task tiedness, throttle and cut-offs mechanisms,
    single/multiple task generators, etc.

    Alignment: Aligns sequences of proteins.
    FFT: Computes a Fast Fourier Transformation.
    Floorplan: Computes the optimal placement of cells in a floorplan.
    Health: Simulates a country health system.
    NQueens: Finds solutions of the N Queens problem.
    Sort: Uses a mixture of sorting algorithms to sort a vector.
    SparseLU: Computes the LU factorization of a sparse matrix.
    Strassen: Computes a matrix multiply with Strassen's method.
    """

    DOMAIN: str = 'bots'
    GROUP: str = 'bots'
    VERSION: str = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/bsc-pm/bots',
            local='bots.git',
            limit=5,
            refspec='HEAD')
    ]

    path_dict = {
        "alignment": "serial/alignment",
        "fft": "serial/fft",
        "fib": "serial/fib",
        "floorplan": "serial/floorplan",
        "health": "serial/health",
        "knapsack": "serial/knapsack",
        "nqueens": "serial/nqueens",
        "sort": "serial/sort",
        "sparselu": "serial/sparselu",
        "strassen": "serial/strassen",
        "uts": "serial/uts"
    }

    input_dict = {
        "alignment": ["prot.100.aa", "prot.20.aa"],
        "floorplan": ["input.15", "input.20", "input.5"],
        "health": ["large.input", "medium.input", "small.input", "test.input"],
        "knapsack": [
            "knapsack-012.input", "knapsack-016.input", "knapsack-020.input",
            "knapsack-024.input", "knapsack-032.input", "knapsack-036.input",
            "knapsack-040.input", "knapsack-044.input", "knapsack-048.input",
            "knapsack-064.input", "knapsack-096.input", "knapsack-128.input"
        ],
        "uts": [
            "huge.input", "large.input", "medium.input", "small.input",
            "test.input", "tiny.input"
        ]
    }

    def compile(self):
        bots_repo = local.path(self.source[0].local)
        makefile_config = bots_repo / "config" / "make.config"
        clang = compiler.cc(self)

        with open(makefile_config, 'w') as config:
            lines = [
                "LABEL=benchbuild",
                "ENABLE_OMPSS=",
                "OMPSSC=",
                "OMPC=",
                "CC={cc}",
                "OMPSSLINK=",
                "OMPLINK={cc} -fopenmp",
                "CLINK={cc}",
                "OPT_FLAGS=",
                "CC_FLAGS=",
                "OMPC_FLAGS=",
                "OMPSSC_FLAGS=",
                "OMPC_FINAL_FLAGS=",
                "OMPSSC_FINAL_FLAG=",
                "CLINK_FLAGS=",
                "OMPLINK_FLAGS=",
                "OMPSSLINK_FLAGS=",
            ]
            lines = [l.format(cc=clang) + "\n" for l in lines]
            config.writelines(lines)
        mkdir(bots_repo / "bin")
        with local.cwd(bots_repo):
            make_ = run.watch(make)
            make_("-C", self.path_dict[self.name])

    def run_tests(self):
        binary_name = "{name}.benchbuild.serial".format(name=self.name)
        bots_repo = local.path(self.source[0].local)
        binary_path = bots_repo / "bin" / binary_name
        exp = wrapping.wrap(binary_path, self)
        exp = run.watch(exp)

        if self.name in self.input_dict:
            for test_input in self.input_dict[self.name]:
                input_file = bots_repo / "inputs" / self.name / test_input
                exp("-f", input_file)
        else:
            exp()


class Alignment(BOTSGroup):
    NAME: str = 'alignment'


class FFT(BOTSGroup):
    NAME: str = 'fft'


class Fib(BOTSGroup):
    NAME: str = 'fib'


class FloorPlan(BOTSGroup):
    NAME: str = 'floorplan'


class Health(BOTSGroup):
    NAME: str = 'health'


class Knapsack(BOTSGroup):
    NAME: str = 'knapsack'


class NQueens(BOTSGroup):
    NAME: str = 'nqueens'


class Sort(BOTSGroup):
    NAME: str = 'sort'


class SparseLU(BOTSGroup):
    NAME: str = 'sparselu'


class Strassen(BOTSGroup):
    NAME: str = 'strassen'


class UTS(BOTSGroup):
    NAME: str = 'uts'
