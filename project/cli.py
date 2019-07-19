#!/usr/bin/env python2
# Author: Vlad Doster (mvdoster (at) gmail.com)
# Small cli tool to run different versions of program

import click

@click.group()
@click.option('-n', '--num-residents', multiple=True)
def cli(num_residents):
    click.echo('Running cli. . .')

@cli.command()
def run_serial():
    """Run streets4serial.py"""
    click.echo("Running serial version")

@cli.command()
@click.option('--num-threads', required=True)
def run_mpi():
    """Run streets4mpi.py"""
    click.echo('Running mpi version with %s nodes' % (num_threads))


@cli.command()
@click.option('--num-threads', required=True)
def run_multi_proc(num_threads):
    """Run streets4multiprocessing.py"""
    click.echo("Running multiprocessing version with %s nodes" % (num_threads))

if __name__ == '__main__':
    cli()
