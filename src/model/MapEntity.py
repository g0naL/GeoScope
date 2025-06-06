class Mapa:
    def __init__(self, id):
        self.id = id  # Asignado manualmente
        self.conflicto_oids = []  # Lista de OIDs de objetos Conflicto

    def añadir_conflicto(self, conflicto, srp):
        oid = srp.save(conflicto)
        if oid not in self.conflicto_oids:
            self.conflicto_oids.append(oid)

    def get_conflictos(self, srp):
        return [srp.load(oid) for oid in self.conflicto_oids]


    def get_paises_afectados(self, srp):
        conflictos = self.get_conflictos(srp)
        return list({
            pais
            for c in conflictos
            for pais in c.paises
        })
