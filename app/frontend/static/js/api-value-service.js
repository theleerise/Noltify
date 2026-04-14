const apiValueRecordsCache = new Map();
const apiValuePromiseCache = new Map();

function buildApiValueUrl(masterKey, baseUrl = "/api_value/data/") {
    const normalizedBaseUrl = String(baseUrl || "/api_value/data/").replace(/\/+$/, "");
    const normalizedMasterKey = encodeURIComponent(String(masterKey || "").trim());

    return `${normalizedBaseUrl}/${normalizedMasterKey}`;
}

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
