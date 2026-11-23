
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, F
from django.db import transaction
from django import forms
from decimal import Decimal
import json

from .models import (
    Resena,
    Producto,
    Pedido,
    DetallePedido,
    Conversacion,
    Mensaje
)

from .forms import ProductoForm


# ==========================================
# FORMULARIO PARA EDITAR USUARIOS
# ==========================================

class UsuarioAdminForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff'
        ]

        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'is_active': 'Cuenta activa',
            'is_staff': 'Permisos de administrador'
        }

        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput()
        }


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

def inicio(request):

    productos = Producto.objects.filter(
        disponible=True
    ).order_by('-fecha_creacion')

    return render(request, 'tienda/index.html', {
        'productos_db': productos
    })


# ==========================================
# DETALLES DE PRODUCTO Y SUS RESEÑAS
# ==========================================

def detalle_producto(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        disponible=True
    )

    resenas_producto = Resena.objects.filter(
        producto=producto
    ).select_related('usuario').order_by('-fecha')

    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
        'resenas_producto': resenas_producto
    })


# ==========================================
# REGISTRO DE USUARIOS
# ==========================================

def registro(request):

    if request.method == "POST":
        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect("inicio")

    else:
        formulario = UserCreationForm()

    return render(request, "tienda/registro.html", {
        "formulario": formulario
    })


# ==========================================
# AGREGAR RESEÑA GENERAL
# ==========================================

@login_required(login_url='login')
def agregar_resena(request):

    if request.user.is_staff:
        return HttpResponseForbidden(
            "Los administradores no pueden publicar reseñas."
        )

    if request.method == "POST":

        videojuego = request.POST.get(
            "videojuego", ""
        ).strip()

        comentario = request.POST.get(
            "comentario", ""
        ).strip()

        try:
            calificacion = int(
                request.POST.get("calificacion", "")
            )
        except (ValueError, TypeError):
            calificacion = 0

        if videojuego and comentario and 1 <= calificacion <= 5:

            Resena.objects.create(
                usuario=request.user,
                videojuego=videojuego,
                calificacion=calificacion,
                comentario=comentario
            )

            return redirect("resenas")

    return redirect("resenas")


# ==========================================
# PUBLICAR RESEÑA DE UN PRODUCTO
# ==========================================

@login_required(login_url='login')
@require_POST
def agregar_resena_producto(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        disponible=True
    )

    if request.user.is_staff:
        return HttpResponseForbidden(
            "Los administradores no pueden publicar reseñas."
        )

    comentario = request.POST.get(
        "comentario", ""
    ).strip()

    try:
        calificacion = int(
            request.POST.get("calificacion", "")
        )
    except (ValueError, TypeError):
        calificacion = 0

    if comentario and 1 <= calificacion <= 5:

        Resena.objects.create(
            usuario=request.user,
            producto=producto,
            videojuego=producto.nombre,
            calificacion=calificacion,
            comentario=comentario
        )

    return redirect(
        'detalle_producto',
        id=producto.id
    )


# ==========================================
# VER TODAS LAS RESEÑAS
# ==========================================

@login_required(login_url='login')
def resenas(request):

    lista_resenas = Resena.objects.select_related(
        'usuario', 'producto'
    ).order_by('-fecha')

    return render(request, 'tienda/resenas.html', {
        'resenas': lista_resenas
    })


# ==========================================
# ELIMINAR RESEÑA
# ==========================================

@login_required(login_url='login')
@require_POST
def eliminar_resena(request, id):

    resena = get_object_or_404(Resena, id=id)

    if (
        resena.usuario_id != request.user.id
        and not request.user.is_staff
    ):
        return HttpResponseForbidden(
            "No tienes permiso para eliminar esta reseña."
        )

    producto_id = resena.producto_id

    resena.delete()

    if producto_id:
        return redirect(
            'detalle_producto',
            id=producto_id
        )

    return redirect('resenas')


# ==========================================
# MODIFICAR RESEÑA
# ==========================================

