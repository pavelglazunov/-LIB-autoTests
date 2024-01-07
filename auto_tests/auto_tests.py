import subprocess
import sys
import time
import uuid
import inspect
import os

from auto_tests import formats


def _generate_file(current_data):
    stack = inspect.stack()

    caller_frame = stack[-1]
    call_file_path = os.path.abspath(caller_frame.filename)

    code = uuid.uuid1()

    with open(call_file_path) as call_file:
        call_file_content = call_file.read()
    call_file_content = f"""from builtins import input as base_input
class T:
    def __init__(self, data):
        self.data = data
        self.index = 0
    def __iter__(self):
        self.index = 0
        return self.data[self.index]
    def __next__(self):
        value = self.data[self.index]
        self.index += 1
        return value
t = T({current_data})
def input():
    return next(t)
""" + call_file_content
    call_file_content = "def _(*args, **kwargs): pass\n" + call_file_content

    call_file_content = call_file_content.replace("auto_tests", "os")
    call_file_content = call_file_content.replace("set_tests", "_")

    with open(f"{code}.py", "w") as exec_file:
        exec_file.write(call_file_content)

    return os.path.join(os.getcwd(), f"{code}.py")


def _compare_answer(test_answer: str, correct_answer: str) -> bool:
    if correct_answer is None:
        return True
    return test_answer.strip("\n").strip() == correct_answer.strip("\n").strip()


def _run_code(test: formats.Test, test_id: int, add_timer: bool):
    test_data = test.data
    test_answer = test.answer

    new_file_path = _generate_file(test_data)

    start_time = time.time()
    result = subprocess.run(["python", new_file_path], capture_output=True, text=True)
    end_time = time.time()

    exec_time = f"{format(end_time - start_time, '.6f')} ms" if add_timer else ""
    test_completed = True
    if result.stderr:
        status = "*"
    else:
        status = "+" if (test_completed := _compare_answer(result.stdout, test_answer)) else "-"

    if result.stderr:
        print(f"[{status}] [test {test_id}] [{exec_time}] failed (executable error)")
        print(result.stderr)
    elif test_answer is None:
        print(f"[{status}] [test {test_id}] [{exec_time}] finished")
        print(result.stdout)
    else:
        if test_completed:
            print(f"[{status}] [test {test_id}] [{exec_time}] completed")
            # print(result.stdout)
        else:
            print(f"[{status}] [test {test_id}] [{exec_time}] failed (incorrect answer)")
            print("program output:")
            print(result.stdout)
            print("correct answer:")
            print(test_answer)
    os.remove(new_file_path)


def _to_format(data) -> tuple[formats.Format, formats.Format]:
    if isinstance(data, list) or isinstance(data, tuple):
        return formats.Array(data), formats.NullAnswer()
    elif isinstance(data, str):
        if data.startswith("file:"):
            return formats.File(data), formats.NullAnswer()
        else:
            return formats.String(data), formats.NullAnswer()
    elif isinstance(data, dict):
        d = list(data.keys())[0]
        a = data[d]
        return _to_format(d)[0], _to_format(a)[0]
    return formats.NoFormat(), formats.NullAnswer()


def set_tests(*input_tests: dict | list | str | tuple, add_timer: bool = False):
    """
    Функция принимает тесты, переданные как отдельные аргументы.
    Каждый тест может быть в любом из трех форматах:
        - строка в тройных кавычках, где на каждой строке записаны входные данные.
        - список: [line1, line2], где line1 и line2 - строки со входными данными одного теста.
        - файл: строка с названием файла в формате - "file:filename.txt".

    :param input_tests: неограниченное количество тестов в любом из форматов.
    :param add_timer: добавить замер времени на выполнение каждого теста.
    :return:
    """
    tests: [formats.Test] = []
    for test_data in input_tests:

        formatted_test, formatted_answer = _to_format(test_data)
        if isinstance(formatted_test, formats.NoFormat) or isinstance(formatted_answer, formats.NoFormat):
            print(f"[пропущен] Неверный формат теста или ответа: {test_data}")
            continue

        t = formats.Test(
            data=formatted_test.before_use_test(),
            answer=formatted_answer.before_use_answer()
        )

        tests.append(t)

    for t_id, test in enumerate(tests):
        _run_code(test, t_id, add_timer)

    sys.exit()
