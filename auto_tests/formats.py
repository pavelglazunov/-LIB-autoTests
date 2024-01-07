from abc import ABC, abstractmethod


class Format(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def before_use_test(self) -> list[str]:
        pass

    @abstractmethod
    def before_use_answer(self) -> str:
        pass


class String(Format):
    def __init__(self, data):
        super().__init__(data)

    def before_use_test(self) -> list[str]:
        return self.data.strip("\n").strip().split("\n")

    def before_use_answer(self) -> str:
        return self.data.strip("\n").strip()


class Array(Format):
    def __init__(self, data):
        super().__init__(data)

    def before_use_test(self) -> list[str]:
        return self.data

    def before_use_answer(self) -> str:
        return "\n".join(self.data)


class File(Format):
    def __init__(self, data):
        super().__init__(data)

    def before_use_test(self) -> list[str]:
        filename = self.data.split("file:")[1]

        with open(filename) as file:
            return file.read().strip("\n").strip().split("\n")

    def before_use_answer(self) -> str:
        filename = self.data.split("file:")[1]
        with open(filename) as file:
            return file.read().strip("\n").strip()


class NullAnswer(Format):
    def __init__(self, data=None):
        super(NullAnswer, self).__init__(data)

    def before_use_test(self) -> list[str]:
        pass

    def before_use_answer(self) -> str | None:
        return None


class NoFormat(Format):
    def __init__(self, data=None):
        super().__init__(data)

    def before_use_test(self) -> list[str]:
        pass

    def before_use_answer(self) -> str:
        pass


class Test:
    def __init__(self, data: list[str], answer: str = None):
        self.data = data
        self.answer = answer
