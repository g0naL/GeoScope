import uuid
import flask_login
import werkzeug.security as safe


class UserEntity(flask_login.UserMixin):
    def __init__(self, name, email, password, country):
        self.id = str(uuid.uuid4()) # Usado como user ID para flask login manager, único e incambiable.
        self.name = name
        self.email = email
        self.password = safe.generate_password_hash(password)
        self.country = country

    def key(self):
        return self.id
    
    @property
    def id(self):
        return self.id
    
    @property
    def oid(self):
        return self.__oid__
    
    @property
    def safe_oid(self, srp):
        return srp.safe_from_oid(self.__oid__)

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
    def create(srp, name, email, password, country):
        if UserEntity.find_by_mail(srp, email):
            return None  # Ya existe
        user = UserEntity(name, email, password, country)
        srp.save(user)
        return user
