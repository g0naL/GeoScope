class Conflicto:
    """Representa un conflicto geopolítico con sus países implicados, marcadores y conversaciones."""

    def __init__(self, id, titulo, paises, color, fillColor, descripcion=""):
        """Inicializa un conflicto con su información básica.

        :param id: Identificador único del conflicto.
        :param titulo: Título o nombre del conflicto.
        :param paises: Lista de países involucrados en el conflicto.
        :param color: Color del borde del conflicto en el mapa.
        :param fillColor: Color de relleno del conflicto en el mapa.
        :param descripcion: Descripción opcional del conflicto.
        """
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.paises = paises
        self.color = color
        self.fillColor = fillColor
        self.marcadores = []
        self.conversacion_oids = []

    def añadir_marcador(self, marcador: dict):
        """Añade un marcador geográfico al conflicto.

        :param marcador: Diccionario con la información del marcador (latitud, longitud, etc.).
        """
        self.marcadores.append(marcador)

    def get_marcadores(self):
        """Devuelve la lista de marcadores del conflicto.

        :return: Lista de diccionarios con información geográfica.
        """
        return self.marcadores

    def añadir_conversacion(self, conversacion, srp):
        """Añade una conversación relacionada con el conflicto.

        :param conversacion: Objeto de tipo ConversationEntity.
        :param srp: Objeto Sirope para persistencia.
        """
        oid = srp.save(conversacion)
        if oid not in self.conversacion_oids:
            self.conversacion_oids.append(oid)

    def get_conversaciones(self, srp):
        """Recupera las conversaciones asociadas al conflicto.

        :param srp: Objeto Sirope para cargar las conversaciones.
        :return: Lista de objetos ConversationEntity.
        """
        return [srp.load(oid) for oid in self.conversacion_oids]

    def eliminar_marcador(self, lat, lng):
        """Elimina un marcador del conflicto por coordenadas.

        :param lat: Latitud del marcador a eliminar.
        :param lng: Longitud del marcador a eliminar.
        """
        self.marcadores = [m for m in self.marcadores if m["lat"] != lat or m["lng"] != lng]

    def to_dict(self):
        """Convierte el conflicto a un diccionario serializable.

        :return: Diccionario con los atributos principales del conflicto.
        """
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "paises": self.paises,
            "color": self.color,
            "fillColor": self.fillColor,
            "marcadores": self.marcadores
        }
