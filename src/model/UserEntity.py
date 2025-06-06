import datetime
import uuid
import flask_login
import werkzeug.security as safe


class UserEntity(flask_login.UserMixin):
    def __init__(self, name, email, password, country, username=None, language='es', timezone='Europe/Madrid'):
        self._id = str(uuid.uuid4()) # Usado como user ID para flask login manager, único e incambiable.
        self.name = name
        self.email = email
        self._password = safe.generate_password_hash(password)
        self.country = country
        self.username = username
        self.language = language
        self.timezone = timezone
        self.bio = "" 
        self.created_at = datetime.datetime.now()
        self.last_login = None

    def key(self):
        return self.id
    
    @property
    def id(self):
        return self._id
    
    @property
    def oid(self):
        return self.__oid__
    
    def get_safe_oid(self, srp):
        oid = getattr(self, "__oid__", None)
        return srp.safe_from_oid(oid) if oid else None
    
    def get_created_at(self):
        return self.created_at.strftime("%d/%m/%Y")

    def get_last_login(self):
        if self.last_login:
            return self.last_login.strftime("%d/%m/%Y %H:%M")
        return "Nunca"
    
    def check_password(self,input_password):
        return safe.check_password_hash(self._password, input_password)
    
    def set_last_login_now(self):
        self.last_login = datetime.datetime.now()

    def __eq__(self, other):
        return isinstance(other, UserEntity) and self.email == other.email

    def __hash__(self):
        return hash(self.email)

    @staticmethod
    def find(srp, id):
         return srp.find_first(UserEntity, lambda u: u.id == id)
    
    @staticmethod
    def find_by_mail(srp, email):
         return srp.find_first(UserEntity, lambda u: u.email == email)

    @staticmethod
    def create(srp, name, email, password, country, username, language, timezone):
        if UserEntity.find_by_mail(srp, email):
            return None  # Ya existe
        user = UserEntity(name, email, password, country, username, language, timezone)
        srp.save(user)
        return user
