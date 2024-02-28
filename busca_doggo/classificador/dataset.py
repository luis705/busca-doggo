import shutil
from logging import Logger
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

from torch.utils.data import Dataset
from torchvision.io import read_image
from tqdm import tqdm


class DogBreedDataset(Dataset):
    """
    Classe de dataset do pytorch, ver
    [torch.utils.dataset](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html).
    Há a opção de utilizar o dataset previamente baixado ou baixá-lo diretamente na instanciação da classe.
    No primeiro caso

    Args:
        logger (Logger): Objeto para salvar logs
        transform (Union[transform, None]): Transformação aplicada nos dados, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        target_transform (Union[transform, None]): Transformação aplicada nos labels, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        path (Path): Caminho onde os dados estão ou serão salvos (subdiretórios de raças)
        download_path (Path): Caminho onde os dados serão baixados do kaggle

    Attributes:
        logger (Logger): Objeto para salvar logs
        transform (Union[transform, None]): Transformação aplicada nos dados, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        target_transform (Union[transform, None]): Transformação aplicada nos labels, ver [torchvision.transforms](https://pytorch.org/vision/0.9/transforms.html)
        path (Path): Caminho onde as imagens estão
        download_path (Path): Caminho onde as imagens serão baixadas
        kaggle_api (Union[KaggleApi, None]): Objeto de API do Kaggle para baixar o dataset. Valor padrão é None, caso `generate_dataset` seja chamado se torna um objeto KaggleApi
        imagens (list[Path]): Lista contendo o caminho de cada imagem, necessário para manter sempre a mesma ordem
        labels (list[str]): Lista contendo o label de cada imagem
    """

    def __init__(
        self,
        logger: Logger,
        transform: Union[callable, None] = None,
        target_transform: Union[callable, None] = None,
        path: Optional[Path] = Path('dados', 'Imagens'),
        download_path: Optional[Path] = Path('dados'),
        force_download: Optional[bool] = False,
        verbose: Optional[bool] = False,
    ) -> None:
        # Metadados da classe
        self.logger = logger
        self.kaggle_api = None
        self.path = Path(path)
        self.download_path = Path(download_path)

        # Funções de transformação
        self.transform = transform
        self.target_transform = target_transform

        # Gerando dataset, se necessário
        self.generate_dataset(force=force_download, verbose=verbose)
        if not self.path.exists():
            logger.critical(
                'O caminho com os dados não existe. Ocorreu algum erro na hora de baixá-los.'
            )

        # Carregando dataset em memória
        self.imagens = list(self.path.iterdir())
        self.labels = [
            "_".join(img.stem.split('_')[:-1]).lower()
            for img in self.imagens
        ]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img = read_image(self.imagens[idx])
        label = self.labels[idx]

        if self.transform:
            img = self.transform(img)
        if self.target_transform:
            label = self.target_transform(label)

        return img, label
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

    def _unzip_dataset(
        self, verbose: bool = False, force: bool = False
    ) -> None:
        """
        Descompacta dataset baixado salvando assim as imagens prontas para serem processadas.

        Args:
            verbose (bool) : Verbosidade do processo
            force (bool) : Se `True` realiza o download mesmo se o arquivo já existe

        Returns:
            Path: diretório contendo os subdiretórios de cada raça de cachorro. Caso `self.path` seja um diretório e `force` seja Falso retorna o próprio `self.path`

        """
        if (
            self.path.exists()
            and self.path.is_dir()
            and len(list(self.path.iterdir()))
            and not force
        ):
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
                desc='Quantidade descompactado',
            ) as pbar:
                for arquivo in compactado.namelist():
                    pbar.update(compactado.getinfo(arquivo).compress_size)
                    compactado.extract(member=arquivo, path=self.download_path)

        shutil.rmtree(self.download_path / 'annotations')
        shutil.copytree(self.download_path / 'images' / 'Images', self.path)
        shutil.rmtree(self.download_path / 'images')

    def _corrige_imagens(
            self, verbose: bool = False
    ) -> None:
        subdirs = [sub for sub in self.path.iterdir() if sub.is_dir()]

        if len(subdirs) == 0:
            return

        for sub in tqdm(
            subdirs,
            desc='Analisando diretórios de cachorros',
            disable=not verbose,
        ):
            # Transforma objeto Path em string
            # Em seguida separa a partir de "-"
            # Seleciona todos os itens menos o primeiro
            # Deixando assim só o nome da raça
            # Junta lista com "-" caso haja hífen no nome
            raca = '-'.join(str(sub).split('-')[1:])
            imagens = list(sub.iterdir())
            total = len(imagens)
            self.logger.info(f'Organizando {total} imagens de {raca}')

            for indice, cachorro in tqdm(
                enumerate(sub.iterdir()),
                desc=raca,
                total=total,
                disable=not verbose,
                leave=False,
            ):
                caminho_completo = cachorro.resolve()
                caminho_atualizado = (
                    self.path / f'{raca}_{indice:03}{caminho_completo.suffix}'
                ).resolve()
                caminho_completo.rename(caminho_atualizado)
            sub.rmdir()

    def generate_dataset(self, verbose: bool = False, force: bool = False):
        """
        Gera o dataset ao baixá-lo do Kaggle e descompactá-lo.

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
        self._corrige_imagens(verbose=verbose)
        self.logger.info(f'Dataset disponível em: {self.path.resolve()}')


if __name__ == '__main__':
    from busca_doggo.utils import ReadMeta, log

    metadata = ReadMeta('../../metadata.json')
    logger = log.setup_logger(metadata.logger('config'))

    DogBreedDataset(
        logger=logger,
        transform=None,
        path=metadata.data('image_path'),
        download_path=metadata.data('download_path'),
        force_download=False,
        verbose=True,
    )
