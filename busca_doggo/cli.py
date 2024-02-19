from pathlib import Path

import click

from busca_doggo.classificador import DogBreedDataset
from busca_doggo.utils import ReadMeta, log


@click.group()
@click.option('--meta_path')
@click.pass_context
def cli(ctx, meta_path):
    metadata = ReadMeta(meta_path)
    ctx.obj['METADATA'] = metadata

    log.setup_logs_folder(metadata.logger('folder'))
    logger = log.setup_logger(metadata.logger('config'))
    ctx.obj['LOGGER'] = logger
    logger.info('Iniciando a execução da CLI busca_doggo')


@cli.command()
@click.option('--force', '-f', is_flag=True, type=bool, default=False)
@click.option('--verbose', '-v', is_flag=True, type=bool, default=False)
@click.pass_context
def get_dataset(ctx, force, verbose):
    metadata = ctx.obj['METADATA']
    logger = ctx.obj['LOGGER']

    dataset = DogBreedDataset(
        logger=logger,
        transform=None,
        path=metadata.data('image_path'),
        download_path=metadata.data('download_path'),
    )
    dataset.generate_dataset(verbose=verbose, force=force)


def entry_point():
    cli(obj={})
