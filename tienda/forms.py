
from django import forms
from .models import Producto


# ==========================================
# FORMULARIO PARA ADMINISTRAR PRODUCTOS
# ==========================================

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto

        fields = [
            'nombre',
            'categoria',
            'descripcion',
            'precio',
            'imagen',
            'existencias',
            'disponible'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del producto',
                'rows': 5
            }),

            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Precio en MXN',
                'min': '0',
                'step': '0.01'
            }),

            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),

            'existencias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),

            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_precio(self):
        precio = self.cleaned_data['precio']

        if precio < 0:
            raise forms.ValidationError(
                'El precio no puede ser negativo.'
            )

        return precio
