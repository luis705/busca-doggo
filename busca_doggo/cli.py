from pathlib import Path

import click

from busca_doggo.utils import ReadMeta, log


@click.group()
@click.option('--meta_path')
@click.pass_context
def cli(ctx, meta_path):
    metadata = ReadMeta(meta_path)
    ctx.obj['METADATA'] = metadata

    log.setup_logs_folder(Path('../logs'))
    logger = log.setup_logger(metadata.logger('config'))
    ctx.obj['LOGGER'] = logger
    logger.info('Iniciando a execução da CLI busca_doggo')


def entry_point():
    cli(obj={})
