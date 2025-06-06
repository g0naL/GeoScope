from datetime import datetime

class Comentario:
    def __init__(self, autor, contenido):
        self.autor = autor
        self.contenido = contenido
        self.fecha = datetime.now()

    def to_dict(self):
        return {
            "autor": self.autor,
            "contenido": self.contenido,
            "fecha": self.fecha.isoformat()
        }
