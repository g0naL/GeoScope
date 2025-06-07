class ConversationEntity:
    def __init__(self, title, content, autor):
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
    
    def eliminar_comentario(self, srp, comentario_oid):
        """
        Elimina un comentario de la conversación y lo borra del almacenamiento.
        """
        if comentario_oid in self.comentario_oids:
            self.comentario_oids.remove(comentario_oid)
            srp.delete(comentario_oid)
        
    def eliminar_comentarios_de(self, username, srp):
        for i, c in reversed(list(enumerate(self.get_comentarios(srp)))):
            if c.autor == username:
                srp.delete_oid(self.comentario_oids[i])
                del self.comentario_oids[i]


    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "autor": self.autor,
            "comentarios": [oid.hex() for oid in self.comentario_oids]
        }
