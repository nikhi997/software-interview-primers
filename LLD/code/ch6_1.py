class Logger:
    def __init__(self,filename="application.log"):
        self.filename=filename

    def log(self, message):
        with open(self.filename,"a") as f:
            f.write(f"{message}/n")

class app:
    def __init__(self,logger):
        self.logger=logger

    def action(self):
        self.logger.log("acted on something")


class SingletonLogger:
    _instance=None
    def __new__(cls, filename="application.log"):
        if not cls._instance:
            logger=super().__new__(cls)
            logger.filename= filename
            cls._instance=logger
        return cls._instance
