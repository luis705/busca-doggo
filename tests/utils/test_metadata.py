from tempfile import NamedTemporaryFile

from busca_doggo.utils import ReadMeta


class TestReadMeta:
    name = 'teste'
    version = 5
    log = 'teste.log'
    meta_string = (
        '{'
        '"project_name": "%s",'
        '"version": %d,'
        '"logger": { "config": "%s" }'
        '}' % (name, version, log)
    )

    meta_file = NamedTemporaryFile(delete=False)

    with open(meta_file.name, mode='w') as f:
        f.write(meta_string)

    meta = ReadMeta(meta_file.name)
    print(meta.metadata)

    def test_name(self):
        assert self.meta.project_name() == self.name

    def test_version(self):
        assert self.meta.version() == self.version

    def test_logger(self):
        assert str(self.meta.logger('config')) == self.log
