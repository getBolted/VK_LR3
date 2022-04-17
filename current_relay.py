class CurrentRelay:
    """
    Класс, реализующий функуионал токовой отсечки с выдержкой времени
    """
    def __init__(self, breaker, current_indexes, current_threshold, time_threshold):
        """
        :param breaker: объект силового вылкючателя
        :param current_indexes: кортеж из чисел-индексов, по которым располагаются необходимые для данной зашиты токи в
        кортеже со всеме измерениями
        :param current_threshold: уставка по току
        :param time_threshold: уставка по напряжению
        """
        self.current_indexes = current_indexes
        self.breaker = breaker
        self.current_threshold = current_threshold
        self.time_threshold = time_threshold
        self.acted = False # флажок, указывающий на статус срабатывания защиты

    def process(self, measurement: tuple):
        """
        :param measurement:кортеж со значениями токов и напряжений и отметкой времени
        """
        if not self.acted:  # проверяем не срабатывала ли уже защита
            for channel in self.current_indexes:
                if measurement[channel] >= self.current_threshold:
                    self.acted = True
        else:
            self._count_down()

    def _count_down(self):
        """
            Функция-счетчик, уменьшающее уставку по времени на 1 за каждое измерение после превышения порога уставки
        """
        self.time_threshold -= 1
        if self.time_threshold == 0:
            self.breaker.turn_off() # как только досчитали до конца уставки по времени - щелкаем выключатель
