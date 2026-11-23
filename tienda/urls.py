
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [

    # ==========================================
    # PÁGINA PRINCIPAL
    # ==========================================

    path(
        '',
        views.inicio,
        name='inicio'
    ),

    # ==========================================
    # DETALLES DE CADA PRODUCTO
    # ==========================================

    path(
        'producto/<int:id>/',
        views.detalle_producto,
        name='detalle_producto'
    ),

    # ==========================================
    # PUBLICAR RESEÑA DE UN PRODUCTO
    # ==========================================

    path(
        'producto/<int:id>/resena/agregar/',
        views.agregar_resena_producto,
        name='agregar_resena_producto'
    ),

    # ==========================================
    # REGISTRO DE USUARIOS
    # ==========================================

    path(
        'registro/',
        views.registro,
        name='registro'
    ),

    # ==========================================
    # INICIAR SESIÓN
    # ==========================================

    path(
        'login/',
        LoginView.as_view(
            template_name='tienda/login.html',
            next_page='inicio'
        ),
        name='login'
    ),

    # ==========================================
    # CERRAR SESIÓN
    # ==========================================

    path(
        'logout/',
        LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),

    # ==========================================
    # VER TODAS LAS RESEÑAS
    # ==========================================

    path(
        'resenas/',
        views.resenas,
        name='resenas'
    ),

    # ==========================================
    # AGREGAR RESEÑA GENERAL
    # ==========================================

    path(
        'resenas/agregar/',
        views.agregar_resena,
        name='agregar_resena'
    ),

    # ==========================================
    # ELIMINAR RESEÑA
    # ==========================================

    path(
        'resenas/eliminar/<int:id>/',
        views.eliminar_resena,
        name='eliminar_resena'
    ),

    # ==========================================
    # MODIFICAR RESEÑA
    # ==========================================

    path(
        'resenas/modificar/<int:id>/',
        views.modificar_resena,
        name='modificar_resena'
    ),

    # ==========================================
    # PANEL DE ADMINISTRACIÓN
    # ==========================================

    path(
        'panel-admin/',
        views.panel_admin,
        name='panel_admin'
    ),

    # ==========================================
    # ADMINISTRAR PRODUCTOS
    # ==========================================

    path(
        'administracion/productos/',
        views.administrar_productos,
        name='administrar_productos'
    ),

    # ==========================================
    # AGREGAR NUEVO PRODUCTO
    # ==========================================

    path(
        'administracion/productos/agregar/',
        views.agregar_producto,
        name='agregar_producto'
    ),

    # ==========================================
    # EDITAR PRODUCTO
    # ==========================================

    path(
        'administracion/productos/editar/<int:id>/',
        views.editar_producto,
        name='editar_producto'
    ),

    # ==========================================
    # ELIMINAR PRODUCTO
    # ==========================================

    path(
        'administracion/productos/eliminar/<int:id>/',
        views.eliminar_producto,
        name='eliminar_producto'
    ),

    # ==========================================
    # ADMINISTRAR USUARIOS
    # ==========================================

    path(
        'administracion/usuarios/',
        views.administrar_usuarios,
        name='administrar_usuarios'
    ),

    # ==========================================
    # EDITAR USUARIO
    # ==========================================

    path(
        'administracion/usuarios/editar/<int:id>/',
        views.editar_usuario,
        name='editar_usuario'
    ),

    # ==========================================
    # ACTIVAR O DESACTIVAR USUARIO
    # ==========================================

    path(
        'administracion/usuarios/estado/<int:id>/',
        views.cambiar_estado_usuario,
        name='cambiar_estado_usuario'
    ),

    # ==========================================
    # CONFIRMAR COMPRA
    # ==========================================

    path(
        'compras/confirmar/',
        views.confirmar_compra,
        name='confirmar_compra'
    ),

    # ==========================================
    # VER CONFIRMACIÓN DE UN PEDIDO
    # ==========================================

    path(
        'compras/pedido/<int:id>/',
        views.confirmacion_pedido,
        name='confirmacion_pedido'
    ),

    # ==========================================
    # HISTORIAL DE COMPRAS
    # ==========================================

    path(
        'mis-pedidos/',
        views.mis_pedidos,
        name='mis_pedidos'
    ),

    # ==========================================
    # CHAT PRIVADO DEL CLIENTE
    # ==========================================

    path(
        'mensajes/',
        views.chat_cliente,
        name='chat_cliente'
    ),

    # ==========================================
    # ENVIAR MENSAJE DEL CLIENTE
    # ==========================================

    path(
        'mensajes/enviar/',
        views.enviar_mensaje_cliente,
        name='enviar_mensaje_cliente'
    ),

    # ==========================================
    # BANDEJA DE MENSAJES DEL ADMINISTRADOR
    # ==========================================

    path(
        'administracion/mensajes/',
        views.chat_admin,
        name='chat_admin'
    ),

    # ==========================================
    # VER CONVERSACIÓN DEL CLIENTE
    # COMO ADMINISTRADOR
    # ==========================================

    path(
        'administracion/mensajes/<int:id>/',
        views.chat_admin_detalle,
        name='chat_admin_detalle'
    ),

    # ==========================================
    # RESPONDER MENSAJE DEL CLIENTE
    # ==========================================

    path(
        'administracion/mensajes/<int:id>/responder/',
        views.responder_mensaje_admin,
        name='responder_mensaje_admin'
    ),

    # ==========================================
    # CONSULTAR MENSAJES NUEVOS
    # ==========================================

    path(
        'mensajes/conversacion/<int:id>/actualizar/',
        views.obtener_mensajes_chat,
        name='obtener_mensajes_chat'
    ),

]



