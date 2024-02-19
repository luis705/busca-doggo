# Busca doggo

API para detecção de raça de cachorros em imagens. O projeto é separado em três pastas:

- [src](https://github.com/luis705/tree/main/src) que contém os arquivos de código do projeto dividida em
    - [src/classificador](https://github.com/luis705/tree/main/src/classificador) contendo o código da rede neural classificadora
    - [src/busca_doggo](https://github.com/luis705/tree/main/src/busca_doggo) contendo o código da API em si
- [docs](https://github.com/luis705/tree/main/docs) que contém os arquivos de documentação e
- [tests](https://github.com/luis705/tree/main/test) contendo os arquivos de testes.

## Instruções

### Pytorch
A instalação do pytorch utilizando o poetry é um pouquinho complicada. Para simplificar o problema adicionei no
`pyproject.toml` os caminhos de onde instalar a biblioteca. Assim há duas forma de instalação correta.

#### PyTorch com CUDA
Para instalar a versão CUDA do pytorch basta corrigir nas dependências a versão do framework CUDA instalado. A forma mais
simples de fazer isso é seguindo o passo a passo abaixo:
- Desinstalar todas as versões do framework CUDA;
- Verificar no [site do pytorch](https://pytorch.org/get-started/locally/) qual a versão CUDA mais
recente suportada e instalá-la;
- Remover do `pyproject.toml` as dependências `torch` e `torchvision` com `poetry remove torch torchvision`
- Reinstalar as dependências com `poetry add --source pytorch-gpu torch torchvision`

#### PyTorch para CPU
Este caso é mais simples, porém obviamente a rede neural demorará mais tempo para ser executada por completo. Para
instalar o pacote para CPU basta executar:
```
$ `poetry remove torch torchvision`
$ poetry add --source pytorch-cpu torch torchvision
```

## Objetivos
Este projeto foi iniciado com 3 objetivos principais em mente:

#### Transfer learning
Por mais que eu tenha trabalhado com diversos modelos de machine learning, nunca utilizei um modelo pré-treinado para
resolver algum problema. Desta forma quero entender como se estrutura um pipeline para treinamento e predição utilizando
essa técnica.

#### Arquitetura de projetos
Um cientista de dados precisa, além de saber de estatística, modelos de IA, análise e visualização de dados, saber
estruturar e manter um projeto em pé. Por isso estou utilizando também esse projeto como um piloto para alguns testes de
estrutura de projetos de execução de modelos de aprendizagem de máquina.

#### Portfólio
Por fim, mas não menos importante, decidi que em 2024 iria iniciar realmente meu portfólio de projetos de dados.
Acredito que deveria ter iniciado isso antes, já que estou na área desde 2020,.
Ainda assim acho que a demora foi interessante, pois me trouxe uma experiência que me permite criar projetos mais
complexos e bem feitos.

## Ferramentas utilizadas

Antes de falar do código em si, é importante falar um pouco sobre as ferramentas utilizadas em sua construção. São elas:

- Gerenciamento de dependências: [poetry](https://python-poetry.org/) 
- Testes: [pytest](https://docs.pytest.org/en/7.4.x/)
- Lint: [blue](https://blue.readthedocs.io/en/latest/) e [isort](https://pycqa.github.io/isort/)
- Documentação: [mkdocs](https://www.mkdocs.org/) com o tema [material](https://squidfunk.github.io/mkdocs-material/)

Além disso, utilizei também as bibliotecas [requests](https://requests.readthedocs.io/en/latest/) e [PyTorch](https://pytorch.org/).
Inclusive é importante notar um detalhe sobre a instalação do PyTorch: para poder utilizar a versão de GPU desta
biblioteca foi necessário fornecer no [`pyproject.toml`](https://github.com/luis705/tree/main/pyproject.toml) a url dos wheels desta versão diretamente.
Esses wheels só funcionarão caso exista uma GPU com possibilidade de utilizar CUDA e a versão 11.7 do CUDA estejam
instaladas na máquina, caso contrário, recomendo renomear o arquivo [`pyproject-cpu.toml`](https://github.com/luis705/tree/main/pyproject-cpu.toml)
para `pyproject.toml` antes de executar `poetry install`.

## Planejamento
O desenvolvimento dos modelos se dará de acordo com o planejamento na imagem a seguir.

![Planejamento da construção dos modelos. 
Passo 1 - rotinas para construção de dataset:
  Rotina para extração dos dados;
  Classe de dataset pytorch;
  Classe de dataloader pytorch
Passo 2 - rotinas para execução de treino - teste:
  Criação do loop de treino;
  Definição de métricas;
  Definição de baseline - AutoML
Passo 3 - definição do melhor modelo - transfer learning:
  Treino e avaliação de diversas modelo
  Seleção do campeão
](assets/img/Planejamento.png)

Após a definição do modelo a ser utilizado, o planejamento para a finalização do projeto - construção da API em si -
será criado.