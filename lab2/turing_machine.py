#!/usr/bin/env python3
"""
Лабораторная работа №2
Вариант 21: f(x₁, x₂) = x₁ + x₂ - 1

Симулятор машины Тьюринга
"""

import sys
from typing import List, Dict, Tuple, Optional


class TuringMachine:
    """
    Класс, реализующий симулятор машины Тьюринга
    """

    def __init__(self, alphabet: List[str], program: List[str], tape: str):
        """
        Инициализация машины Тьюринга

        Args:
            alphabet: внешний алфавит машины
            program: список команд программы
            tape: начальное состояние ленты
        """
        # Добавляем пустой символ в алфавит, если его там нет
        self.alphabet = set(alphabet)
        if 'λ' not in self.alphabet:
            self.alphabet.add('λ')

        # Проверяем символы на ленте
        for symbol in tape:
            if symbol not in self.alphabet:
                raise ValueError(f"Символ '{symbol}' не принадлежит алфавиту {sorted(self.alphabet)}")

        self.tape = list(tape)
        self.head_position = 0
        self.current_state = 'q0'
        self.final_state = 'qz'
        self.transitions = {}  # Таблица переходов
        self.trace = []  # Трассировка выполнения

        # Парсинг программы
        self._parse_program(program)

    def _parse_program(self, program: List[str]):
        """
        Парсинг программы машины Тьюринга

        Формат команды: qi aj -> qi' aj' dk
        где:
            qi - текущее состояние
            aj - текущий символ
            qi' - новое состояние
            aj' - символ для записи
            dk - направление движения (L, R, E)
        """
        for line in program:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                # Разбираем команду: q0 1 -> q1 1 R
                parts = line.split('->')
                if len(parts) != 2:
                    raise ValueError(f"Неверный формат команды: {line}")

                left = parts[0].strip().split()
                right = parts[1].strip().split()

                if len(left) != 2 or len(right) != 3:
                    raise ValueError(f"Неверный формат команды: {line}")

                current_state = left[0]
                current_symbol = left[1]
                new_state = right[0]
                new_symbol = right[1]
                direction = right[2]

                if direction not in ['L', 'R', 'E']:
                    raise ValueError(f"Неверное направление: {direction}")

                # Проверяем, что символы принадлежат алфавиту
                if current_symbol not in self.alphabet:
                    raise ValueError(
                        f"Символ '{current_symbol}' в команде '{line}' "
                        f"не принадлежит алфавиту {sorted(self.alphabet)}"
                    )
                if new_symbol not in self.alphabet:
                    raise ValueError(
                        f"Символ '{new_symbol}' в команде '{line}' "
                        f"не принадлежит алфавиту {sorted(self.alphabet)}"
                    )

                # Сохраняем переход
                self.transitions[(current_state, current_symbol)] = (
                    new_state, new_symbol, direction
                )

            except Exception as e:
                print(f"Ошибка при парсинге команды '{line}': {e}")
                raise

    def _get_current_symbol(self) -> str:
        """
        Получить символ под головкой

        Returns:
            Символ под головкой
        """
        self._ensure_tape_bounds()
        return self.tape[self.head_position]

    def _ensure_tape_bounds(self):
        """
        Обеспечить корректные границы ленты для текущей позиции головки
        """
        # Расширяем ленту вправо
        while self.head_position >= len(self.tape):
            self.tape.append('λ')

        # Расширяем ленту влево
        while self.head_position < 0:
            self.tape.insert(0, 'λ')
            self.head_position += 1

    def _write_symbol(self, symbol: str):
        """
        Записать символ в текущую позицию

        Args:
            symbol: символ для записи
        """
        self._ensure_tape_bounds()
        self.tape[self.head_position] = symbol

    def _move_head(self, direction: str):
        """
        Переместить головку

        Args:
            direction: направление (L - влево, R - вправо, E - на месте)
        """
        if direction == 'L':
            self.head_position -= 1
        elif direction == 'R':
            self.head_position += 1
        # E - остаемся на месте

    def _tape_to_string(self) -> str:
        """
        Преобразовать ленту в строку, убирая концевые _

        Returns:
            Строковое представление ленты
        """
        # Убираем _ с концов
        tape_str = ''.join(self.tape).strip('λ')
        return tape_str if tape_str else 'λ'

    def _format_tape_with_head(self) -> Tuple[str, str]:
        """
        Форматировать ленту с указателем головки

        Returns:
            Кортеж (лента, позиция головки)
        """
        # Находим левую и правую границы значимой части ленты
        # Значимая часть включает все непустые символы и позицию головки
        left_bound = 0
        right_bound = len(self.tape) - 1

        # Находим первый непустой символ слева
        for i in range(len(self.tape)):
            if self.tape[i] != 'λ':
                left_bound = i
                break
        else:
            # Если лента полностью пустая
            left_bound = self.head_position

        # Находим последний непустой символ справа
        for i in range(len(self.tape) - 1, -1, -1):
            if self.tape[i] != 'λ':
                right_bound = i
                break
        else:
            # Если лента полностью пустая
            right_bound = self.head_position

        # Расширяем границы, чтобы включить позицию головки
        left_bound = min(left_bound, self.head_position)
        right_bound = max(right_bound, self.head_position)

        # Формируем строку ленты в этих границах
        tape_str = ''.join(self.tape[left_bound:right_bound + 1])

        # Вычисляем позицию указателя относительно начала отображаемой части
        pointer_pos = self.head_position - left_bound
        pointer = ' ' * pointer_pos + '^'

        return tape_str, pointer

    def step(self) -> bool:
        """
        Выполнить один шаг машины Тьюринга

        Returns:
            True, если шаг выполнен успешно, False, если машина остановлена
        """
        # Проверяем, не в конечном ли состоянии
        if self.current_state == self.final_state:
            return False

        current_symbol = self._get_current_symbol()

        # Ищем подходящую команду
        key = (self.current_state, current_symbol)
        if key not in self.transitions:
            raise RuntimeError(
                f"Не найден переход для состояния '{self.current_state}' "
                f"и символа '{current_symbol}'"
            )

        new_state, new_symbol, direction = self.transitions[key]

        # Записываем трассировку ДО выполнения команды
        tape_str, pointer = self._format_tape_with_head()
        command = f"{self.current_state} {current_symbol} -> {new_state} {new_symbol} {direction}"

        self.trace.append({
            'tape': tape_str,
            'pointer': pointer,
            'command': command
        })

        # Выполняем команду
        self._write_symbol(new_symbol)
        self.current_state = new_state
        self._move_head(direction)

        return True

    def run(self, max_steps: int = 10000) -> str:
        """
        Запустить машину Тьюринга

        Args:
            max_steps: максимальное количество шагов (защита от зацикливания)

        Returns:
            Результат работы (содержимое ленты)
        """
        steps = 0

        try:
            while self.current_state != self.final_state and steps < max_steps:
                self.step()
                steps += 1

            if steps >= max_steps:
                raise RuntimeError("Превышено максимальное количество шагов. Возможно зацикливание.")

            # Добавляем финальное состояние ленты
            tape_str, pointer = self._format_tape_with_head()
            self.trace.append({
                'tape': tape_str,
                'pointer': pointer,
                'command': f'Конечное состояние: {self.final_state}'
            })

            return self._tape_to_string()

        except Exception as e:
            raise RuntimeError(f"Ошибка выполнения: {e}")

    def get_trace(self) -> List[Dict]:
        """
        Получить трассировку выполнения

        Returns:
            Список шагов выполнения
        """
        return self.trace


