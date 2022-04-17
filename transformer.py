class Transformer:
    def __init__(self, signal_gen, cb, transform_rates):
        """
        :param signal_gen: генератор измерений
        :param cb: объект силового выключателя
        :param transform_rates: кортеж коэффициентов трансформации для каждого сигнала в кортеже измерений из генератора
        """
        self.cb = cb
        self.signal = signal_gen
        self.transform_rates = transform_rates

    def get_data(self):
        """
        Метод, реализующий функционал трансформации первичных величин во вторичные и обнуление сигналов при размыкании
        выключателя
        """
        if self.cb.get_state(): # если выключатель замкнут
            before_tr = next(self.signal) # считываем следущие измерения из генератора
            after_tr = list()
            for i in range(len(before_tr)): # пробегаемся по кортежу измерений
                if i == 0:
                    after_tr.append(before_tr[i]) # добавляем метку времени
                else:
                    after_tr.append(before_tr[i] * 1000 / self.transform_rates[i-1]) # добавляем значение измерения из канала с пересчетом
            return tuple(after_tr) # преобразуем в кортеж
        else:
            to_zero = next(self.signal) # если выключатель разомкнут, все также считываем измерения из генератора
            time = to_zero[0] # считываем метку времени из кортежа измерений
            zeroed = list()
            zeroed.append(time) # добавляем метку времени в пустой список
            zeroed.extend([0 for _ in range(1, len(to_zero))]) # добавим ноликов по числу каналов в кортеже измерений
            return tuple(zeroed) # преобразуем в кортеж