@login_required(login_url='login')
def modificar_resena(request, id):

    resena = get_object_or_404(Resena, id=id)

    if (
        request.user.is_staff
        or resena.usuario_id != request.user.id
    ):
        return HttpResponseForbidden(
            "No tienes permiso para modificar esta reseña."
        )

    if request.method == "POST":

        videojuego = request.POST.get(
            "videojuego", ""
        ).strip()

        comentario = request.POST.get(
            "comentario", ""
        ).strip()

        try:
            calificacion = int(
                request.POST.get("calificacion", "")
            )
        except (ValueError, TypeError):
            calificacion = 0

        if videojuego and comentario and 1 <= calificacion <= 5:

            if resena.producto_id:
                resena.videojuego = resena.producto.nombre
            else:
                resena.videojuego = videojuego

            resena.comentario = comentario
            resena.calificacion = calificacion
            resena.save()

            if resena.producto_id:
                return redirect(
                    'detalle_producto',
                    id=resena.producto_id
                )

            return redirect("resenas")

    return render(request, 'tienda/modificar_resena.html', {
        'resena': resena
    })


# ==========================================
# PANEL DE ADMINISTRACIÓN
# ==========================================

@staff_member_required(login_url='login')
def panel_admin(request):

    total_productos = Producto.objects.count()

    productos_disponibles = Producto.objects.filter(
        disponible=True
    ).count()

    total_usuarios = User.objects.count()

    total_resenas = Resena.objects.count()

    productos_recientes = Producto.objects.order_by(
        '-fecha_creacion'
    )[:5]

    return render(request, 'tienda/panel_admin.html', {
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'total_usuarios': total_usuarios,
        'total_resenas': total_resenas,
        'productos_recientes': productos_recientes
    })


# ==========================================
# LISTA DE PRODUCTOS
# ==========================================

@staff_member_required(login_url='login')
def administrar_productos(request):

    productos = Producto.objects.all().order_by(
        '-fecha_creacion'
    )

    return render(request, 'tienda/administrar_productos.html', {
        'productos': productos
    })


# ==========================================
# AGREGAR PRODUCTO
# ==========================================

@staff_member_required(login_url='login')
def agregar_producto(request):

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, request.FILES)

        if formulario.is_valid():
            formulario.save()
            return redirect('administrar_productos')

    else:
        formulario = ProductoForm()

    return render(request, 'tienda/formulario_producto.html', {
        'formulario': formulario,
        'titulo': 'Agregar producto'
    })


# ==========================================
# EDITAR PRODUCTO
# ==========================================

@staff_member_required(login_url='login')
def editar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':

        formulario = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto
        )

        if formulario.is_valid():
            formulario.save()
            return redirect('administrar_productos')

    else:
        formulario = ProductoForm(instance=producto)

    return render(request, 'tienda/formulario_producto.html', {
        'formulario': formulario,
        'titulo': 'Editar producto',
        'producto': producto
    })


# ==========================================
# ELIMINAR PRODUCTO
# ==========================================

@staff_member_required(login_url='login')
@require_POST
def eliminar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)

    producto.delete()

    return redirect('administrar_productos')


# ==========================================
# ADMINISTRAR USUARIOS
# ==========================================

@staff_member_required(login_url='login')
def administrar_usuarios(request):

    busqueda = request.GET.get('buscar', '').strip()

    usuarios = User.objects.all().order_by('-date_joined')

    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    total_usuarios = User.objects.count()

    total_administradores = User.objects.filter(
        is_staff=True
    ).count()

    total_clientes = User.objects.filter(
        is_staff=False
    ).count()

    return render(request, 'tienda/administrar_usuarios.html', {
        'usuarios': usuarios,
        'busqueda': busqueda,
        'total_usuarios': total_usuarios,
        'total_administradores': total_administradores,
        'total_clientes': total_clientes
    })


# ==========================================
# EDITAR USUARIO
# SOLO SUPERUSUARIOS
# ==========================================

