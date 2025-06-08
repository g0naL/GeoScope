from datetime import datetime
import uuid

class Comentario:
    """Representa un comentario realizado por un usuario."""

    def __init__(self, autor, contenido):
        """Inicializa un comentario con un autor, contenido y fecha de creación.

        :param autor: Nombre del usuario que escribe el comentario.
        :param contenido: Texto del comentario.
        """
        self.id = str(uuid.uuid4())
        self.autor = autor
        self.contenido = contenido
        self.fecha = datetime.now()

    def to_dict(self):
        """Devuelve una representación del comentario como diccionario.

        :return: Diccionario con autor, contenido y fecha en formato ISO 8601.
        """
        return {
            "autor": self.autor,
            "contenido": self.contenido,
            "fecha": self.fecha.isoformat()
        }
