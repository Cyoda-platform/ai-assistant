import logging
import sys
import time


def setup_root_logger(level=logging.INFO):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    #todo improve
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    class UTCFormatter(logging.Formatter):
        converter = time.gmtime
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                s = time.strftime(datefmt, ct)
            else:
                s = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
                s += ".%03dZ" % (record.msecs)
            return s

    formatter = UTCFormatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(threadName)s] %(name)s: "
            "%(message)s [in %(filename)s:%(funcName)s:%(lineno)d]"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)