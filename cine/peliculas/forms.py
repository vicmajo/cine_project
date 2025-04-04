from django import forms
from .models import Estado


class EstadoForm(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ['strDescripcion']


from django import forms
from .models import Horarios

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horarios
        fields = ['dteFechaInicio', 'dteFechaFin']


from django import forms
from .models import GeneroPelicula

class GeneroPeliculaForm(forms.ModelForm):
    class Meta:
        model = GeneroPelicula
        fields = ['strDescripcion']




from django import forms
from .models import Pelicula


        
class PeliculaForm(forms.ModelForm):
    strArchivoFtp = forms.FileField(required=False)
    class Meta:
        model = Pelicula
        fields = ['strNombre', 'strSinopsis', 'AnioEstreno', 'duracionMint','strArchivoFtp', 'strVideo', 'idGenero']


from django import forms
from .models import Cartelera

class CarteleraForm(forms.ModelForm):
    class Meta:
        model = Cartelera
        fields = '__all__'
        widgets = {
            'idPelicula': forms.Select(attrs={'class': 'form-control'}),
            'idSala': forms.Select(attrs={'class': 'form-control'}),
            'idHorarios': forms.Select(attrs={'class': 'form-control'}),
            'idEstado': forms.Select(attrs={'class': 'form-control'}),
            'HorarioInicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'HorarioFin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
