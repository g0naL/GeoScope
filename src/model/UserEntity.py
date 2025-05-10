import flask_login
import werkzeug.security as safe


class UserEntity(flask_login.UserMixin):
    def __init__(self, name, email, password, country):
        self.name = name
        self.email = email
        self.password = safe.generate_password_hash(password)
        self.country = country

    def key(self):
        return self.email

    def __eq__(self, other):
        return isinstance(other, UserEntity) and self.email == other.email

    def __hash__(self):
        return hash(self.email)

    @staticmethod
    def find(srp, email):
         return srp.find_first(UserEntity, lambda u: u.email == email)

    @staticmethod
    def create(srp, name, email, password, country):
        if UserEntity.find(srp, email):
            return None  # Ya existe
        user = UserEntity(name, email, password, country)
        srp.save(user)
        return user
