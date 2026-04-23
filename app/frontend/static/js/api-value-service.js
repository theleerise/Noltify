/**
 * @module api-value-service
 * @description Servicio auxiliar para consultar catálogos remotos de valores
 * maestros, reutilizar los resultados en caché y traducir identificadores
 * almacenados a etiquetas legibles para la interfaz.
 */

const apiValueRecordsCache = new Map();
const apiValuePromiseCache = new Map();

/**
 * Construye la URL final para consultar los valores de un master.
 *
 * @param {string} masterKey - Clave del master a consultar.
 * @param {string} [baseUrl="/api_value/data/"] - URL base del endpoint.
 * @returns {string} URL normalizada lista para usar en una petición HTTP.
 */
function buildApiValueUrl(masterKey, baseUrl = "/api_value/data/") {
    const normalizedBaseUrl = String(baseUrl || "/api_value/data/").replace(/\/+$/, "");
    const normalizedMasterKey = encodeURIComponent(String(masterKey || "").trim());

    return `${normalizedBaseUrl}/${normalizedMasterKey}`;
}

/**
 * Recupera los registros de un master remoto utilizando caché en memoria tanto
 * para resultados resueltos como para peticiones en curso.
 *
 * @async
 * @param {string} masterKey - Clave lógica del master.
 * @param {{baseUrl?: string}} [options={}] - Opciones de consulta.
 * @returns {Promise<Array<object>>} Lista de registros devueltos por la API.
 * @throws {Error} Cuando la API responde con error.
 */
async function fetchApiValueRecords(masterKey, options = {}) {
    const normalizedMasterKey = String(masterKey || "").trim().toUpperCase();

    if (!normalizedMasterKey) {
        return [];
    }

    if (apiValueRecordsCache.has(normalizedMasterKey)) {
        return apiValueRecordsCache.get(normalizedMasterKey);
    }

    if (apiValuePromiseCache.has(normalizedMasterKey)) {
        return apiValuePromiseCache.get(normalizedMasterKey);
    }

    const requestPromise = (async () => {
        const response = await fetch(
            buildApiValueUrl(
                normalizedMasterKey,
                options.baseUrl
            ),
            {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                credentials: "include"
            }
        );

        const responseJson = await response.json();

        if (!response.ok) {
            throw new Error(responseJson?.error || "No se pudieron cargar los valores del master.");
        }

        const records = Array.isArray(responseJson)
            ? responseJson
            : (Array.isArray(responseJson?.data) ? responseJson.data : []);

        apiValueRecordsCache.set(normalizedMasterKey, records);

        return records;
    })();

    apiValuePromiseCache.set(normalizedMasterKey, requestPromise);

    try {
        return await requestPromise;
    } finally {
        apiValuePromiseCache.delete(normalizedMasterKey);
    }
}

/**
 * Busca la etiqueta legible asociada a un valor dentro de una colección de
 * registros de api value.
 *
 * @param {Array<object>} records - Registros disponibles.
 * @param {*} rawValue - Valor bruto que se quiere resolver.
 * @returns {string|null} Texto mostrado al usuario o `null` si no existe coincidencia.
 */
function getApiValueLabel(records, rawValue) {
    if (rawValue === undefined || rawValue === null || rawValue === "") {
        return "";
    }

    const normalizedRawValue = String(rawValue).trim();

    const record = (records || []).find((currentRecord) => {
        const currentValue = currentRecord?.ID_ROW ?? currentRecord?.id_row;
        return String(currentValue ?? "").trim() === normalizedRawValue;
    });

    if (!record) {
        return null;
    }

    return record?.DISPLAY_VALUE ?? record?.display_value ?? null;
}

export {
    buildApiValueUrl,
    fetchApiValueRecords,
    getApiValueLabel
};