@staff_member_required(login_url='login')
def editar_usuario(request, id):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "Solo un superusuario puede modificar cuentas."
        )

    usuario = get_object_or_404(User, id=id)

    if request.method == 'POST':

        formulario = UsuarioAdminForm(
            request.POST,
            instance=usuario
        )

        if formulario.is_valid():

            usuario_editado = formulario.save(commit=False)

            if usuario.id == request.user.id:
                usuario_editado.is_active = True
                usuario_editado.is_staff = True

            if usuario.is_superuser:
                usuario_editado.is_staff = True

            usuario_editado.save()

            return redirect('administrar_usuarios')

    else:
        formulario = UsuarioAdminForm(instance=usuario)

    return render(request, 'tienda/editar_usuario.html', {
        'formulario': formulario,
        'usuario_editado': usuario
    })


# ==========================================
# ACTIVAR / DESACTIVAR USUARIO
# SOLO SUPERUSUARIOS
# ==========================================

@staff_member_required(login_url='login')
@require_POST
def cambiar_estado_usuario(request, id):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "Solo un superusuario puede cambiar estados."
        )

    usuario = get_object_or_404(User, id=id)

    if usuario.id == request.user.id:
        return HttpResponseForbidden(
            "No puedes desactivar tu propia cuenta."
        )

    if usuario.is_superuser:
        return HttpResponseForbidden(
            "No puedes desactivar otro superusuario."
        )

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])

    return redirect('administrar_usuarios')


# ==========================================
# CONFIRMAR COMPRA Y DESCONTAR INVENTARIO
# ==========================================

@login_required(login_url='login')
@require_POST
def confirmar_compra(request):

    if request.user.is_staff:
        return JsonResponse(
            {
                'error': 'Las cuentas administrativas no pueden comprar.'
            },
            status=403
        )

    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse(
            {'error': 'JSON inválido.'},
            status=400
        )

    if not isinstance(datos, dict):
        return JsonResponse(
            {'error': 'Solicitud inválida.'},
            status=400
        )

    articulos = datos.get('productos')

    if (
        not isinstance(articulos, list)
        or not 1 <= len(articulos) <= 50
    ):
        return JsonResponse(
            {
                'error': 'El carrito está vacío o es inválido.'
            },
            status=400
        )

    # ======================================
    # VALIDAR PRODUCTOS Y CANTIDADES
    # ======================================

    cantidades = {}

    for articulo in articulos:

        if not isinstance(articulo, dict):
            return JsonResponse(
                {'error': 'Producto inválido.'},
                status=400
            )

        producto_id = articulo.get('id')
        cantidad = articulo.get('cantidad')

        if (
            type(producto_id) is not int
            or producto_id < 1
            or type(cantidad) is not int
            or not 1 <= cantidad <= 100
        ):
            return JsonResponse(
                {
                    'error': 'ID o cantidad inválida.'
                },
                status=400
            )

        cantidades[producto_id] = (
            cantidades.get(producto_id, 0) + cantidad
        )

        if cantidades[producto_id] > 100:
            return JsonResponse(
                {
                    'error': 'Cantidad máxima por producto: 100.'
                },
                status=400
            )

    # ======================================
    # DATOS OPCIONALES DEL CLIENTE
    # ======================================

    nombre = str(
        datos.get('nombre_cliente', '')
    ).strip()

    correo = str(
        datos.get('correo_cliente', '')
    ).strip()

    telefono = str(
        datos.get('telefono', '')
    ).strip()

    direccion = str(
        datos.get('direccion_entrega', '')
    ).strip()

    if (
        len(nombre) > 150
        or len(correo) > 254
        or len(telefono) > 20
        or len(direccion) > 2000
    ):
        return JsonResponse(
            {
                'error': 'Los datos de entrega son demasiado largos.'
            },
            status=400
        )

    # ======================================
    # GUARDAR PEDIDO Y DESCONTAR INVENTARIO
    # ======================================

    try:
        with transaction.atomic():

            productos = Producto.objects.filter(
                id__in=cantidades
            ).in_bulk()

            if len(productos) != len(cantidades):
                raise ValueError(
                    'Uno o más productos ya no existen.'
                )

            total = Decimal('0.00')
            detalles = []

            for producto_id in sorted(cantidades):

                producto = productos[producto_id]
                cantidad = cantidades[producto_id]

                if not producto.disponible:
                    raise ValueError(
                        f'{producto.nombre} ya no está disponible.'
                    )

                actualizados = Producto.objects.filter(
                    id=producto_id,
                    disponible=True,
                    existencias__gte=cantidad
                ).update(
                    existencias=F('existencias') - cantidad
                )

                if actualizados != 1:
                    raise ValueError(
                        f'No hay suficientes existencias de {producto.nombre}.'
                    )

                subtotal = producto.precio * cantidad
                total += subtotal

                detalles.append(
                    (producto, cantidad, subtotal)
                )

            pedido = Pedido.objects.create(
                usuario=request.user,
                total=total,
                estado='pendiente',
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono=telefono,
                direccion_entrega=direccion
            )

            DetallePedido.objects.bulk_create([
                DetallePedido(
                    pedido=pedido,
                    producto=producto,
                    nombre_producto=producto.nombre,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal
                )
                for producto, cantidad, subtotal in detalles
            ])

    except ValueError as error:
        return JsonResponse(
            {'error': str(error)},
            status=400
        )

    return JsonResponse(
        {
            'mensaje': 'Pedido registrado correctamente. Pago pendiente.',
            'pedido_id': pedido.id,
            'total': str(total),
            'estado': pedido.estado
        },
        status=201
    )


