import shutil
from logging import Logger
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

from torch.utils.data import Dataset
from tqdm import tqdm

from busca_doggo.utils import log


class DogBreedDataset(Dataset):
    """
    Classe de dataset do pytorch, ver
    [torch.utils.dataset](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html).
    Há a opção de utilizar o dataset previamente baixado ou baixá-lo diretamente na instanciação da classe.
    No primeiro caso

    Args:
        logger (Logger): Objeto para salvar logs
        transform (Union[transform, None]): Transformação aplicada nos dados, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        path (Path): Caminho onde os dados estão ou serão salvos (subdiretórios de raças)
        download_path (Path): Caminho onde os dados serão baixados do kaggle

    Attributes:
        logger (Logger): Objeto para salvar logs
        transform (Union[transform, None]): Transformação aplicada nos dados, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        path (Path): Caminho onde as imagens estão
        kaggle_api (Union[KaggleApi, None]): Objeto de API do Kaggle para baixar o dataset. Valor padrão é None, caso `generate_dataset` seja chamado se torna um objeto KaggleApi
    """

    def __init__(
        self,
        logger: Logger,
        transform: Union[callable, None] = None,
        path: Optional[Path] = Path('dados', 'Imagens'),
        download_path: Optional[Path] = Path('dados'),
    ) -> None:
        self.logger = logger
        self.path = Path(path)
        self.transform = transform
        self.kaggle_api = None
        self.download_path = Path(download_path)

    @staticmethod
    def _authenticate_on_kaggle():
        """
        Realiza autenticação na API do kaggle
        """
        from dotenv import load_dotenv

        load_dotenv()

        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        return api

    def _download_dataset(
        self, verbose: bool = False, force: bool = False
    ) -> None:
        """
        Baixa o conjunto de dados do kaggle.

        Args:
            verbose (bool) : Verbosidade do processo
            force (bool) : Se `True` realiza o download mesmo se o arquivo já existe
        """
        if self.download_path.exists() and not force:
            return

        shutil.rmtree(
            self.download_path / 'stanford-dogs-dataset.zip',
            ignore_errors=True,
        )
        self.logger.info(
            f'Iniciando download do dataset jessicali9530/stanford-dogs-dataset para {self.download_path.resolve()}'
        )

        # Preferimos descompactar manualmente, pois unzip=True no download faz com que
        # o arquivo compactado seja deletado, assim não é necessário baixar o arquivo
        # toda vez
        self.kaggle_api.dataset_download_files(
            'jessicali9530/stanford-dogs-dataset',
            path=self.download_path,
            unzip=False,
            quiet=not verbose,
            force=force,
        )

    def _unzip_dataset(self, verbose: bool = False, force: bool = False) -> None:
        """
        Descompacta dataset baixado salvando assim as imagens prontas para serem processadas.

        Atenção: o atributo self.path é sobrescrito para apontar para o diretório que os subdiretórios contendo
        as imagens está, ou seja, `self.path = self.path / 'Imagens'`, desta forma chama

        Args:
            verbose (bool) : Verbosidade do processo
            force (bool) : Se `True` realiza o download mesmo se o arquivo já existe

        Returns:
            Path: diretório contendo os subdiretórios de cada raça de cachorro. Caso `self.path` seja um diretório e `force` seja Falso retorna o próprio `self.path`

        """
        if self.path.exists() and self.path.is_dir() and not force:
            return

        shutil.rmtree(self.path, ignore_errors=True)
        self.logger.info(f'Descompactando conjunto de dados para {self.path}')

        with ZipFile(
            self.download_path / 'stanford-dogs-dataset.zip'
        ) as compactado:
            tamanho_bytes = sum([t.compress_size for t in compactado.filelist])
            with tqdm(
                total=tamanho_bytes,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                disable=not verbose,
            ) as pbar:
                for arquivo in compactado.namelist():
                    pbar.update(compactado.getinfo(arquivo).compress_size)
                    compactado.extract(member=arquivo, path=self.download_path)

        shutil.rmtree(self.download_path / 'annotations')
        shutil.copytree(self.download_path / 'images' / 'Images', self.path)
        shutil.rmtree(self.download_path / 'images')

    def generate_dataset(self, verbose: bool = False, force: bool = False):
        """
        Gera o dataset ao baixá-lo do Kaggle e descompactá-lo.

        Atenção: a propriedade `self.path` é modificada para apontar para o diretório contendo os subdiretórios das
        raças de cachorro.

        Args:
            verbose (bool): Verbosidade do processo
            force (bool): Se `True` realiza o download mesmo se o arquivo já existe

        """
        if force:
            self.logger.info(
                f'Flag `force` com valor `True`. Caso dados estejam disponíveis em {self.path.resolve()} eles serão sobrescritos'
            )
        self.kaggle_api = self._authenticate_on_kaggle()
        self._download_dataset(verbose=verbose, force=force)
        self._unzip_dataset(verbose=verbose, force=force)
        self.logger.info(f'Dataset disponível em: {self.path.resolve()}')
