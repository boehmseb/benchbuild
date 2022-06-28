from plumbum import local

import benchbuild as bb
from benchbuild import CFG, workload
from benchbuild.command import WorkloadSet, Command, SourceRoot
from benchbuild.environments.domain import declarative
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs


class X264(bb.Project):
    """ x264 """

    NAME = "x264"
    DOMAIN = "multimedia"
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://code.videolan.org/videolan/x264.git',
            local='x264.git',
            refspec='HEAD',
            limit=5
        ),
        HTTP(
            remote={'tbbt-small': 'http://lairosiel.de/dist/tbbt-small.y4m'},
            local='tbbt-small.y4m'
        ),
        HTTP(
            remote={'sintel': 'http://lairosiel.de/dist/Sintel.2010.720p.raw'},
            local='sintel.raw'
        ),
    ]

    CONFIG = {"tbbt-small": [], "sintel": ["--input-res", "1280x720"]}
    CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

    # yapf: disable
    JOBS = {
        WorkloadSet(inputfile="tbbt-small.y4m"): [
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--crf", "30", "-b1", "-m1", "-r1", "--me", "dia" "--no-cabac", "--direct temporal", "--ssim", "--no-weightb"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--crf", "16", "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct", "--direct", "spatial", "--no-dct-decimate", "-t0", "", "--slice-max-mbs", "50"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--cr", "2", "-b", "-m", "-r", "--m", "he", "--cq", "jv", "--n", "10", "--psn", "--no-mixed-ref", "--b-adap", "", "--slice-max-siz", "1500"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--cr", "1", "-b", "-m", "-r", "--m", "um", "-t", "-", "al", "--b-pyrami", "norma", "--direc", "aut", "--no-fast-pski", "--no-mbtree"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--cr", "2", "-b", "-m", "-r", "--m", "es", "-t", "-", "al", "--psy-r", "1.0:1.", "--slice", "4"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--frame", "5", "--cr", "2", "-b", "-m1", "-r", "--m", "tes", "-t2"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--frame", "5", "-q", "-m", "-r", "--m", "he", "-Aall"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.raw", "--threads", "1", "-o", "/dev/null", "--frame", "5", "-q", "-m", "-r", "--m", "he", "--no-cabac")
        ],
        WorkloadSet(inputfile="sintel.raw"): [
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "30", "-b1", "-m1", "-r1", "--me", "dia" "--no-cabac", "--direct temporal", "--ssim", "--no-weightb"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "16", "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct", "--direct", "spatial", "--no-dct-decimate", "-t0", "", "--slice-max-mbs", "50"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--cr", "2", "-b", "-m", "-r", "--m", "he", "--cq", "jv", "--n", "10", "--psn", "--no-mixed-ref", "--b-adap", "", "--slice-max-siz", "1500"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--cr", "1", "-b", "-m", "-r", "--m", "um", "-t", "-", "al", "--b-pyrami", "norma", "--direc", "aut", "--no-fast-pski", "--no-mbtree"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--cr", "2", "-b", "-m", "-r", "--m", "es", "-t", "-", "al", "--psy-r", "1.0:1.", "--slice", "4"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frame", "5", "--cr", "2", "-b", "-m1", "-r", "--m", "tes", "-t2"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frame", "5", "-q", "-m", "-r", "--m", "he", "-Aall"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frame", "5", "-q", "-m", "-r", "--m", "he", "--no-cabac")
        ]
    }
    # yapf: enable

    @workload.define(workload.COMPILE)
    def compile(self):
        x264_repo = local.path(self.source_of('x264.git'))
        clang = bb.compiler.cc(self)

        with local.cwd(x264_repo):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with local.env(CC=str(clang)):
                _configure(
                    "--disable-thread", "--disable-opencl", "--enable-pic"
                )

            _make = bb.watch(make)
            _make("clean", "all", "-j", get_number_of_jobs(CFG))