def read_file_lines(filename: str) -> List[str]:
    """
    Прочитать строки из файла

    Args:
        filename: имя файла

    Returns:
        Список строк
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла '{filename}': {e}")
        sys.exit(1)


def write_trace_to_file(filename: str, trace: List[Dict]):
    """
    Записать трассировку в файл

    Args:
        filename: имя выходного файла
        trace: трассировка выполнения
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("Трассировка работы машины Тьюринга\n")
            f.write("Вариант 21: f(x₁, x₂) = x₁ + x₂ - 1\n")
            f.write("=" * 70 + "\n\n")

            for i, step in enumerate(trace):
                f.write(f"Шаг {i}:\n")
                f.write(f"{step['tape']}\n")
                f.write(f"{step['pointer']}\n")
                f.write(f"Команда: {step['command']}\n")
                f.write("\n")

            f.write("=" * 70 + "\n")
            f.write("Работа машины Тьюринга завершена успешно\n")
            f.write("=" * 70 + "\n")

    except Exception as e:
        print(f"Ошибка при записи в файл '{filename}': {e}")
        sys.exit(1)


def main():
    """
    Главная функция программы
    """
    # Читаем входные данные
    print("Чтение входных данных...")
    alphabet_lines = read_file_lines('alphabet.txt')
    alphabet = alphabet_lines[0].split()
    print(f"Внешний алфавит: {alphabet}")

    program = read_file_lines('program.txt')
    print(f"Программа: {len(program)} команд")

    tape_lines = read_file_lines('tape.txt')
    initial_tape = tape_lines[0]
    print(f"Начальная лента: {initial_tape}")
    print()

    # Создаем и запускаем машину Тьюринга
    print("Запуск машины Тьюринга...")
    try:
        tm = TuringMachine(alphabet, program, initial_tape)
        result = tm.run()

        print("Машина Тьюринга завершила работу успешно!")
        print(f"Результат: {result}")
        print()

        # Записываем трассировку в файл
        output_file = 'output.txt'
        write_trace_to_file(output_file, tm.get_trace())
        print(f"Трассировка записана в файл '{output_file}'")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
