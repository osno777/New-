from models.active_record_entity import ActiveRecordentity
from models.user import User
from exceptions import InvalidArgumentException
import os

MAX_FILE_SIZE = 5 * 1024 * 1024


class Article(ActiveRecordentity):
    _name = None
    _text = None
    _create_at = None
    _author_id = None

    def get_name(self):
        return self._name

    def get_img(self):
        return getattr(self, '_img', None)
    
    def get_author_id(self):
        return self._author_id

    def get_author(self):
        return User.get_by_id(self._author_id)

    def get_text(self):
        return self._text

    def get_create_at(self):
        return self._create_at

    def set_author_id(self, author_id):
        self._author_id = author_id

    def set_name(self, name):
        self._name = name

    def set_text(self, text):
        self._text = text

    @staticmethod
    def get_table_name():
        return 'articles'

    @staticmethod
    def create(fields, img_file, author):
        if not fields['name']:
            raise InvalidArgumentException('не передано название статьи')

        if not fields['text']:
            raise InvalidArgumentException('не передан текст статьи')

        if not Article.check_file_size(img_file, MAX_FILE_SIZE)[0]:
            raise InvalidArgumentException('Слишком большой файл! Должно быть не более 5МБ')

        article = Article()
        article._name = fields['name']
        article._text = fields['text']
        article._author_id = author.get_id()

        if img_file.filename:
            file_path = 'uploads/' + img_file.filename
            article._img = file_path
            os.makedirs('uploads', exist_ok=True)

            with open(file_path, 'wb') as f:
                while True:
                    chunk = img_file.file.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

        article.save()
        return article

    @staticmethod
    def check_file_size(file_item, max_size):
        """
        Проверка размера файла без загрузки всего файла в память.
        Читает файл по частям и суммирует их размер.
        """
        total_size = 0
        chunk_size = 8192  # Читаем по 8KB

        # Сохраняем текущую позицию, чтобы потом вернуться
        current_pos = file_item.file.tell()

        try:
            # Перемещаемся в начало файла
            file_item.file.seek(0)

            # Читаем файл по частям и суммируем размер
            while True:
                chunk = file_item.file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)

                # Если уже превысили лимит, можно прервать проверку
                if total_size > max_size:
                    break
        finally:
            # Возвращаемся на исходную позицию для последующего чтения
            file_item.file.seek(current_pos)

        print(total_size)
        return total_size <= max_size, total_size

    @staticmethod
    def search_by_name(search_string):
        return __class__.search('name', search_string)
    

