from signals import *
from transformer import Transformer
from breaker import CircuitBreaker
from current_relay import CurrentRelay

if __name__ == '__main__':
    with open('A3_in.dat', 'r') as dat:
        dat_line_list = dat.readlines()
    with open('A3_in.cfg', 'r') as cfg:
        coef_line_list = cfg.readlines()

    coefs = config_parser(coef_line_list)
    signals = signal_converter(dat_line_list, coefs)
    gen = signals.prepare_signals()

    breaker = CircuitBreaker("CB1")
    breaker.turn_on()

    tr = Transformer(gen, breaker, (300, 300, 300, 1000, 1000, 1000, 300, 300, 300, 1000, 1000, 1000))

    relay = CurrentRelay(breaker, (1, 2, 3))

    while True:
        try:
            measurement = tr.get_data()
            relay.process(measurement)
            print(measurement)
        except StopIteration:
            print("COMTRADE is over!")
            break
