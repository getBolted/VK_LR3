from math import sqrt


def fourier(window: list) -> float:
    """
    :param window: список - окно, длиной в 1 ППЧ, по которому считается действующее значение
    :return: действующее значение сигнала по окну в 1 ППЧ
    """
    return sqrt(sum(m * m for m in window) / len(window))


def config_parser(config_lines: list) -> list:
    """
    Функция для парсинга конфигурациоонго файла COMTRADE
    :param config_lines: список строк конфигурационного файла
    :return: список кортежей поправочных коэффициентов (a, b) для каналов
    """
    channel_info = config_lines[1]  # Считаем информацию о каналах данных (1 строка из списка)
    analogue_channels = int(channel_info.split(',')[1][
                            :-1])  # Из строки вычленим количество аналоговых сигналов в записи и преобразуем в целое число

    coefs = list()
    for i in range(2, 2 + analogue_channels):  # опишем цикл, в котором сформируем словарь поправочных коэффициентов для каждого сигнала
        data = config_lines[i].split(',')
        coefs.append((float(data[5]), float(data[6])))

    return coefs


def signal_converter(data_lines: list, coefs: list) -> object:
    """
    Функция для преобразования "сырых" данных из .dat файлов в мгновенные значения токов и напряжений при помощи
    коэффициентов a,b из .cfg файла
    :param data_lines: список "сырых" данных из .dat файла
    :param coefs: список коэффициентов a,b для каждого сигнала после преобразования в функции config_parser
    :return: объект класса Signals, содержащий списки сигналов мгновенных значений и список меток времени
    """

    # создадим словарь: ключ - название сигнала, значение - пустой список + список для отсчета времени с ключом "time"
    kwargs = dict()
    kwargs["time"] = list()
    for i in range(len(coefs)):
        kwargs[f'signal_{i}'] = list()

    for data_line in data_lines:
        parsed_line = data_line.split(',')  # распарсим строку на список элементов по символу ","
        kwargs["time"].append(int(parsed_line[1]))  # добавим метку времени из текущей строки
        for i in range(2,
                       len(parsed_line)):  # добавим все сигналы из текущей строки, преобразовав значения по формуле aX + b
            kwargs[f'signal_{i - 2}'].append(int(parsed_line[i]) * coefs[i - 2][0] + coefs[i - 2][1])
    return Signals(**kwargs)


def _get_signal_generator(values) -> object:
    """
    Метод, создающий генератор для доступа к данным из списка кортежей измерений по одному измерению за обращение next
    :return:
    """
    for value in values:
        yield value # возвращает следующий кортеж с измерениями, начиная с нулевого в списке, при обращении через next
        # Выбрасывает исключение StopIteration, когда в списке нет больше данных


class Signals:
    """
    Класс-контейнер, куда скалдываются списки всех значений токов и напряжений из COMTRADE, а также их производные
    """

    def __init__(self, **kwargs):
        """
        Конструктор класса-контейнера, преобразует входной словарь сигналов в атрибуты класса
        :param kwargs: словарь (ключ - название сигнала, значение - список значений сигнала)
        """
        for attr in kwargs.keys():
            self.__dict__[attr] = kwargs[attr]

    def _calculate_rms(self):
        """
        Метод для рассчета действующих значений всех сигналов
        """
        signal_names = [x for x in self.__dict__.keys() if
                        'signal_' in x]  # достаем из словаря атрибутов класса все названия с "signal_"
        for attr in signal_names:
            signal = getattr(self, attr)  # достаем значение атрибута
            left = 0  # задаем начальную и конечную границы окна для фильтра Фурье
            right = 100
            rms_signal_name = attr + "_rms"  # задаем имя для новго атрибута сигнала
            setattr(self, rms_signal_name,
                    [0 for _ in range(100)])  # инициализируем новый атрибут 100 нулевыми значениями
            while right != len(signal):
                getattr(self, rms_signal_name).append(
                    fourier(signal[left:right]))  # считаем значение по окну и добавляем в атрибут
                left += 1
                right += 1

    def _transform_for_gen(self) -> list:
        """
        Метод для преобразования атрибутов классов в список кортежей
        :return: список кортежей по числу измерений в .dat файле
        """
        values = list() # создаем пустой список, который будем возвращать
        for i in range(len(self.time)): # цикл по кол-ву элементов
            row = list() # создаем пустой список под каждое измерение
            for attr_key, attr_value in self.__dict__.items(): # цикл по атрибутам класса
                if 'time' in attr_key or 'rms' in attr_key: # если в названии атрибута есть time или rms
                    row.append(attr_value[i]) # добавляем в список-строчку
            values.append(tuple(row)) # преобразуем в список-строчку в кортеж и добавляем в итоговый список
        return values

    def prepare(self) -> object:
        """
        Метод, в котором производятся все базовые преобразования и из сырых данных .dat-файла получается генератор,
        "выплевывающий" кортежи с измерениями
        :return: генератор, который возвращает кортежи измерений действующих значений сигналов
        """
        self._calculate_rms()
        values = self._transform_for_gen()
        return _get_signal_generator(values)
