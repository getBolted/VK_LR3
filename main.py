from signals import signal_converter, config_parser
from transformer import Transformer
from breaker import CircuitBreaker
from current_relay import CurrentRelay
import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('A3_in.dat', 'r') as dat:
        dat_line_list = dat.readlines()
    with open('A3_in.cfg', 'r') as cfg:
        coef_line_list = cfg.readlines()

    coefs = config_parser(coef_line_list)
    signals = signal_converter(dat_line_list, coefs)
    gen = signals.prepare()

    breaker = CircuitBreaker("CB1")
    breaker.turn_on()

    tr = Transformer(signal_gen=gen, cb=breaker, transform_rates=(300/1, 300, 300, 1000, 1000, 1000, 300, 300, 300, 1000, 1000, 1000))

    relay = CurrentRelay(breaker=breaker, current_indexes=(1, 2, 3), current_threshold=1, time_threshold=5000) # 5000 = 0,5 c

    time = list()
    Ia = list()
    Ib = list()
    Ic = list()
    breaker_state = list()

    while True:
        try:
            measurement = tr.get_data()
            relay.process(measurement)
            time.append(measurement[0])
            Ia.append(measurement[1])
            Ib.append(measurement[2])
            Ic.append(measurement[3])
            breaker_state.append(relay.breaker.get_state())
        except StopIteration:
            print("COMTRADE is over!")
            break

    fig = plt.figure(figsize=(10, 10)) # создаем объект для графиков с размером полотна

    ax1 = fig.add_subplot(211) # добавляем 1 подграфик
    ax1.set_title('Действующее значение фазных токов на ТТ') # добавляем название подграфика
    ax2 = fig.add_subplot(212)
    ax2.set_title('Положение силового выключателя (1 - замкнут, 0 - разомкнут)')

    ax1.plot(time, Ia, 'y') # задаем первую функуию - ток Ia, цвет y(=yellow)
    ax1.plot(time, Ib, 'g')
    ax1.plot(time, Ic, 'r')
    ax1.set_ylabel('Ток, А') # задаем название оси х
    ax1.set_xlabel('Время, с') # задаем название оси y

    ax2.plot(time, breaker_state)
    ax2.set_ylabel('Положение')
    ax2.set_xlabel('Время, с')

    plt.show() # выводим график
