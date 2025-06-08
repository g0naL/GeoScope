class MapEntity:
    """Representa un mapa que contiene una colección de conflictos geopolíticos."""

    def __init__(self, id):
        """Inicializa un nuevo mapa con un identificador único.

        :param id: Identificador manual del mapa.
        """
        self.id = id
        self.conflicto_oids = []

    def añadir_conflicto(self, conflicto, srp):
        """Añade un conflicto al mapa, si no ha sido añadido previamente.

        :param conflicto: Objeto Conflicto que se desea añadir.
        :param srp: Objeto Sirope para gestionar la persistencia.
        """
        oid = srp.save(conflicto)
        if oid not in self.conflicto_oids:
            self.conflicto_oids.append(oid)

    def get_conflictos(self, srp):
        """Devuelve todos los conflictos registrados en el mapa.

        :param srp: Objeto Sirope para cargar los conflictos.
        :return: Lista de objetos Conflicto.
        """
        return [srp.load(oid) for oid in self.conflicto_oids]

    def get_paises_afectados(self, srp):
        """Obtiene la lista de países involucrados en los conflictos del mapa.

        :param srp: Objeto Sirope para cargar los conflictos.
        :return: Lista de nombres de países únicos.
        """
        conflictos = self.get_conflictos(srp)
        return list({
            pais
            for c in conflictos
            for pais in c.paises
        })
