def create_logger(config):
    if config["type"]=="file":
        return FileLogger(config["finename"])
    elif config["type"]=="console":
        return ConsoleLogger()


class FileLogger:
    def __init(self,filename):
        self.filename=filename

    def log(self, message):
        with open(self.filename,"a") as f:
            f.write(f"{message}\n")

class consoleLogger:
    def log(self,message):
        print(message)
