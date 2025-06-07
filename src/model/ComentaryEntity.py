from datetime import datetime
import uuid

class Comentario:
    def __init__(self, autor, contenido):
        self.id = str(uuid.uuid4())
        self.autor = autor
        self.contenido = contenido
        self.fecha = datetime.now()

    def to_dict(self):
        return {
            "autor": self.autor,
            "contenido": self.contenido,
            "fecha": self.fecha.isoformat()
        }
