#!/usr/bin/env python3
"""
Лабораторная работа №4
Вариант 7: (n|<b|d>)(h|k)<z|m>c

Конечный автомат Мили для проверки входного слова
"""


class MealyAutomaton:
    """
    Класс, реализующий конечный автомат Мили
    """

    def __init__(self):
        """
        Инициализация автомата
        """
        # Определение алфавитов
        self.input_alphabet = {'n', 'b', 'd', 'h', 'k', 'z', 'm', 'c'}
        self.output_alphabet = {'0', '1'}
        self.states = {'q0', 'q1', 'q2', 'q3', 'qf', 'qe'}
        self.initial_state = 'q0'
        self.final_state = 'qf'
        self.error_state = 'qe'

        # Текущее состояние
        self.current_state = self.initial_state

        # Определение функций переходов (δ) и выходов (λ)
        # Формат: transitions[(state, symbol)] = (next_state, output)
        self.transitions = self._build_transitions()

        # История переходов для трассировки
        self.trace = []

    def _build_transitions(self):
        """
        Построение таблицы переходов автомата Мили

        Регулярное выражение: (n|<b|d>)(h|k)<z|m>c

        Состояния:
        - q0: начальное состояние
        - q1: прочитали символ из (n|b|d)
        - q2: прочитали символ из (h|k)
        - q3: прочитали символ из <z|m>
        - qf: конечное состояние (прочитали c)
        - qe: состояние ошибки
        """
        trans = {}

        # Из q0 (начальное состояние)
        trans[('q0', 'n')] = ('q1', '0')  # Прочитали n
        trans[('q0', 'b')] = ('q1', '0')  # Прочитали b
        trans[('q0', 'd')] = ('q1', '0')  # Прочитали d
        trans[('q0', 'h')] = ('q2', '0')  # Пропустили первую группу, сразу h
        trans[('q0', 'k')] = ('q2', '0')  # Пропустили первую группу, сразу k

        # Из q1 (прочитали n, b или d)
        trans[('q1', 'h')] = ('q2', '0')  # Прочитали h
        trans[('q1', 'k')] = ('q2', '0')  # Прочитали k

        # Из q2 (прочитали h или k)
        trans[('q2', 'z')] = ('q3', '0')  # Прочитали z
        trans[('q2', 'm')] = ('q3', '0')  # Прочитали m
        trans[('q2', 'c')] = ('qf', '1')  # Пропустили <z|m>, сразу c - успех!

        # Из q3 (прочитали z или m)
        trans[('q3', 'c')] = ('qf', '1')  # Прочитали c - успех!

        # Из qf (конечное состояние) - любой символ ведет в ошибку
        for symbol in self.input_alphabet:
            trans[('qf', symbol)] = ('qe', '0')

        # Из qe (состояние ошибки) - остаемся в ошибке
        for symbol in self.input_alphabet:
            trans[('qe', symbol)] = ('qe', '0')

        return trans

    def reset(self):
        """
        Сброс автомата в начальное состояние
        """
        self.current_state = self.initial_state
        self.trace = []

    def step(self, symbol):
        """
        Выполнить один шаг автомата

        Args:
            symbol: входной символ

        Returns:
            Кортеж (следующее_состояние, выход)
        """
        if symbol not in self.input_alphabet:
            # Неизвестный символ - переходим в состояние ошибки
            next_state = self.error_state
            output = '0'
        else:
            # Ищем переход для текущего состояния и символа
            key = (self.current_state, symbol)
            if key in self.transitions:
                next_state, output = self.transitions[key]
            else:
                # Переход не определен - идем в состояние ошибки
                next_state = self.error_state
                output = '0'

        # Сохраняем трассировку
        self.trace.append({
            'state': self.current_state,
            'input': symbol,
            'next_state': next_state,
            'output': output
        })

        # Обновляем текущее состояние
        self.current_state = next_state

        return next_state, output

    def process(self, word):
        """
        Обработать входное слово

        Args:
            word: входное слово (строка)

        Returns:
            True, если слово допустимо, False иначе
        """
        self.reset()

        # Обрабатываем каждый символ
        for symbol in word:
            next_state, output = self.step(symbol)

        # Проверяем, что закончили в конечном состоянии
        return self.current_state == self.final_state

    def get_transition_matrix(self):
        """
        Получить матрицу переходов Δ

        Returns:
            Словарь с матрицей переходов
        """
        matrix = {}
        for state in sorted(self.states):
            matrix[state] = {}
            for symbol in sorted(self.input_alphabet):
                key = (state, symbol)
                if key in self.transitions:
                    next_state, _ = self.transitions[key]
                    matrix[state][symbol] = next_state
                else:
                    matrix[state][symbol] = self.error_state
        return matrix

    def get_output_matrix(self):
        """
        Получить матрицу выходов Λ

        Returns:
            Словарь с матрицей выходов
        """
        matrix = {}
        for state in sorted(self.states):
            matrix[state] = {}
            for symbol in sorted(self.input_alphabet):
                key = (state, symbol)
                if key in self.transitions:
                    _, output = self.transitions[key]
                    matrix[state][symbol] = output
                else:
                    matrix[state][symbol] = '0'
        return matrix

    def print_trace(self):
        """
        Вывести трассировку выполнения
        """
        print("\nТрассировка выполнения:")
        print(f"{'Состояние':<12} {'Вход':<8} {'След. состояние':<18} {'Выход':<8}")

        for step in self.trace:
            print(f"{step['state']:<12} {step['input']:<8} "
                  f"{step['next_state']:<18} {step['output']:<8}")

        print("-" * 60)


