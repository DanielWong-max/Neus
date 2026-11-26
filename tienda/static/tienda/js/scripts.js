
/* =========================================
   NEXUS - TIENDA DE VIDEOJUEGOS
   CATALOGO, CARRITO Y PAGOS SIMULADOS
   VERSION 7
========================================= */

// =========================================
// 1. CARGAR PRODUCTOS DE DJANGO
// =========================================

let productos = [];
const IMAGEN_DEFAULT_GLOBAL = "/static/tienda/img/sin-imagen.png";

const datosDjango = document.getElementById(
    "productos-django"
);

if (datosDjango) {
    try {
        const datos = JSON.parse(datosDjango.textContent);

        productos = datos.map(p => {
            const imagenDefault = p.imagen_default || IMAGEN_DEFAULT_GLOBAL;
            const imagenReal = (p.imagen || "").trim();

            return {
                id: 1000000 + Number(p.id),
                idDjango: Number(p.id),
                nombre: p.nombre,
                categoria: p.categoria,
                precio: Number(p.precio),
                imagen: imagenReal || imagenDefault,
                imagenDefault: imagenDefault,
                existencias: Number(p.existencias),
                desdeDjango: true
            };
        });
    } catch (error) {
        console.error("Error cargando productos:", error);
    }
}

// =========================================
// 2. VARIABLES GENERALES
// =========================================

let categoriaActual = "Todos";
let carrito = [];
let compraEnProceso = false;
let modalAbierto = false;

const nombresMetodosPago = {
    tarjeta: "Tarjeta de crédito o débito",
    transferencia: "Transferencia bancaria",
    oxxo: "Pago en OXXO"
};

try {
    carrito = JSON.parse(
        localStorage.getItem("nexusCarrito")
    ) || [];
} catch (error) {
    carrito = [];
}

if (!Array.isArray(carrito)) {
    carrito = [];
}

// =========================================
// 3. FUNCIONES AUXILIARES
// =========================================

function dinero(valor) {
    return Number(valor).toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN"
    });
}

