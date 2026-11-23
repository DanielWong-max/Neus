
from django.contrib import admin
from .models import Producto, Resena


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'categoria',
        'precio',
        'existencias',
        'disponible'
    )

    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'existencias', 'disponible')


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'videojuego',
        'calificacion',
        'fecha'
    )

    list_filter = ('calificacion', 'fecha')
    search_fields = ('usuario__username', 'videojuego')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
