class Conflicto:
    def __init__(self, titulo, paises, color, fillColor, descripcion="",):
        self.titulo = titulo
        self.descripcion = descripcion
        self.paises = paises
        self.color = color
        self.fillColor = fillColor

    def añadir_pais(self, pais):
        if pais not in self.paises:
            self.paises.append(pais)

    def __eq__(self, other):
        return (
            isinstance(other, Conflicto) and
            self.paises == other.paises and
            self.nombre == other.nombre
        )

    def __hash__(self):
        return hash((self.pais, self.titulo))
