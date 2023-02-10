# source : https://github.com/qwc-services/qwc-config-generator/blob/master/config_generator/config_generator.py

from logging import Logger as Log

class Logger:
    """Logger class
    Show and collect log entries.
    """

    LEVEL_DEBUG = 'debug'
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    LEVEL_CRITICAL = 'critical'

    def __init__(self, logger=None):
        """Constructor
        :param Logger logger: Logger
        """
        if logger:
            self.logger = logger
        else:
            self.logger = Log("Global Config Generator")

        self.logs = []

    def clear(self):
        """Clear log entries."""
        self.logs = []

    def log_entries(self):
        """Return log entries."""
        return self.logs

    def debug(self, msg):
        """Show debug log entry.
        :param str msg: Log message
        """
        self.logger.debug(msg)
        # do not collect debug entries

    def info(self, msg):
        """Add info log entry.
        :param str msg: Log message
        """
        self.logger.info(msg)
        self.add_log_entry(msg, self.LEVEL_INFO)

    def warning(self, msg):
        """Add warning log entry.
        :param str msg: Log message
        """
        self.logger.warning(msg)
        self.add_log_entry(msg, self.LEVEL_WARNING)

    def warn(self, msg):
        self.warning(msg)

    def error(self, msg):
        """Add error log entry.
        :param str msg: Log message
        """
        self.logger.error(msg)
        self.add_log_entry(msg, self.LEVEL_ERROR)

    def critical(self, msg):
        """Add critical log entry.
        :param str msg: Log message
        """
        self.logger.critical(msg)
        self.add_log_entry(msg, self.LEVEL_CRITICAL)

    def add_log_entry(self, msg, level):
        """Append log entry with level.
        :param str msg: Log message
        :param str level: Log level
        """
        self.logs.append({
            'msg': msg,
            'level': level
        })