function escaparHTML(valor) {
    return String(valor).replace(
        /[&<>"']/g,
        caracter => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[caracter]
    );
}

function obtenerElemento(id) {
    return document.getElementById(id);
}

function obtenerValor(id) {
    const elemento = obtenerElemento(id);
    return elemento ? elemento.value.trim() : "";
}

function mostrarImagen(producto, ancho, alto) {
    const respaldo =
        producto.imagenDefault || IMAGEN_DEFAULT_GLOBAL;
    const ruta =
        (producto.imagen && producto.imagen !== "🎮")
            ? producto.imagen
            : respaldo;

    if (!producto.desdeDjango && producto.imagen === "🎮") {
        return "🎮";
    }

    return `
        <img
            src="${escaparHTML(ruta)}"
            alt="${escaparHTML(producto.nombre)}"
            onerror="this.onerror=null;this.src='${escaparHTML(respaldo)}';"
            style="
                width:${ancho}px;
                height:${alto}px;
                max-width:100%;
                object-fit:contain;
            "
        >
    `;
}

// =========================================
// 4. GUARDAR Y SINCRONIZAR CARRITO
// =========================================

function guardarCarritoLocal() {
    try {
        localStorage.setItem(
            "nexusCarrito",
            JSON.stringify(carrito)
        );
    } catch (error) {
        console.warn("Error guardando carrito:", error);
    }
}

function guardarCarrito() {
    guardarCarritoLocal();
    actualizarCarrito();
}

function sincronizarCarrito() {
    const actualizado = [];

    for (const item of carrito) {
        const id = Number(item.idDjango) ||
                   Number(item.id) - 1000000;

        const actual = productos.find(
            p => p.idDjango === id
        );

        if (!actual) continue;

        const cantidad = Number(item.cantidad);

        if (!Number.isInteger(cantidad) || cantidad <= 0) {
            continue;
        }

        const disponible = Math.min(
            cantidad,
            actual.existencias,
            100
        );

        if (disponible <= 0) continue;

        const existente = actualizado.find(
            p => p.idDjango === id
        );

        if (existente) {
            existente.cantidad = Math.min(
                existente.cantidad + disponible,
                actual.existencias,
                100
            );
        } else {
            actualizado.push({
                ...actual,
                cantidad: disponible
            });
        }
    }

    carrito = actualizado;
    guardarCarritoLocal();
}

// =========================================
// 5. MOSTRAR PRODUCTOS
// =========================================

function mostrarProductos() {
    const contenedor = obtenerElemento("productos");
    const buscador = obtenerElemento("buscador");

    if (!contenedor) return;

    const busqueda = buscador
        ? buscador.value.toLowerCase().trim()
        : "";

    const filtrados = productos.filter(p => {
        const coincideCategoria =
            categoriaActual === "Todos" ||
            p.categoria.toLowerCase() ===
            categoriaActual.toLowerCase();

        const coincideBusqueda =
            p.nombre.toLowerCase().includes(busqueda);

        return coincideCategoria && coincideBusqueda;
    });

    contenedor.innerHTML = "";

    if (filtrados.length === 0) {
        contenedor.innerHTML =
            "<p>No se encontraron productos.</p>";
        return;
    }

    filtrados.forEach(p => {
        const agotado = p.existencias <= 0;

        const tarjeta = document.createElement("div");
        tarjeta.className = "producto";

        tarjeta.innerHTML = `
            <div class="imagen">
                ${mostrarImagen(p, 220, 180)}
            </div>

            <div class="info">
                <small>
                    ${escaparHTML(p.categoria)}
                </small>

                <h3>${escaparHTML(p.nombre)}</h3>

                <p class="precio">
                    ${dinero(p.precio)}
                </p>

                <p style="
                    color:${agotado ? "#ff7777" : "#69e6a4"};
                    font-size:13px;
                ">
                    ${
                        agotado
                        ? "Producto agotado"
                        : "Disponible: " +
                          p.existencias + " unidades"
                    }
                </p>

                <button
                    type="button"
                    class="boton-detalles"
                    data-accion="detalles"
                >
                    👁️ Ver detalles
                </button>

                <button
                    type="button"
                    data-accion="carrito"
                    ${agotado ? "disabled" : ""}
                >
                    ${
                        agotado
                        ? "Agotado"
                        : "🛒 Agregar al carrito"
                    }
                </button>
            </div>
        `;

        tarjeta.querySelector(
            '[data-accion="detalles"]'
        ).addEventListener("click", () => {
            verDetalles(p.idDjango);
        });

        tarjeta.querySelector(
            '[data-accion="carrito"]'
        ).addEventListener("click", () => {
            agregarCarrito(p.id);
        });

        contenedor.appendChild(tarjeta);
    });
}

function filtrar(categoria) {
    categoriaActual = categoria;
    mostrarProductos();
}

function verDetalles(idDjango) {
    window.location.href =
        "/producto/" +
        encodeURIComponent(idDjango) +
        "/";
}

// =========================================
// 6. AGREGAR PRODUCTOS
// =========================================

function agregarCarrito(id) {
    if (compraEnProceso || modalAbierto) return;

    const producto = productos.find(
        p => p.id === Number(id)
    );

    if (!producto) {
        alert("No se encontró el producto.");
        return;
    }

    if (producto.existencias <= 0) {
        alert("Este producto está agotado.");
        return;
    }

    const existente = carrito.find(
        p => Number(p.id) === Number(id)
    );

    const cantidadActual = existente
        ? Number(existente.cantidad) || 0
        : 0;

    if (
        cantidadActual >= producto.existencias ||
        cantidadActual >= 100
    ) {
        alert("No hay más unidades disponibles.");
        return;
    }

    if (existente) {
        existente.cantidad = cantidadActual + 1;
        existente.precio = producto.precio;
        existente.nombre = producto.nombre;
        existente.imagen = producto.imagen;
        existente.imagenDefault = producto.imagenDefault;
        existente.existencias = producto.existencias;
    } else {
        carrito.push({
            ...producto,
            cantidad: 1
        });
    }

    guardarCarrito();
    abrirCarrito();
}

// =========================================
// 7. ACTUALIZAR CARRITO
// =========================================

function actualizarCarrito() {
    const lista = obtenerElemento("listaCarrito");

    let total = 0;
    let cantidad = 0;

    if (lista) lista.innerHTML = "";

    carrito.forEach(p => {
        const precio = Number(p.precio) || 0;
        const unidades = Number(p.cantidad) || 0;

        total += precio * unidades;
        cantidad += unidades;

        if (!lista) return;

        const item = document.createElement("div");
        item.className = "item-carrito";

        item.innerHTML = `
            <h4>
                ${mostrarImagen(p, 45, 45)}
                ${escaparHTML(p.nombre)}
            </h4>

            <p>
                ${dinero(precio)} x ${unidades}
            </p>

            <p style="
                color:#a78bfa;
                font-size:13px;
            ">
                Subtotal:
                ${dinero(precio * unidades)}
            </p>

            <button
                type="button"
                data-accion="menos"
                ${compraEnProceso || modalAbierto ? "disabled" : ""}
            >
                −
            </button>

            <button
                type="button"
                data-accion="mas"
                ${
                    compraEnProceso ||
                    modalAbierto ||
                    unidades >= p.existencias ||
                    unidades >= 100
                    ? "disabled"
                    : ""
                }
            >
                +
            </button>

            <button
                type="button"
                data-accion="eliminar"
                ${compraEnProceso || modalAbierto ? "disabled" : ""}
            >
                Eliminar
            </button>
        `;

        item.querySelector(
            '[data-accion="menos"]'
        ).addEventListener("click", () => {
            cambiarCantidad(p.id, -1);
        });

        item.querySelector(
            '[data-accion="mas"]'
        ).addEventListener("click", () => {
            cambiarCantidad(p.id, 1);
        });

        item.querySelector(
            '[data-accion="eliminar"]'
        ).addEventListener("click", () => {
            eliminarProducto(p.id);
        });

        lista.appendChild(item);
    });

    if (lista && carrito.length === 0) {
        lista.innerHTML = "<p>Tu carrito está vacío.</p>";
    }

    const contador = obtenerElemento("contador");
    const totalElemento = obtenerElemento("total");
    const botonComprar = obtenerElemento("comprar");

    if (contador) contador.textContent = cantidad;
    if (totalElemento) {
        totalElemento.textContent = dinero(total);
    }

    if (botonComprar) {
        botonComprar.disabled =
            compraEnProceso ||
            modalAbierto ||
            carrito.length === 0;

        botonComprar.textContent = compraEnProceso
            ? "⏳ Registrando pedido..."
            : "🎮 Revisar y confirmar pedido";
    }
}

function cambiarCantidad(id, cambio) {
    if (compraEnProceso || modalAbierto) return;

    const producto = carrito.find(
        p => Number(p.id) === Number(id)
    );

    if (!producto) return;

    const actual = productos.find(
        p => p.id === Number(id)
    );

    if (cambio > 0) {
        if (
            !actual ||
            Number(producto.cantidad) >= actual.existencias ||
            Number(producto.cantidad) >= 100
        ) {
            alert("No hay más unidades disponibles.");
            return;
        }
    }

    producto.cantidad =
        Number(producto.cantidad) + cambio;

    if (producto.cantidad <= 0) {
        carrito = carrito.filter(
            p => Number(p.id) !== Number(id)
        );
    }

    guardarCarrito();
}

function eliminarProducto(id) {
    if (compraEnProceso || modalAbierto) return;

    carrito = carrito.filter(
        p => Number(p.id) !== Number(id)
    );

    guardarCarrito();
}

// =========================================
// 8. ABRIR Y CERRAR CARRITO
// =========================================

function abrirCarrito() {
    const panel = obtenerElemento("carritoPanel");
    const fondo = obtenerElemento("fondoCarrito");

    if (panel) panel.classList.add("abierto");
    if (fondo) fondo.style.display = "block";
}

function cerrarCarrito() {
    if (compraEnProceso || modalAbierto) return;

    const panel = obtenerElemento("carritoPanel");
    const fondo = obtenerElemento("fondoCarrito");

    if (panel) panel.classList.remove("abierto");
    if (fondo) fondo.style.display = "none";
}

// =========================================
// 9. METODOS DE PAGO SIMULADOS
// =========================================

function obtenerMetodoPago() {
    const seleccionado = document.querySelector(
        'input[name="metodoPago"]:checked'
    );

    return seleccionado ? seleccionado.value : null;
}

function actualizarAvisoMetodoPago() {
    const metodo = obtenerMetodoPago();
    const aviso = obtenerElemento("avisoMetodoPago");

    const formularios = {
        tarjeta: obtenerElemento("formularioTarjeta"),
        transferencia: obtenerElemento("formularioTransferencia"),
        oxxo: obtenerElemento("formularioOxxo")
    };

    Object.entries(formularios).forEach(([clave, elemento]) => {
        if (elemento) {
            elemento.classList.toggle(
                "activo",
                clave === metodo
            );
        }
    });

    if (!aviso) return;

    const mensajes = {
        tarjeta:
            "💳 Pago simulado con tarjeta. " +
            "Usa únicamente los datos ficticios de prueba.",

        transferencia:
            "🏦 Transferencia simulada. " +
            "No transfieras dinero real.",

        oxxo:
            "🏪 Pago OXXO simulado. " +
            "La referencia no tiene valor monetario."
    };

    aviso.textContent =
        mensajes[metodo] ||
        "Selecciona un método de pago.";
}

// =========================================
// 10. FORMATO DE CAMPOS FICTICIOS
// =========================================

const numeroTarjeta = obtenerElemento("numeroTarjeta");
const fechaTarjeta = obtenerElemento("fechaTarjeta");
const cvvTarjeta = obtenerElemento("cvvTarjeta");

if (numeroTarjeta) {
    numeroTarjeta.addEventListener("input", () => {
        const numeros = numeroTarjeta.value
            .replace(/\D/g, "")
            .slice(0, 16);

        numeroTarjeta.value =
            numeros.match(/.{1,4}/g)?.join(" ") || "";
    });
}

if (fechaTarjeta) {
    fechaTarjeta.addEventListener("input", () => {
        const numeros = fechaTarjeta.value
            .replace(/\D/g, "")
            .slice(0, 4);

        fechaTarjeta.value =
            numeros.length > 2
            ? numeros.slice(0, 2) + "/" + numeros.slice(2)
            : numeros;
    });
}

if (cvvTarjeta) {
    cvvTarjeta.addEventListener("input", () => {
        cvvTarjeta.value = cvvTarjeta.value
            .replace(/\D/g, "")
            .slice(0, 3);
    });
}

// =========================================
// 11. VALIDAR PAGO SIMULADO
// =========================================

function validarPagoSimulado() {
    const metodo = obtenerMetodoPago();

    if (!nombresMetodosPago[metodo]) {
        throw new Error("Selecciona un método de pago.");
    }

    if (metodo === "tarjeta") {
        const banco = obtenerValor("bancoTarjeta");
        const titular = obtenerValor("titularTarjeta");

        const numero = obtenerValor("numeroTarjeta")
            .replace(/\s/g, "");

        const fecha = obtenerValor("fechaTarjeta");
        const cvv = obtenerValor("cvvTarjeta");

        const bancosPermitidos = [
            "Banco Demo NEXUS",
            "Banco Gamer Ficticio"
        ];

        if (!bancosPermitidos.includes(banco)) {
            throw new Error(
                "Selecciona un banco ficticio."
            );
        }

        if (!titular || titular.length < 3) {
            throw new Error(
                "Escribe un nombre ficticio para el titular."
            );
        }

        if (numero !== "4242424242424242") {
            throw new Error(
                "Usa únicamente la tarjeta de prueba: " +
                "4242 4242 4242 4242."
            );
        }

        if (fecha !== "12/30") {
            throw new Error(
                "La fecha de prueba debe ser 12/30."
            );
        }

        if (cvv !== "123") {
            throw new Error(
                "El CVV ficticio debe ser 123."
            );
        }

        return {
            metodo: "tarjeta",
            banco: banco,
            titular: titular,
            ultimos4: "4242"
        };
    }

    if (metodo === "transferencia") {
        const banco = obtenerValor("bancoTransferencia");
        const referencia = obtenerValor(
            "referenciaTransferencia"
        );

        const confirmacion = obtenerElemento(
            "confirmarTransferencia"
        );

        const bancosPermitidos = [
            "Banco Demo NEXUS",
            "Banco Gamer Ficticio"
        ];

        if (!bancosPermitidos.includes(banco)) {
            throw new Error(
                "Selecciona un banco ficticio de origen."
            );
        }

        if (referencia !== "NEXUS-DEMO-001") {
            throw new Error(
                "La referencia ficticia no es válida."
            );
        }

        if (!confirmacion || !confirmacion.checked) {
            throw new Error(
                "Confirma que deseas simular la transferencia."
            );
        }

        return {
            metodo: "transferencia",
            banco: banco,
            referencia: "NEXUS-DEMO-001"
        };
    }

    if (metodo === "oxxo") {
        const confirmacion = obtenerElemento(
            "confirmarOxxo"
        );

        if (!confirmacion || !confirmacion.checked) {
            throw new Error(
                "Confirma que deseas simular el pago OXXO."
            );
        }

        return {
            metodo: "oxxo",
            referencia: "NEXUS-DEMO-OXXO-001"
        };
    }

    throw new Error("Método de pago no reconocido.");
}

// =========================================
// 12. VALIDAR PRODUCTOS DEL PEDIDO
// =========================================

function validarArticulosCompra() {
    if (carrito.length === 0) {
        throw new Error("Tu carrito está vacío.");
    }

    if (carrito.length > 50) {
        throw new Error(
            "El pedido supera el límite de productos."
        );
    }

    const articulos = [];

    for (const item of carrito) {
        const actual = productos.find(
            p => p.id === Number(item.id)
        );

        if (!actual) {
            throw new Error(
                "Hay productos que ya no están disponibles."
            );
        }

        const cantidad = Number(item.cantidad);

        if (
            !Number.isInteger(cantidad) ||
            cantidad < 1 ||
            cantidad > 100
        ) {
            throw new Error(
                "Cantidad inválida para " + actual.nombre
            );
        }

        if (cantidad > actual.existencias) {
            throw new Error(
                "No hay suficientes existencias de " +
                actual.nombre
            );
        }

        articulos.push({
            id: actual.idDjango,
            cantidad: cantidad
        });
    }

    return articulos;
}

// =========================================
// 13. CALCULAR TOTAL
// =========================================

function calcularTotalCarrito() {
    return carrito.reduce((total, item) => {
        return total +
            Number(item.precio) * Number(item.cantidad);
    }, 0);
}

// =========================================
// 14. RESUMEN DE COMPRA
// =========================================

function crearResumenCompra(datosPago) {
    const metodo = datosPago.metodo;

    const productosHTML = carrito.map(item => `
        <div style="
            display:flex;
            justify-content:space-between;
            gap:10px;
            padding:8px 0;
            border-bottom:1px solid #443759;
        ">
            <span>
                ${escaparHTML(item.nombre)}
                <small>x ${Number(item.cantidad)}</small>
            </span>

            <strong>
                ${dinero(
                    Number(item.precio) *
                    Number(item.cantidad)
                )}
            </strong>
        </div>
    `).join("");

    let detallePago = "";

    if (metodo === "tarjeta") {
        detallePago = `
            <p>
                Banco: ${escaparHTML(datosPago.banco)}
            </p>
            <p>
                Titular ficticio:
                ${escaparHTML(datosPago.titular)}
            </p>
            <p>Tarjeta de prueba: •••• 4242</p>
        `;
    }

    if (metodo === "transferencia") {
        detallePago = `
            <p>
                Banco: ${escaparHTML(datosPago.banco)}
            </p>
            <p>
                Referencia:
                ${escaparHTML(datosPago.referencia)}
            </p>
        `;
    }

    if (metodo === "oxxo") {
        detallePago = `
            <p>
                Referencia ficticia:
                ${escaparHTML(datosPago.referencia)}
            </p>
        `;
    }

    return `
        <strong style="color:#c4b5fd">
            🎮 Productos
        </strong>

        ${productosHTML}

        <div style="margin-top:15px">
            <strong style="color:#c4b5fd">
                💳 Método de pago
            </strong>

            <p>
                ${escaparHTML(nombresMetodosPago[metodo])}
            </p>

            ${detallePago}
        </div>

        <div style="
            display:flex;
            justify-content:space-between;
            border-top:1px solid #55466f;
            padding-top:12px;
        ">
            <strong>Total del pedido</strong>

            <strong style="color:#c4b5fd">
                ${dinero(calcularTotalCarrito())}
            </strong>
        </div>

        <p style="font-size:12px">
            🧪 Pago simulado.
            No se realizará ningún cargo.
        </p>
    `;
}

// =========================================
// 15. ABRIR MODAL
// =========================================

function abrirModalCompra(datosPago) {
    const modal = obtenerElemento(
        "modalConfirmarCompra"
    );

    const resumen = obtenerElemento(
        "resumenModalCompra"
    );

    if (!modal || !resumen) return false;

    resumen.innerHTML = crearResumenCompra(datosPago);

    modal.classList.add("visible");
    modalAbierto = true;

    document.body.style.overflow = "hidden";
    actualizarCarrito();

    const boton = obtenerElemento("aceptarModalCompra");
    if (boton) boton.focus();

    return true;
}

function cerrarModalCompra() {
    if (compraEnProceso) return;

    const modal = obtenerElemento(
        "modalConfirmarCompra"
    );

    if (modal) modal.classList.remove("visible");

    modalAbierto = false;
    document.body.style.overflow = "";
    actualizarCarrito();
}

// =========================================
// 16. FINALIZAR COMPRA
// =========================================

function finalizarCompra() {
    if (compraEnProceso || modalAbierto) return;

    try {
        validarArticulosCompra();

        const datosPago = validarPagoSimulado();

        if (!abrirModalCompra(datosPago)) {
            alert(
                "No se encontró la ventana de confirmación."
            );
        }
    } catch (error) {
        alert("⚠️ " + error.message);
    }
}

// =========================================
// 17. TOKEN CSRF
// =========================================

function obtenerCookie(nombre) {
    const cookies = document.cookie
        ? document.cookie.split(";")
        : [];

    for (const cookie of cookies) {
        const texto = cookie.trim();

        if (texto.startsWith(nombre + "=")) {
            return decodeURIComponent(
                texto.substring(nombre.length + 1)
            );
        }
    }

    return null;
}

function obtenerTokenCSRF() {
    const campo = document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    if (campo && campo.value) return campo.value;

    return obtenerCookie("csrftoken");
}

// =========================================
// 18. INVENTARIO VISUAL
// =========================================

function descontarExistenciasLocales(articulos) {
    articulos.forEach(item => {
        const producto = productos.find(
            p => p.idDjango === item.id
        );

        if (producto) {
            producto.existencias = Math.max(
                0,
                producto.existencias - item.cantidad
            );
        }
    });

    mostrarProductos();
}

// =========================================
// 19. REGISTRAR PEDIDO EN DJANGO
// =========================================

async function registrarPedido() {
    if (compraEnProceso || !modalAbierto) return;

    let articulos;

    try {
        articulos = validarArticulosCompra();

        // Comprobar nuevamente la simulación.
        validarPagoSimulado();
    } catch (error) {
        cerrarModalCompra();
        alert(error.message);
        return;
    }

    const token = obtenerTokenCSRF();

    if (!token) {
        cerrarModalCompra();

        alert(
            "No se encontró el token CSRF. " +
            "Actualiza la página e inicia sesión."
        );
        return;
    }

    compraEnProceso = true;
    actualizarCarrito();

    const botonAceptar = obtenerElemento(
        "aceptarModalCompra"
    );

    const botonCancelar = obtenerElemento(
        "cancelarModalCompra"
    );

    if (botonAceptar) {
        botonAceptar.disabled = true;
        botonAceptar.textContent =
            "⏳ Registrando pedido...";
    }

    if (botonCancelar) {
        botonCancelar.disabled = true;
    }

    try {
        const respuesta = await fetch(
            "/compras/confirmar/",
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": token,
                    "Accept": "application/json"
                },

                // No enviar tarjeta ni CVV.
                // El backend actual recibe productos.
                body: JSON.stringify({
                    productos: articulos
                })
            }
        );

        if (respuesta.redirected) {
            const destino = new URL(respuesta.url);

            if (destino.pathname.includes("login")) {
                window.location.href =
                    destino.pathname + destino.search;
                return;
            }
        }

        let resultado;

        try {
            resultado = await respuesta.json();
        } catch (error) {
            throw new Error(
                "Django no devolvió JSON. " +
                "Revisa la terminal del servidor."
            );
        }

        if (!respuesta.ok) {
            throw new Error(
                resultado.error ||
                "No se pudo registrar el pedido."
            );
        }

        const numeroPedido = Number(
            resultado.pedido_id
        );

        if (
            !Number.isInteger(numeroPedido) ||
            numeroPedido <= 0
        ) {
            throw new Error(
                "No se recibió un número de pedido válido. " +
                "Revisa Mis pedidos antes de volver a comprar."
            );
        }

        console.log(
            "Pedido de demostración registrado:",
            numeroPedido
        );

        descontarExistenciasLocales(articulos);

        carrito = [];
        guardarCarrito();

        const modal = obtenerElemento(
            "modalConfirmarCompra"
        );

        if (modal) modal.classList.remove("visible");

        modalAbierto = false;
        document.body.style.overflow = "";

        window.location.assign(
            "/compras/pedido/" +
            encodeURIComponent(numeroPedido) +
            "/"
        );

    } catch (error) {
        console.error(
            "Error registrando pedido:",
            error
        );

        alert(
            "⚠️ No se pudo registrar la compra.\n\n" +
            error.message +
            "\n\nRevisa Mis pedidos antes de " +
            "intentarlo otra vez para evitar duplicados."
        );
    } finally {
        compraEnProceso = false;
        actualizarCarrito();

        if (botonAceptar) {
            botonAceptar.disabled = false;
            botonAceptar.textContent = "Confirmar pedido";
        }

        if (botonCancelar) {
            botonCancelar.disabled = false;
        }
    }
}

// =========================================
// 20. EVENTOS
// =========================================

const botonCancelarModal = obtenerElemento(
    "cancelarModalCompra"
);

const botonAceptarModal = obtenerElemento(
    "aceptarModalCompra"
);

if (botonCancelarModal) {
    botonCancelarModal.addEventListener(
        "click",
        cerrarModalCompra
    );
}

if (botonAceptarModal) {
    botonAceptarModal.addEventListener(
        "click",
        registrarPedido
    );
}

document.addEventListener("keydown", evento => {
    if (
        evento.key === "Escape" &&
        modalAbierto &&
        !compraEnProceso
    ) {
        cerrarModalCompra();
    }
});

document.querySelectorAll(
    'input[name="metodoPago"]'
).forEach(opcion => {
    opcion.addEventListener(
        "change",
        actualizarAvisoMetodoPago
    );
});

// =========================================
// 21. INICIAR NEXUS
// =========================================

sincronizarCarrito();
mostrarProductos();
actualizarCarrito();
actualizarAvisoMetodoPago();

console.log("NEXUS: catálogo Django conectado.");
console.log("NEXUS: carrito funcionando.");
console.log("NEXUS: pagos simulados activados.");
