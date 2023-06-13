
class State:
    def __init__(self) -> None:
        self.interrupted = False

    def Begin(self):
        self.interrupted = False

    def End(self):
        self.interrupted = False

    def IsInterrupted(self):
        return self.interrupted

    def Interrupt(self):
        self.interrupted = True

state:State = State()

