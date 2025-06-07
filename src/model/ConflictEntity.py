class Conflicto:
    def __init__(self, id, titulo, paises, color, fillColor, descripcion=""):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.paises = paises
        self.color = color
        self.fillColor = fillColor
        self.marcadores = []  # Lista de diccionarios
        self.conversacion_oids = []  # Lista de OIDs de ConversationEntity

    def añadir_marcador(self, marcador: dict):
        self.marcadores.append(marcador)

    def get_marcadores(self):
        return self.marcadores

    def añadir_conversacion(self, conversacion, srp):
        oid = srp.save(conversacion)
        if oid not in self.conversacion_oids:
            self.conversacion_oids.append(oid)

    def get_conversaciones(self, srp):
        return [srp.load(oid) for oid in self.conversacion_oids]
    
    def eliminar_marcador(self, lat, lng):
        self.marcadores = [m for m in self.marcadores if m["lat"] != lat or m["lng"] != lng]

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "paises": self.paises,
            "color": self.color,
            "fillColor": self.fillColor,
            "marcadores": self.marcadores
        }
