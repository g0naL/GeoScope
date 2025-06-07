class ConversationEntity:
    """Representa una conversación dentro de un conflicto, con su título, contenido, autor y comentarios."""

    def __init__(self, title, content, autor):
        """Inicializa una nueva conversación.

        :param title: Título de la conversación.
        :param content: Contenido principal de la conversación.
        :param autor: Nombre de usuario del autor de la conversación.
        """
        self.title = title
        self.content = content
        self.autor = autor
        self.comentario_oids = []

    def añadir_comentario(self, comentario, srp):
        """Añade un comentario a la conversación.

        :param comentario: Objeto de tipo Comentario.
        :param srp: Objeto Sirope para persistencia.
        """
        oid = srp.save(comentario)
        if oid not in self.comentario_oids:
            self.comentario_oids.append(oid)

    def get_comentarios(self, srp):
        """Devuelve la lista de comentarios asociados a esta conversación.

        :param srp: Objeto Sirope para cargar los comentarios.
        :return: Lista de objetos Comentario.
        """
        return [srp.load(oid) for oid in self.comentario_oids]

    def eliminar_comentario(self, srp, comentario_oid):
        """Elimina un comentario específico de la conversación.

        :param srp: Objeto Sirope para eliminar el comentario.
        :param comentario_oid: OID del comentario a eliminar.
        """
        if comentario_oid in self.comentario_oids:
            self.comentario_oids.remove(comentario_oid)
            srp.delete(comentario_oid)

    def eliminar_comentarios_de(self, username, srp):
        """Elimina todos los comentarios de un usuario concreto.

        :param username: Nombre del autor cuyos comentarios se eliminarán.
        :param srp: Objeto Sirope para eliminar los comentarios.
        """
        for i, c in reversed(list(enumerate(self.get_comentarios(srp)))):
            if c.autor == username:
                srp.delete_oid(self.comentario_oids[i])
                del self.comentario_oids[i]

    def to_dict(self):
        """Convierte la conversación a un diccionario serializable.

        :return: Diccionario con el título, contenido, autor y lista de comentarios.
        """
        return {
            "title": self.title,
            "content": self.content,
            "autor": self.autor,
            "comentarios": [oid.hex() for oid in self.comentario_oids]
        }
