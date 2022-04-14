class CurrentRelay:
    def __init__(self, breaker, current_indexes):
        self.current_indexes = current_indexes
        self.breaker = breaker
        self.current_threshold = 1
        self.time_threshold = 5000  # 5000 отсчетов = 0.5 секунд
        self.acted = False

    def process(self, measurement):
        if not self.acted:
            for channel in self.current_indexes:
                if measurement[channel] >= self.current_threshold:
                    self.acted = True
        else:
            self._count_down()

    def _count_down(self):
        self.time_threshold -= 1
        if self.time_threshold == 0:
            self.breaker.turn_off()
