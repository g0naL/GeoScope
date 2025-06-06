class ConversationEntity:
    def __init__(self, title, content, autor="Anónimo"):
        self.title = title
        self.content = content
        self.autor = autor
        self.comentario_oids = []

    def añadir_comentario(self, comentario, srp):
        oid = srp.save(comentario)
        if oid not in self.comentario_oids:
            self.comentario_oids.append(oid)

    def get_comentarios(self, srp):
        return [srp.load(oid) for oid in self.comentario_oids]

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "autor": self.autor,
            "comentarios": [oid.hex() for oid in self.comentario_oids]
        }
