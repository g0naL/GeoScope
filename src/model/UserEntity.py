import datetime
import uuid
import flask_login
import werkzeug.security as safe


class UserEntity(flask_login.UserMixin):
    """Entidad que representa a un usuario de la aplicación."""

    def __init__(self, name, email, password, country, username=None, language='es', timezone='Europe/Madrid'):
        """Inicializa un nuevo usuario con los datos proporcionados.

        :param name: Nombre completo del usuario.
        :param email: Correo electrónico único del usuario.
        :param password: Contraseña sin hashear.
        :param country: País de origen del usuario.
        :param username: Nombre de usuario único (opcional).
        :param language: Idioma preferido (por defecto 'es').
        :param timezone: Zona horaria (por defecto 'Europe/Madrid').
        """
        self._id = str(uuid.uuid4())
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
        """Devuelve el identificador único del usuario.

        :return: ID único del usuario.
        """
        return self.id

    @property
    def id(self):
        """ID accesible públicamente.

        :return: ID del usuario.
        """
        return self._id

    @property
    def oid(self):
        """Devuelve el OID interno asignado por Sirope.

        :return: OID del objeto.
        """
        return self.__oid__

    def get_safe_oid(self, srp):
        """Devuelve el OID seguro para la URL, usando Sirope.

        :param srp: Objeto Sirope.
        :return: OID codificado de forma segura o None.
        """
        oid = getattr(self, "__oid__", None)
        return srp.safe_from_oid(oid) if oid else None

    def get_created_at(self):
        """Devuelve la fecha de creación formateada.

        :return: Fecha en formato 'dd/mm/yyyy'.
        """
        return self.created_at.strftime("%d/%m/%Y")

    def get_last_login(self):
        """Devuelve la fecha de último acceso formateada o 'Nunca'.

        :return: Fecha y hora o cadena 'Nunca'.
        """
        if self.last_login:
            return self.last_login.strftime("%d/%m/%Y %H:%M")
        return "Nunca"

    def check_password(self, input_password):
        """Verifica si la contraseña introducida es válida.

        :param input_password: Contraseña proporcionada.
        :return: True si es válida, False en caso contrario.
        """
        return safe.check_password_hash(self._password, input_password)

    def set_last_login_now(self):
        """Actualiza el atributo de último acceso al momento actual."""
        self.last_login = datetime.datetime.now()

    def __eq__(self, other):
        """Compara dos objetos UserEntity por su email.

        :param other: Otro objeto a comparar.
        :return: True si tienen el mismo email, False en caso contrario.
        """
        return isinstance(other, UserEntity) and self.email == other.email

    def __hash__(self):
        """Devuelve el hash del usuario basado en su email.

        :return: Hash único.
        """
        return hash(self.email)

    @staticmethod
    def find(srp, id):
        """Busca un usuario por su ID.

        :param srp: Objeto Sirope.
        :param id: ID del usuario.
        :return: Instancia de UserEntity o None.
        """
        return srp.find_first(UserEntity, lambda u: u.id == id)

    @staticmethod
    def find_by_mail(srp, email):
        """Busca un usuario por su correo electrónico.

        :param srp: Objeto Sirope.
        :param email: Email del usuario.
        :return: Instancia de UserEntity o None.
        """
        return srp.find_first(UserEntity, lambda u: u.email == email)

    @staticmethod
    def create(srp, name, email, password, country, username, language, timezone):
        """Crea un nuevo usuario y lo guarda si no existe ya por email.

        :param srp: Objeto Sirope.
        :param name: Nombre completo.
        :param email: Correo electrónico.
        :param password: Contraseña sin hashear.
        :param country: País.
        :param username: Nombre de usuario.
        :param language: Idioma preferido.
        :param timezone: Zona horaria.
        :return: Usuario creado o None si ya existía.
        """
        if UserEntity.find_by_mail(srp, email):
            return None  # Ya existe
        user = UserEntity(name, email, password, country, username, language, timezone)
        srp.save(user)
        return user
