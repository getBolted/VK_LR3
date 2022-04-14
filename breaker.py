class CircuitBreaker:
    """
    Класс, реализующий функционал силового выключателя
    """

    def __init__(self, name):
        self.name = name
        self.__state = False

    def turn_on(self):
        self.__state = True

    def turn_off(self):
        self.__state = False

    def get_state(self):
        return self.__state
