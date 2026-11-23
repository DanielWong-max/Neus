
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ==========================================
# PRODUCTOS DE LA TIENDA
# ==========================================

class Producto(models.Model):

    CATEGORIAS = [
        ('juegos', 'Juegos'),
        ('consolas', 'Consolas'),
        ('audifonos', 'Audífonos'),
        ('teclados_mouse', 'Teclados y Mouse'),
    ]

    nombre = models.CharField(
        max_length=150
    )

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIAS
    )

    descripcion = models.TextField()

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True
    )

    existencias = models.PositiveIntegerField(
        default=0
    )

    disponible = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre


# ==========================================
# RESEÑAS DE LOS PRODUCTOS
# ==========================================

class Resena(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    videojuego = models.CharField(
        max_length=150
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas',
        null=True,
        blank=True
    )

    calificacion = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comentario = models.TextField()

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        nombre = (
            self.producto.nombre
            if self.producto
            else self.videojuego
        )

        return f"{self.usuario.username} - {nombre}"


# ==========================================
# PEDIDOS DE LOS CLIENTES
# ==========================================

class Pedido(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    nombre_cliente = models.CharField(
        max_length=150,
        blank=True
    )

    correo_cliente = models.EmailField(
        blank=True
    )

    direccion_entrega = models.TextField(
        blank=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'


# ==========================================
# PRODUCTOS INCLUIDOS EN CADA PEDIDO
# ==========================================

class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    nombre_producto = models.CharField(
        max_length=150
    )

    cantidad = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"{self.cantidad} x {self.nombre_producto} "
            f"- Pedido #{self.pedido.id}"
        )

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedidos'


# ==========================================
# CONVERSACIONES DE SOPORTE NEXUS
# ==========================================

class Conversacion(models.Model):

    # Cada cliente tiene una conversación
    # privada con el equipo administrador.

    cliente = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conversacion_soporte'
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    activa = models.BooleanField(
        default=True
    )

    def __str__(self):
        return (
            f"Chat de {self.cliente.username}"
        )

    class Meta:
        ordering = ['-fecha_actualizacion']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'


# ==========================================
# MENSAJES DEL CHAT NEXUS
# ==========================================

class Mensaje(models.Model):

    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )

    remitente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )

    contenido = models.TextField(
        max_length=2000
    )

    fecha_envio = models.DateTimeField(
        auto_now_add=True
    )

    leido = models.BooleanField(
        default=False
    )

    def __str__(self):
        return (
            f"{self.remitente.username}: "
            f"{self.contenido[:40]}"
        )

    class Meta:
        ordering = ['fecha_envio', 'id']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'


