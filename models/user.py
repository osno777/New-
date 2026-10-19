import re
import hashlib
import random

from models.active_record_entity import ActiveRecordentity
from exceptions import InvalidArgumentException
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash


class User(ActiveRecordentity):
   _nickname = None
   _email = None
   _is_confirmed = None
   _author_id = None
   _role = None
   _password_hash = None
   _auth_token = None
   _created_at = None

   def get_nickname(self):
      return self._nickname

   def get_author_id(self):
      return self._author_id
   
   def get_email(self):
      return self._email

   def get_create_at(self):
      return self._create_at
   
   def get_role(self):
      return self._role

   def get_password_hash(self):
      return self._password_hash

   def get_auth_token(self):
      return self._auth_token


   def set_author_id(self,author_id):
      self._author_id = author_id
      
   def set_nickname(self,nickname):
      self._nickname = nickname

   def set_email(self,email):
      self._text = email
   
   def set_role(self,role):
      self._text = role

   def refresh_auth_token(self):
      self._auth_token = hashlib.sha1(random.randbytes(100)).hexdigest() + hashlib.sha1(random.randbytes(100)).hexdigest()


   @staticmethod
   def sign_up(user_data):
      if not user_data['nickname']:
         raise InvalidArgumentException('Не передан логин')

      if re.search(r'^[a-zA-Z0-9]+$', user_data['nickname']) is None :
         raise InvalidArgumentException('Логин может состоять только из символов латинского алфавита и цифр')

      if __class__.find_one_by_column('nickname',user_data['nickname']):
         raise InvalidArgumentException('Логин существует')

      if not user_data['email']:
         raise InvalidArgumentException('Не передан email')
      try:
         validate_email(user_data['email'])
      except EmailNotValidError as e:
         raise InvalidArgumentException('email некорректен')
      
      if __class__.find_one_by_column('email',user_data['email']):
         raise InvalidArgumentException('Email существует')


      if not user_data['password']:
         raise InvalidArgumentException('Не передан password')   

      if len(user_data['password']) < 8:
         raise InvalidArgumentException('Пароль должен быть не мнеее 8 символов')


      user = User()
      user._nickname = user_data['nickname']
      user._email = user_data['email']
      user._is_confirmed = True
      user._role = 'user'

      user._password_hash = generate_password_hash(user_data['password'])
      user.refresh_auth_token()
      user.save()
      return user

   @staticmethod
   def sign_in(user_data):
      if not user_data['nickname']:
         raise InvalidArgumentException('Не передан логин')

      if not user_data['password']:
         raise InvalidArgumentException('Не передан password')   

      user = User.find_one_by_column('nickname', user_data['nickname'])

      if user is None:
         raise InvalidArgumentException('Неверный логин или пароль')
      
      if check_password_hash(user_data['password'],user.get_password_hash):
         raise InvalidArgumentException('Неверный логин или пароль')

      user.refresh_auth_token()
      user.save()
      return user
      



   
   @staticmethod
   def get_table_name():
      return 'user'
