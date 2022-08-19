# ---------------------------------------------------------------------
# Класс FileRead, при создании экземпляра считывает файл по указанному пути.
# Каждый экземпляр класса имеет поле data (лист с данными из считанного файла)
# Метод read считывает файл построчно, поэтому данные в файле должны быть разбиты в столбик
#
# Поля класса:
# file_path - String, путь до файла
# data - list, лист с данными из файла
# ---------------------------------------------------------------------
import os.path


class FileRead:

    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        self.__data = self.__read(self.file_path)

    # Геттер - возвращает путь до файла из поля file_path
    @property
    def file_path(self) -> str:
        return self.__file_path

    # Геттер - возвращает лист с данными из файла
    @property
    def data(self) -> list:
        return self.__data

    # Метод для чтения построчно из файла.
    # Проверяет существует ли файл, если его нет, то генерируется ошибка FileNotFoundError.
    # возвращает лист с данными
    def __read(self, file_path: str) -> list:
        if os.path.exists(file_path):
            try:
                with open(file_path, encoding='utf-8') as f:
                    text = f.read().split('\n')
                data = [s for s in text]
                return data
            except Exception as err:
                raise err
        else:
            raise FileNotFoundError("Не найден указанный файл!")
