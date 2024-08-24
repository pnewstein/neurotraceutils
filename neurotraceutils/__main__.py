"""
commandline interface for the utility
"""
import sys
from pathlib import Path

from h5py import File
import click

from .output import write_swcs
from .swc import get_filement_paths_or_err, NoFilementError

@click.group()
def cli():
    pass

@cli.command(help="Converts imaris ims files into a directory of swc files")
@click.option('-o', '--output-dir', default=None, help="The parent directory where swc subdirectories will be located")
@click.argument('ims-file', nargs=-1, type=click.Path(exists=True))
def ims2swc(output_dir, ims_file):
    if not ims_file:
        click.echo("Error: no ims files specified", err=True)
        sys.exit(2)
    if output_dir is not None:
        output_dir=Path(output_dir)
    for file in ims_file:
        click.echo(file, err=True)
        if Path(file).suffix != ".ims":
            click.echo(f"Error: {file} is not an imaris file", err=True)
            sys.exit(2)
        with File(file) as h5f:
            write_swcs(h5f, out_dir_parent=output_dir / Path(file).parent)


@cli.command(help="writes paths containing filements to stdout")
@click.argument('ims-file', nargs=-1, type=click.Path(exists=True))
def pollswc(ims_file):
    if not ims_file:
        click.echo("Error: no ims files specified", err=True)
        sys.exit(2)
    for file in ims_file:
        if Path(file).suffix != ".ims":
            click.echo(f"Error: {file} is not an imaris file", err=True)
            sys.exit(2)
        with File(file) as h5f:
            try:
                get_filement_paths_or_err(h5f)
            except NoFilementError:
                continue
            click.echo(str(Path(file).resolve()))
cli()
