// Interacción del formulario: lista de ciudades por estado, ejemplos precargados y validación básica.
(function () {
  "use strict";

  const form = document.getElementById("formulario");
  if (!form) return;

  // ---- Ciudades sugeridas según el estado elegido ----
  const cache = {};
  async function cargarCiudades(estado, idLista) {
    const lista = document.getElementById(idLista);
    lista.innerHTML = "";
    if (!estado) return;
    try {
      if (!cache[estado]) {
        const resp = await fetch(`${window.API_CIUDADES}?estado=${encodeURIComponent(estado)}`);
        cache[estado] = resp.ok ? await resp.json() : [];
      }
      cache[estado].forEach((c) => {
        const op = document.createElement("option");
        op.value = c;
        lista.appendChild(op);
      });
    } catch (e) {
      // Sin conexión a la API: la ciudad es opcional, así que el formulario sigue funcionando.
    }
  }

  function enlazar(idEstado, idCiudad, idLista) {
    const sel = document.getElementById(idEstado);
    const ciudad = document.getElementById(idCiudad);
    sel.addEventListener("change", () => {
      ciudad.value = "";
      cargarCiudades(sel.value, idLista);
    });
    cargarCiudades(sel.value, idLista);
  }
  enlazar("estado_cliente", "ciudad_cliente", "lista_ciudad_cliente");
  enlazar("estado_vendedor", "ciudad_vendedor", "lista_ciudad_vendedor");

  // ---- Ejemplos para la demostración ----
  const ahora = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const fechaHoy = `${ahora.getFullYear()}-${pad(ahora.getMonth() + 1)}-${pad(ahora.getDate())}T10:30`;

  // El servidor propone la fecha en su propia zona horaria (UTC en Render). Se reemplaza por la
  // hora local del navegador, salvo que el formulario vuelva con errores (ahí se respeta lo ingresado).
  if (!document.querySelector(".alerta--error")) {
    form.elements["fecha_compra"].value =
      `${ahora.getFullYear()}-${pad(ahora.getMonth() + 1)}-${pad(ahora.getDate())}T${pad(ahora.getHours())}:${pad(ahora.getMinutes())}`;
  }
  const EJEMPLOS = {
    rapido: {
      plazo_plataforma: 12, estado_cliente: "SP", ciudad_cliente: "campinas", estado_vendedor: "SP", ciudad_vendedor: "sao paulo",
      categoria: "health_beauty", n_items: 1, n_vendedores: 1, precio_total: 59.9, flete_total: 9.8, peso_g: 300,
      largo_cm: 18, alto_cm: 8, ancho_cm: 12, medio_pago: "credit_card", cuotas: 1,
    },
    lejano: {
      plazo_plataforma: 30, estado_cliente: "BA", ciudad_cliente: "salvador", estado_vendedor: "SP", ciudad_vendedor: "ibitinga",
      categoria: "bed_bath_table", n_items: 2, n_vendedores: 1, precio_total: 159.8, flete_total: 48.6, peso_g: 1500,
      largo_cm: 40, alto_cm: 15, ancho_cm: 30, medio_pago: "boleto", cuotas: 1,
    },
    pesado: {
      plazo_plataforma: 28, estado_cliente: "RS", ciudad_cliente: "porto alegre", estado_vendedor: "PR", ciudad_vendedor: "curitiba",
      categoria: "office_furniture", n_items: 1, n_vendedores: 1, precio_total: 459.0, flete_total: 95.3, peso_g: 14000,
      largo_cm: 100, alto_cm: 10, ancho_cm: 60, medio_pago: "credit_card", cuotas: 6,
    },
  };

  document.querySelectorAll("[data-ejemplo]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const ej = EJEMPLOS[btn.dataset.ejemplo];
      form.elements["fecha_compra"].value = fechaHoy;
      Object.entries(ej).forEach(([k, v]) => {
        if (form.elements[k]) form.elements[k].value = v;
      });
      await cargarCiudades(ej.estado_cliente, "lista_ciudad_cliente");
      await cargarCiudades(ej.estado_vendedor, "lista_ciudad_vendedor");
      form.querySelectorAll(".invalido").forEach((el) => el.classList.remove("invalido"));
      form.querySelectorAll(".error").forEach((el) => el.remove());
    });
  });

  // ---- Validación en el navegador (el servidor valida de nuevo igual) ----
  form.addEventListener("submit", (ev) => {
    let primero = null;
    form.querySelectorAll("input[required], select[required]").forEach((el) => {
      el.classList.toggle("invalido", !el.checkValidity());
      if (!el.checkValidity() && !primero) primero = el;
    });
    const items = Number(form.elements["n_items"].value);
    const vend = Number(form.elements["n_vendedores"].value);
    if (vend > items) {
      form.elements["n_vendedores"].classList.add("invalido");
      if (!primero) primero = form.elements["n_vendedores"];
    }
    if (primero) {
      ev.preventDefault();
      primero.focus();
      primero.reportValidity();
      return;
    }
    const boton = document.getElementById("boton-predecir");
    boton.disabled = true;
    boton.textContent = "Calculando…";
  });

  // Si el usuario vuelve con el botón "atrás", reactivar el botón
  window.addEventListener("pageshow", () => {
    const boton = document.getElementById("boton-predecir");
    if (boton) { boton.disabled = false; boton.textContent = "Estimar tiempo de entrega"; }
  });
})();
