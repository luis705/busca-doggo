import json
import logging.config
import os
from pathlib import Path
from typing import Optional


def setup_logs_folder(logs_folder: Path) -> None:
    """
    Cria pasta de armazenamento de logs, caso necessário.

    Args:
        logs_folder (Path): caminho onde os logs serão armazenados
    """
    if not isinstance(logs_folder, Path):
        raise ValueError(
            'O argumento `logs_folder` deve ser um objeto `Path` e não {type(logs_folder)}'
        )
    logs_folder.mkdir(exist_ok=True)


def setup_logger(config_path: Optional[Path] = None) -> logging.Logger:
    """
    Realiza setup do logger de acordo com configurações do arquivo JSON fornecido.

    Exemplo de arquivo de configuração:

    ```JSON
    {
      "version": 1,
      "formatters":
      {
        "simple":
        {
          "format": "%(asctime)s | %(levelname)-8s | %(name)s : %(message)s",
          "datefmt": "%Y-%m-%d %H:%M:%S"
        }
      },
      "handlers":
      {
        "console":
        {
          "class": "logging.StreamHandler",
          "level": "WARNING",
          "formatter": "simple",
          "stream": "ext://sys.stdout"
        }
      },
      "loggers":
      {
        "busca_doggo":
        {
          "level": "INFO",
          "handlers": ["console"]
        }
      }
    }
    ```

    Args:
        config_path (Path): caminho para o arquivo de configurações do logger.

    Returns:
        Logger: objeto de logging do projeto
    """
    if not isinstance(config_path, Path):
        raise ValueError(
            'O argumento `config_path` deve ser um objeto `Path` e não {type(logs_folder)}'
        )

    logger = logging.getLogger('busca_doggo')

    if config_path is None or not os.path.exists(config_path):
        logging.basicConfig(
            format='%(asctime)s | %(levelname)-8s | %(name)s : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO,
        )
        if config_path is not None:
            logger.warning(
                f'Arquivo de configurações do logger não encontrado em {config_path.resolve()} - utilizando configuração padrão'
            )
    else:
        with open(config_path, 'rt') as config:
            logging.config.dictConfig(json.load(config))

    return logger
