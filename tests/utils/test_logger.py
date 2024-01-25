from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from busca_doggo.utils import setup_logger, setup_logs_folder


class TestLogger:
    def test_log_folder_gets_created(self):
        with TemporaryDirectory() as data_path:
            data_path = Path(data_path)

            setup_logs_folder(data_path)

            assert data_path.is_dir()
            assert data_path.exists()

    @pytest.mark.parametrize(
        'folder_name',
        ['string', 1, 2.0, {'dict': 'teste'}, ['lista'], {'set'}, ('tupla',)],
    )
    def test_setup_logs_folder_raises_on_wrong_input(self, folder_name):
        with pytest.raises(ValueError):
            setup_logs_folder(folder_name)
            assert False

    def test_default_logger_string_format(self, caplog):
        setup_logger(Path('caminho'))
        assert (
            'Arquivo de configurações do logger não encontrado em'
            in caplog.text
        )

    @pytest.mark.parametrize(
        'log_config',
        ['string', 1, 2.0, {'dict': 'teste'}, ['lista'], {'set'}, ('tupla',)],
    )
    def test_setup_loggger_raises_on_wrong_input(self, log_config):
        with pytest.raises(ValueError):
            setup_logger(log_config)
            assert False

    def test_logging_format_options(self, caplog):
        log_file = NamedTemporaryFile(mode='w', delete=False)

        with open(log_file.name, mode='w') as f:
            f.write(
                '{ "version": 1, "formatters": { "simple": { "format": "%(levelname)s - %(message)s",'
                '"datefmt": "%Y-%m-%d %H:%M:%S" } }, "handlers": { "console": { "class": "logging.StreamHandler",'
                '"level": "WARNING", "formatter": "simple", "stream": "ext://sys.stdout" } },'
                '"loggers": { "busca_doggo": { "level": "INFO", "handlers": ["console"] } } }'
            )

        logger = setup_logger(Path(log_file.name))

        assert caplog.text == ''

        logger.info('INFO TEST')
        logger.warning('WARNING TEST')
        logger.error('ERROR TEST')
        logged = caplog.text.split('\n')

        assert 'INFO TEST' in logged[0]
        assert 'WARNING TEST' in logged[1]
        assert 'ERROR TEST' in logged[2]
