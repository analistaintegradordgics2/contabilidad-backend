import logging
from pathlib import Path
from datetime import datetime


class DailyFileHandler(logging.FileHandler):

    def __init__(self, log_dir, *args, **kwargs):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        filename = self._get_filename()
        super().__init__(filename, *args, **kwargs)

    def _get_filename(self):
        fecha = datetime.now().strftime("%Y_%m_%d")
        return self.log_dir / f"errors_{fecha}.log"

    def emit(self, record):
        nuevo_archivo = self._get_filename()

        if str(nuevo_archivo) != self.baseFilename:
            self.stream.close()
            self.baseFilename = str(nuevo_archivo)
            self.stream = self._open()

        super().emit(record)