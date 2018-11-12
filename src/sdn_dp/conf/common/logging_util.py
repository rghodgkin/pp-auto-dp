import sys
import logging

LOGGING_FORMAT = '%(asctime)s %(levelname)7s: %(filename)s:%(lineno)s[%(funcName)s]-> %(message)s'


def init(file, level):
    if file is None:
        file = "pytest.log"
    if level is None:
        level = "DEBUG"

    logging.getLogger().setLevel(level.upper())

    formatter = logging.Formatter(LOGGING_FORMAT)

    # stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # file
    handler = logging.FileHandler(file)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
