/**
 * @module utils
 * @description Utilidades genéricas compartidas por el frontend.
 * Reúne pequeñas funciones de apoyo desacopladas del resto de componentes,
 * como la lectura segura de cookies del navegador.
 */

/**
 * Obtiene el valor de una cookie a partir de su nombre.
 *
 * @param {string} name - Nombre de la cookie.
 * @returns {string|null} Valor decodificado de la cookie o `null` si no existe.
 */
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let index = 0; index < cookies.length; index++) {
            const cookie = cookies[index].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}