# ==========================================
# CONFIRMACIÓN DE PEDIDO
# ==========================================

@login_required(login_url='login')
def confirmacion_pedido(request, id):

    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('detalles'),
        id=id,
        usuario=request.user
    )

    return render(
        request,
        'tienda/confirmacion_pedido.html',
        {
            'pedido': pedido,
            'detalles': pedido.detalles.all()
        }
    )


# ==========================================
# HISTORIAL DE PEDIDOS DEL CLIENTE
# ==========================================

@login_required(login_url='login')
def mis_pedidos(request):

    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).prefetch_related(
        'detalles'
    ).order_by('-fecha')

    return render(
        request,
        'tienda/mis_pedidos.html',
        {
            'pedidos': pedidos
        }
    )


# ==========================================
# NEXUS - SISTEMA DE MENSAJERÍA
# ==========================================

# ==========================================
# CHAT PRIVADO DEL CLIENTE
# ==========================================

@login_required(login_url='login')
def chat_cliente(request):

    if request.user.is_staff:
        return redirect('chat_admin')

    conversacion, creada = (
        Conversacion.objects.get_or_create(
            cliente=request.user
        )
    )

    mensajes = conversacion.mensajes.select_related(
        'remitente'
    ).order_by('fecha_envio', 'id')

    conversacion.mensajes.exclude(
        remitente=request.user
    ).filter(
        leido=False
    ).update(
        leido=True
    )

    return render(
        request,
        'tienda/chat_cliente.html',
        {
            'conversacion': conversacion,
            'mensajes': mensajes
        }
    )


# ==========================================
# ENVIAR MENSAJE DEL CLIENTE
# ==========================================

@login_required(login_url='login')
@require_POST
def enviar_mensaje_cliente(request):

    if request.user.is_staff:
        return JsonResponse(
            {
                'error': (
                    'Los administradores deben '
                    'responder desde su bandeja.'
                )
            },
            status=403
        )

    contenido = request.POST.get(
        'mensaje', ''
    ).strip()

    if not contenido:
        return JsonResponse(
            {'error': 'Escribe un mensaje.'},
            status=400
        )

    if len(contenido) > 2000:
        return JsonResponse(
            {
                'error': (
                    'El mensaje no puede superar '
                    'los 2000 caracteres.'
                )
            },
            status=400
        )

    with transaction.atomic():

        conversacion, creada = (
            Conversacion.objects.get_or_create(
                cliente=request.user
            )
        )

        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            contenido=contenido
        )

        conversacion.save(
            update_fields=['fecha_actualizacion']
        )

    return JsonResponse(
        {
            'ok': True,
            'id': mensaje.id,
            'mensaje': mensaje.contenido,
            'fecha': mensaje.fecha_envio.strftime(
                '%d/%m/%Y %H:%M'
            )
        },
        status=201
    )


