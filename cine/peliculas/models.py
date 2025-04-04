from django.db import models

# Create your models here.

from django.db import models

class Estado(models.Model):
    strDescripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'estado'

    def __str__(self):
        return self.strDescripcion


class GeneroPelicula(models.Model):
    strDescripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'generopelicula'

    def __str__(self):
        return self.strDescripcion


class Horarios(models.Model):
    dteFechaInicio = models.DateTimeField()
    dteFechaFin = models.DateTimeField()

    class Meta:
        db_table = 'horarios'

    def __str__(self):
        return f"Horario desde {self.dteFechaInicio} hasta {self.dteFechaFin}"


class Usuario(models.Model):
    strNombre = models.CharField(max_length=45)
    strPwd = models.CharField(max_length=45)
    idEstado = models.ForeignKey(Estado, on_delete=models.CASCADE, db_column='idEstado')
    token_sesion = models.CharField(max_length=100, blank=True, null=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.strNombre


class Sala(models.Model):
    strDescripcion = models.CharField(max_length=45)
    intCantidadAcientos = models.IntegerField()
    idEstado = models.ForeignKey(Estado, on_delete=models.CASCADE, db_column='idestad')

    class Meta:
        db_table = 'sala'

    def __str__(self):
        return self.strDescripcion


# peliculas/models.py
from django.db import models

# peliculas/models.py
class Pelicula(models.Model):
    strNombre = models.CharField(max_length=45)
    strSinopsis = models.CharField(max_length=100)
    AnioEstreno = models.IntegerField()
    duracionMint = models.IntegerField()
    strArchivoFtp = models.CharField(max_length=255)
    strVideo = models.CharField(max_length=100)
    idGenero = models.ForeignKey('GeneroPelicula', on_delete=models.CASCADE)  # Cambié a GeneroPelicula

    class Meta:
        db_table = 'pelicula'

    def __str__(self):
        return self.strNombre



class Cartelera(models.Model):
    idPelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicul')
    idSala = models.ForeignKey(Sala, on_delete=models.CASCADE, db_column='idSal')
    idHorarios = models.ForeignKey(Horarios, on_delete=models.CASCADE, db_column='idHorarios')
    idEstado = models.ForeignKey(Estado, on_delete=models.CASCADE, db_column='idEsta')
    HorarioInicio = models.TimeField()
    HorarioFin = models.TimeField()

    class Meta:
        db_table = 'cartelera'

    def __str__(self):
        return f"{self.idPelicula} - {self.idSala} ({self.HorarioInicio} - {self.HorarioFin})"
