class Transformer:
    def __init__(self, signal_gen, cb, transform_rates):
        self.cb = cb
        self.signal = signal_gen
        self.transform_rates = transform_rates

    def get_data(self):
        if self.cb.get_state():
            before_tr = next(self.signal)
            after_tr = list()
            for i in range(len(before_tr)):
                if i == 0:
                    after_tr.append(before_tr[i]) # time
                else:
                    after_tr.append(before_tr[i] * 1000 / self.transform_rates[i-1])
            return tuple(after_tr)
        else:
            to_zero = next(self.signal)
            time = to_zero[0]
            zeroed = list()
            zeroed.append(time)
            zeroed.extend([0 for _ in range(0, len(to_zero)-1)])
            return tuple(zeroed)