# ==========================================
# BANDEJA DE MENSAJES DEL ADMINISTRADOR
# ==========================================

@staff_member_required(login_url='login')
def chat_admin(request):

    conversaciones = (
        Conversacion.objects.select_related(
            'cliente'
        ).order_by(
            '-fecha_actualizacion'
        )
    )

    return render(
        request,
        'tienda/chat_admin.html',
        {
            'conversaciones': conversaciones
        }
    )


# ==========================================
# VER CONVERSACIÓN COMO ADMINISTRADOR
# ==========================================

@staff_member_required(login_url='login')
def chat_admin_detalle(request, id):

    conversacion = get_object_or_404(
        Conversacion.objects.select_related(
            'cliente'
        ),
        id=id
    )

    mensajes = conversacion.mensajes.select_related(
        'remitente'
    ).order_by(
        'fecha_envio', 'id'
    )

    conversacion.mensajes.filter(
        remitente=conversacion.cliente,
        leido=False
    ).update(
        leido=True
    )

    return render(
        request,
        'tienda/chat_admin_detalle.html',
        {
            'conversacion': conversacion,
            'mensajes': mensajes
        }
    )


# ==========================================
# RESPONDER MENSAJE COMO ADMINISTRADOR
# ==========================================

@staff_member_required(login_url='login')
@require_POST
def responder_mensaje_admin(request, id):

    conversacion = get_object_or_404(
        Conversacion,
        id=id
    )

    contenido = request.POST.get(
        'mensaje', ''
    ).strip()

    if not contenido:
        return JsonResponse(
            {'error': 'Escribe una respuesta.'},
            status=400
        )

    if len(contenido) > 2000:
        return JsonResponse(
            {
                'error': (
                    'La respuesta no puede superar '
                    'los 2000 caracteres.'
                )
            },
            status=400
        )

    with transaction.atomic():

        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            contenido=contenido
        )

        conversacion.save(
            update_fields=['fecha_actualizacion']
        )

    return JsonResponse(
        {
            'ok': True,
            'id': mensaje.id,
            'mensaje': mensaje.contenido,
            'fecha': mensaje.fecha_envio.strftime(
                '%d/%m/%Y %H:%M'
            )
        },
        status=201
    )


# ==========================================
# CONSULTAR MENSAJES ACTUALIZADOS
# ==========================================

@login_required(login_url='login')
def obtener_mensajes_chat(request, id):

    conversacion = get_object_or_404(
        Conversacion,
        id=id
    )

    if (
        not request.user.is_staff
        and conversacion.cliente_id != request.user.id
    ):
        return JsonResponse(
            {'error': 'Acceso no autorizado.'},
            status=403
        )

    try:
        ultimo_id = int(
            request.GET.get('ultimo_id', 0)
        )
    except (ValueError, TypeError):
        return JsonResponse(
            {'error': 'ID de mensaje inválido.'},
            status=400
        )

    if ultimo_id < 0:
        return JsonResponse(
            {'error': 'ID de mensaje inválido.'},
            status=400
        )

    mensajes = conversacion.mensajes.filter(
        id__gt=ultimo_id
    ).select_related(
        'remitente'
    ).order_by('id')[:100]

    datos = [
        {
            'id': mensaje.id,
            'contenido': mensaje.contenido,
            'remitente': mensaje.remitente.username,
            'es_mio': (
                mensaje.remitente_id == request.user.id
            ),
            'fecha': mensaje.fecha_envio.strftime(
                '%d/%m/%Y %H:%M'
            )
        }
        for mensaje in mensajes
    ]

    ids_recibidos = [
        mensaje['id']
        for mensaje in datos
        if not mensaje['es_mio']
    ]

    if ids_recibidos:
        conversacion.mensajes.filter(
            id__in=ids_recibidos
        ).update(
            leido=True
        )

    return JsonResponse(
        {
            'ok': True,
            'mensajes': datos
        }
    )

