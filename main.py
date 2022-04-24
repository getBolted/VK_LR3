from signals import signal_converter, config_parser
from transformer import Transformer
from breaker import CircuitBreaker
from current_relay import CurrentRelay
from database import Database
import sqlite3 as sl

if __name__ == '__main__':
    con = sl.connect('relay_protection.db')

    with open('A3_in.dat', 'r') as dat:
        dat_line_list = dat.readlines()
    with open('A3_in.cfg', 'r') as cfg:
        coef_line_list = cfg.readlines()

    coefs = config_parser(coef_line_list)
    signals = signal_converter(dat_line_list, coefs)
    gen = signals.prepare()

    db = Database(signals)
    db.add_signals_table()

    breaker = CircuitBreaker("CB1")
    breaker.turn_on()

    tr = Transformer(signal_gen=gen, cb=breaker, transform_rates=(300/1, 300, 300, 1000, 1000, 1000, 300, 300, 300, 1000, 1000, 1000))

    relay = CurrentRelay(breaker=breaker, current_indexes=(1, 2, 3), current_threshold=1, time_threshold=5000) # 5000 = 0,5 c

    table_id = 1
    while True:
        try:
            measurement = tr.get_data()
            measurement.insert(0, table_id)
            db.add_row(measurement)
            table_id += 1
            relay.process(measurement)
        except StopIteration:
            print("COMTRADE is over!")
            break
