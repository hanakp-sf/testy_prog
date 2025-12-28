class Processor:
    def start(self, val:str, num:int):
        print(f"Starting with values {val}, {num}")

    def stop(self, val:str, num:int):
        print(f"Stopping with value {val}, {num}")

    def __init__(self):
        self.handlers = {
            "start": self.start,
            "stop": self.stop,
        }
    def process(self):
        self.handlers["start"]('init', 3)
        self.handlers["stop"]('closing', -5)

p = Processor()
p.process()