def test_automaton():
    """
    Тестирование автомата на различных входных словах
    """
    automaton = MealyAutomaton()

    # Тестовые примеры
    test_words = [
        # Допустимые слова
        'nhc', 'nkc', 'nhzc', 'nkzc', 'nhmc', 'nkmc',
        'bhc', 'bkc', 'bhzc', 'bkzc', 'bhmc', 'bkmc',
        'dhc', 'dkc', 'dhzc', 'dkzc', 'dhmc', 'dkmc',
        'hc', 'kc', 'hzc', 'kzc', 'hmc', 'kmc',
        # Недопустимые слова
        'nc', 'abc', 'nh', 'nk', 'nhcc', 'xyz', 'h', 'k',
        'nhhc', 'nkk', 'nzc', 'nmc'
    ]

    print("Тестирование конечного автомата Мили")
    print("Вариант 7: (n|<b|d>)(h|k)<z|m>c")
    print()

    for word in test_words:
        result = automaton.process(word)
        status = "ДОПУСТИМО" if result else "ОТКЛОНЕНО"
        print(f"Слово: '{word}'".ljust(20) + f" -> {status}")

    # Детальная трассировка для одного примера
    print("Детальная трассировка для слова 'nhzc':")
    automaton.reset()
    result = automaton.process('nhzc')
    automaton.print_trace()
    print(f"\nРезультат: {'ДОПУСТИМО' if result else 'ОТКЛОНЕНО'}")
    print(f"Конечное состояние: {automaton.current_state}")


def main():
    """
    Главная функция программы
    """
    test_automaton()

    # Интерактивный режим
    print("Интерактивный режим")
    print("Введите слово для проверки (или 'exit' для выхода):")

    automaton = MealyAutomaton()

    while True:
        try:
            word = input("\nСлово: ").strip()
            if word.lower() == 'exit':
                break

            if not word:
                continue

            result = automaton.process(word)
            automaton.print_trace()

            if result:
                print(f"\nСлово '{word}' ДОПУСТИМО")
            else:
                print(f"\nСлово '{word}' ОТКЛОНЕНО")

            print(f"Конечное состояние: {automaton.current_state}")

        except KeyboardInterrupt:
            print("\n\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
