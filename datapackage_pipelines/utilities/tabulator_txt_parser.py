from tabulator.parsers.api import Parser
from tabulator.helpers import reset_stream


class TXTParser(Parser):
    """Parser to parse TXT data format.
    """

    # Public

    options = []

    def __init__(self, **options):

        # Set attributes
        self.__options = options
        self.__extended_rows = None
        self.__loader = None
        self.__chars = None

    @property
    def closed(self):
        return self.__chars is None or self.__chars.closed

    def open(self, source, encoding, loader):
        self.close()
        self.__loader = loader
        self.__chars = loader.load(source, encoding, mode='t')
        self.reset()

    def close(self):
        if not self.closed:
            self.__chars.close()

    def reset(self):
        reset_stream(self.__chars)
        self.__extended_rows = self.__iter_extended_rows()

    @property
    def extended_rows(self):
        return self.__extended_rows

    # Private

    def __iter_extended_rows(self):
        for number, line in enumerate(self.__chars, start=1):
            if line.endswith('\n'):
                line = line[:-1]
            yield (number, None, [line])
