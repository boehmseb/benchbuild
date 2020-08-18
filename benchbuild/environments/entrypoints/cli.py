import typing as tp

import rich
from plumbum import cli

from benchbuild import experiment, plugins, project, source
from benchbuild.cli.main import BenchBuild
from benchbuild.environments.domain import commands
from benchbuild.environments.service_layer import messagebus, unit_of_work
from benchbuild.experiment import ExperimentIndex
from benchbuild.project import ProjectIndex


@BenchBuild.subcommand("container")
class BenchBuildContainer(cli.Application):
    experiment_args: tp.List[str] = []
    group_args: tp.List[str] = []

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def set_experiments(self, names: tp.List[str]) -> None:
        self.experiment_args = names

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def set_group(self, groups: tp.List[str]) -> None:
        self.group_args = groups

    def main(self, *projects: str) -> int:
        plugins.discover()

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        discovered_experiments = experiment.discovered()
        wanted_experiments = dict(
            filter(lambda pair: pair[0] in set(cli_experiments),
                   discovered_experiments.items()))
        unknown_experiments = list(
            filter(lambda name: name not in discovered_experiments.keys(),
                   set(cli_experiments)))

        if unknown_experiments:
            rich.print('Could not find ', str(unknown_experiments),
                       ' in the experiment registry.')
        if not wanted_experiments:
            rich.print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(projects, cli_groups)
        if not wanted_projects:
            rich.print("No projects selected.")
            return -2

        create_project_images(wanted_projects)
        create_experiment_images(wanted_experiments, wanted_projects)


def enumerate_projects(
        projects: ProjectIndex) -> tp.Generator[project.Project, None, None]:
    for prj_class in projects.values():
        for variant in source.product(*prj_class.SOURCE):
            context = source.context(*variant)
            yield prj_class(context)


def make_version_tag(*versions) -> str:
    return '-'.join([str(v) for v in versions])


def make_image_name(name: str, tag: str) -> str:
    return f'{name}:{tag}'


def create_project_images(projects: ProjectIndex) -> None:
    for prj in enumerate_projects(projects):
        version = make_version_tag(*prj.variant.values())
        image_tag = make_image_name(f'{prj.name}/{prj.group}', version)

        cmd = commands.CreateProjectImage(image_tag, prj.container)
        uow = unit_of_work.BuildahUnitOfWork()

        results = messagebus.handle(cmd, uow)

        rich.print("The following images are available:")
        for res in results:
            rich.print('  ', res)


def enumerate_experiments(
        experiments: ExperimentIndex, projects: ProjectIndex
) -> tp.Generator[experiment.Experiment, None, None]:
    for exp_class in experiments.values():
        prjs = list(enumerate_projects(projects))
        yield exp_class(projects=prjs)


def create_experiment_images(experiments: ExperimentIndex,
                             projects: ProjectIndex) -> None:
    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(*prj.variant.values())
            base_tag = make_image_name(f'{prj.name}/{prj.group}', version)
            image_tag = make_image_name(f'{exp.name}/{prj.name}/{prj.group}',
                                        version)
            cmd = commands.CreateExperimentImage(base_tag, image_tag,
                                                 exp.container)
            uow = unit_of_work.BuildahUnitOfWork()

            results = messagebus.handle(cmd, uow)

            rich.print("The following images are available:")
            for res in results:
                rich.print('  ', res)