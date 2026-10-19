import os
import secrets

from models.active_record_entity import ActiveRecordentity
from models.user import User
from exceptions import InvalidArgumentException

ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024


class Article(ActiveRecordentity):
    _name = None
    _text = None
    _create_at = None
    _author_id = None
    _img = None
    # --- getters ---

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

    # --- setters ---

    def set_author_id(self, author_id):
        self._author_id = author_id

    def set_name(self, name):
        self._name = name

    def set_text(self, text):
        self._text = text

    # --- table ---

    @staticmethod
    def get_table_name():
        return 'articles'

    # --- file helpers ---

    @staticmethod
    def check_file_size(file_item, max_size):
        """
        Проверка размера файла без загрузки всего файла в память.
        Читает файл по частям и суммирует их размер.
        """
        if file_item is None or not hasattr(file_item, 'file'):
            return False, 0

        total_size = 0
        chunk_size = 8192

        current_pos = file_item.file.tell()

        try:
            file_item.file.seek(0)
            while True:
                chunk = file_item.file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_size:
                    break
        finally:
            file_item.file.seek(current_pos)

        return total_size <= max_size, total_size

    # --- CRUD ---

    @staticmethod
    def create(fields, img_file, author):
        if not fields.get('name'):
            raise InvalidArgumentException('не передано название статьи')

        if not fields.get('text'):
            raise InvalidArgumentException('не передан текст статьи')

        if img_file is None:
            raise InvalidArgumentException('не передана картинка')

        if not Article.check_file_size(img_file, MAX_FILE_SIZE)[0]:
            raise InvalidArgumentException('Слишком большой файл! Должно быть не более 5МБ')

        original_name = img_file.filename or ''
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in ALLOWED_EXT:
            raise InvalidArgumentException('Недопустимый тип файла')

        article = Article()
        article._name = fields['name']
        article._text = fields['text']
        article._author_id = author.get_id()

        if original_name:
            safe_name = secrets.token_hex(16) + ext
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', safe_name)

            with open(file_path, 'wb') as f:
                while True:
                    chunk = img_file.file.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

            article._img = 'uploads/' + safe_name

        article.save()
        return article

    @staticmethod
    def search_by_name(search_string):
        return Article.search('name', search_string)
