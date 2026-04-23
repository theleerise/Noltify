/**
 * @module render-table
 * @description Componente base para renderizar tablas HTML a partir de una
 * configuración declarativa de columnas, botones y datos.
 * Este módulo resuelve formato de celdas, acciones por fila y catálogos
 * auxiliares antes de pintar la tabla en el DOM.
 */

import { DateFormatter } from "./formater.js";
import { fetchApiValueRecords, getApiValueLabel } from "./api-value-service.js";
import { alertMessage } from "./alert-message.js";


/**
 * Renderiza una tabla HTML con soporte para formateo de columnas, botones por fila
 * y resolución de valores maestros.
 */
export default class RenderTable {

    /**
     * @param {object} [options={}] - Configuración de la tabla.
     * @param {string} options.tableName - Identificador lógico del contenedor.
     * @param {Object<string, object>} [options.entityConfig={}] - Metadatos por columna.
     * @param {string[]} [options.columns=[]] - Columnas a renderizar.
     * @param {Object<string, object>} [options.buttons={}] - Botones por fila.
     * @param {Function|null} [options.onRowRender=null] - Callback tras renderizar cada fila.
     * @param {Function|null} [options.onTableRendered=null] - Callback tras renderizar la tabla completa.
     * @param {string} [options.apiValueBaseUrl="/api_value/data/"] - Endpoint base para masters.
     */
    constructor(options = {}) {
        this.tableName = options.tableName;
        this.entityConfig = options.entityConfig || {};
        this.columns = Array.isArray(options.columns) ? options.columns : [];
        this.buttons = options.buttons || {};
        this.onRowRender = options.onRowRender || null;
        this.onTableRendered = options.onTableRendered || null;
        this.apiValueBaseUrl = options.apiValueBaseUrl || "/api_value/data/";
        this.apiValueRecords = {};
        this.container = this._resolveContainer();
        this.tableElement = null;
        this.tbodyElement = null;
        this.theadElement = null;
        this.data = [];
    }

    /*
        PUBLIC API
    */
    /**
     * Renderiza la tabla completa.
     *
     * @param {Array<object>|null} [data=null] - Datos a pintar. Si no se envían se usan los actuales.
     * @returns {RenderTable} Instancia actual.
     */
    render(data = null) {
        if (data !== null) {
            this.data = Array.isArray(data) ? data : [];
        }

        this._ensureApiValueMastersLoaded();
        this._createStructure();
        this._renderHeader();
        this._renderBody();

        if (this.onTableRendered) {
            this.onTableRendered({
                table: this,
                element: this.tableElement,
                data: this.data
            });
        }

        return this;
    }

    /**
     * Sustituye los datos actuales y vuelve a pintar el cuerpo de la tabla.
     *
     * @param {Array<object>} data - Datos de la tabla.
     * @returns {RenderTable} Instancia actual.
     */
    setData(data) {
        this.data = Array.isArray(data) ? data : [];
        this._renderBody();
        return this;
    }

    /**
     * Vacía el contenedor asociado a la tabla.
     *
     * @returns {void}
     */
    clear() {
        this.container.innerHTML = "";
    }

    /**
     * Muestra un estado de carga en el contenedor.
     *
     * @returns {void}
     */
    showLoading() {
        this.container.innerHTML = `<div class="alert alert-light mb-0">Cargando...</div>`;
    }

    /**
     * Muestra un estado de error en el contenedor.
     *
     * @param {string} [message="Error renderizando tabla"] - Mensaje a mostrar.
     * @returns {void}
     */
    showError(message = "Error renderizando tabla") {
        this.container.innerHTML = `<div class="alert alert-danger mb-0">${message}</div>`;
    }

    /*
        BUILD
    */
    /**
     * Crea la estructura base responsive de la tabla en el DOM.
     *
     * @returns {void}
     */
    _createStructure() {
        this.clear();

        const wrapper = document.createElement("div");
        wrapper.className = "table-responsive";

        this.tableElement = document.createElement("table");
        this.tableElement.className = "table table-sm table-striped table-hover align-middle";
        // this.tableElement.className = "table table-sm table-striped table-hover";

        const thead = document.createElement("thead");
        const tbody = document.createElement("tbody");

        this.tableElement.appendChild(thead);
        this.tableElement.appendChild(tbody);

        wrapper.appendChild(this.tableElement);
        this.container.appendChild(wrapper);

        this.theadElement = thead;
        this.tbodyElement = tbody;
    }

    /**
     * Renderiza la cabecera de la tabla con columnas y botones auxiliares.
     *
     * @returns {void}
     */
    _renderHeader() {
        const tr = document.createElement("tr");

        const startButtons = this._getButtonsByPosition("start");
        const endButtons = this._getButtonsByPosition("end");

        for (const buttonEntry of startButtons) {
            tr.appendChild(this._createButtonHeaderCell(buttonEntry));
        }

        for (const columnName of this.columns) {
            const columnConfig = this.entityConfig[columnName] || {};

            if (columnConfig.hidden === true) {
                continue;
            }

            const th = document.createElement("th");
            const columnTitle = columnConfig.title || columnName;

            th.textContent = columnTitle;
            th.setAttribute("data-column-name", columnName.toUpperCase());
            th.setAttribute("data-column-title", columnTitle);
            th.style.cursor = "pointer";
            th.title = "Doble click para ordenar";

            this._applyColumnAttributes(
                th,
                columnConfig,
                "th"
            );

            tr.appendChild(th);
        }

        for (const buttonEntry of endButtons) {
            tr.appendChild(this._createButtonHeaderCell(buttonEntry));
        }

        this.theadElement.innerHTML = "";
        this.theadElement.appendChild(tr);
    }

    /**
     * Renderiza el cuerpo de la tabla o el estado vacío si no hay datos.
     *
     * @returns {void}
     */
    _renderBody() {
        this.tbodyElement.innerHTML = "";

        if (this.data.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");

            td.colSpan = this._getTotalRenderedColumnsCount();
            td.className = "text-center text-muted";
            td.textContent = "No hay datos";

            tr.appendChild(td);
            this.tbodyElement.appendChild(tr);
            return;
        }

        for (const row of this.data) {
            const tr = this._createRow(row);
            this.tbodyElement.appendChild(tr);
        }
    }

    /**
     * Construye una fila completa a partir de un registro.
     *
     * @param {object} row - Registro origen.
     * @returns {HTMLTableRowElement} Fila renderizada.
     */
    _createRow(row) {
        const tr = document.createElement("tr");

        const startButtons = this._getButtonsByPosition("start");
        const endButtons = this._getButtonsByPosition("end");

        for (const buttonEntry of startButtons) {
            tr.appendChild(this._createSingleButtonCell(buttonEntry, row));
        }

        for (const columnName of this.columns) {
            const columnConfig = this.entityConfig[columnName] || {};

            if (columnConfig.hidden === true) {
                continue;
            }

            const td = document.createElement("td");

            this._applyColumnAttributes(
                td,
                columnConfig,
                "td"
            );

            td.innerHTML = this._formatCellValue(
                row[columnName],
                row,
                columnName,
                columnConfig
            );

            tr.appendChild(td);
        }

        for (const buttonEntry of endButtons) {
            tr.appendChild(this._createSingleButtonCell(buttonEntry, row));
        }

        if (this.onRowRender) {
            this.onRowRender({
                row,
                tr,
                table: this
            });
        }

        return tr;
    }

    /**
     * Genera la celda de cabecera asociada a una columna de botones.
     *
     * @param {{name: string, config: object}} buttonEntry - Configuración del botón.
     * @returns {HTMLTableCellElement} Celda `<th>` creada.
     */
    _createButtonHeaderCell(buttonEntry) {
        const th = document.createElement("th");
        const buttonConfig = buttonEntry.config || {};

        th.textContent = buttonConfig.headerTitle || "";

        if (buttonConfig.headerClassName) {
            th.classList.add(...buttonConfig.headerClassName.split(" ").filter(Boolean));
        }

        if (buttonConfig.headerAttrs) {
            for (const [attrName, attrValue] of Object.entries(buttonConfig.headerAttrs)) {
                if (attrValue !== null && attrValue !== undefined) {
                    th.setAttribute(attrName, String(attrValue));
                }
            }
        }

        if (buttonConfig.headerStyle) {
            th.style = buttonConfig.headerStyle;
        }

        return th;
    }

    /**
     * Genera la celda de acción de una fila concreta.
     *
     * @param {{name: string, config: object}} buttonEntry - Configuración del botón.
     * @param {object} row - Registro de la fila.
     * @returns {HTMLTableCellElement} Celda `<td>` creada.
     */
    _createSingleButtonCell(buttonEntry, row) {
        const td = document.createElement("td");
        const buttonConfig = buttonEntry.config || {};

        td.className = "text-center";

        if (buttonConfig.cellClassName) {
            td.classList.add(...buttonConfig.cellClassName.split(" ").filter(Boolean));
        }

        if (buttonConfig.cellAttrs) {
            for (const [attrName, attrValue] of Object.entries(buttonConfig.cellAttrs)) {
                if (attrValue !== null && attrValue !== undefined) {
                    td.setAttribute(attrName, String(attrValue));
                }
            }
        }

        if (buttonConfig.cellStyle) {
            td.style = buttonConfig.cellStyle;
        }

        if (typeof buttonConfig.visible === "function" && !buttonConfig.visible(row, this)) {
            td.innerHTML = "";
            return td;
        }

        const button = this._createButton(buttonEntry.name, buttonConfig, row);
        td.appendChild(button);

        return td;
    }

    /**
     * Crea el botón HTML y enlaza su acción al registro indicado.
     *
     * @param {string} name - Nombre lógico del botón.
     * @param {object} config - Configuración visual y funcional.
     * @param {object} row - Registro asociado.
     * @returns {HTMLButtonElement} Botón generado.
     */
    _createButton(name, config, row) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `btn btn-sm ${config.className || "btn-outline-secondary"}`;
        button.title = config.title || name;

        if (config.attrs) {
            for (const [attrName, attrValue] of Object.entries(config.attrs)) {
                if (attrValue !== null && attrValue !== undefined) {
                    button.setAttribute(attrName, String(attrValue));
                }
            }
        }

        if (config.ButtonIconClass) {
            const icon = document.createElement("i");
            icon.className = config.ButtonIconClass;
            button.appendChild(icon);
        } else {
            button.textContent = config.text || name;
        }

        button.addEventListener("click", () => {
            config.action(row, button, this);
        });

        return button;
    }

    /*
        HELPERS
    */
    /**
     * Localiza el contenedor objetivo donde se insertará la tabla.
     *
     * @returns {HTMLElement} Contenedor resuelto.
     * @throws {Error} Si el contenedor no existe.
     */
    _resolveContainer() {
        const element = document.querySelector(
            `[table_name="${this.tableName}"]`
        );

        if (!element) {
            throw new Error(`No existe table_name="${this.tableName}"`);
        }

        return element;
    }

    /**
     * Normaliza la configuración de botones a una lista iterable.
     *
     * @returns {Array<{name: string, config: object}>} Botones configurados.
     */
    _getButtonsEntries() {
        return Object.entries(this.buttons).map(([buttonName, buttonConfig]) => {
            return {
                name: buttonName,
                config: buttonConfig || {}
            };
        });
    }

    /**
     * Filtra los botones según la posición configurada en la tabla.
     *
     * @param {"start"|"end"} position - Posición deseada.
     * @returns {Array<{name: string, config: object}>} Botones filtrados.
     */
    _getButtonsByPosition(position) {
        return this._getButtonsEntries().filter((buttonEntry) => {
            const currentPosition = buttonEntry.config.position || "end";
            return currentPosition === position;
        });
    }

    /**
     * Cuenta cuántas columnas de datos son visibles.
     *
     * @returns {number} Número de columnas visibles.
     */
    _getVisibleColumnsCount() {
        return this.columns.filter((columnName) => {
            const columnConfig = this.entityConfig[columnName] || {};
            return columnConfig.hidden !== true;
        }).length;
    }

    /**
     * Cuenta cuántas columnas de botones se renderizarán.
     *
     * @returns {number} Número de botones configurados.
     */
    _getButtonsCount() {
        return this._getButtonsEntries().length;
    }

    /**
     * Calcula el total de columnas visibles, incluidas las de acciones.
     *
     * @returns {number} Total de columnas renderizadas.
     */
    _getTotalRenderedColumnsCount() {
        return this._getVisibleColumnsCount() + this._getButtonsCount();
    }

    /**
     * Aplica clases, atributos y estilos configurados a una celda.
     *
     * @param {HTMLElement} element - Elemento de tabla a modificar.
     * @param {object} columnConfig - Configuración de la columna.
     * @param {"th"|"td"} type - Tipo de celda a resolver.
     * @returns {void}
     */
    _applyColumnAttributes(element, columnConfig, type) {
        if (!columnConfig.table) {
            return;
        }

        const config = columnConfig.table[type];

        if (!config) {
            return;
        }

        if (config.className) {
            element.classList.add(...config.className.split(" ").filter(Boolean));
        }

        if (config.attrs) {
            for (const [attr, value] of Object.entries(config.attrs)) {
                element.setAttribute(attr, value);
            }
        }

        if (config.style) {
            element.style = config.style;
        }
    }

    /**
     * Resuelve el valor final que debe mostrarse en una celda.
     *
     * @param {*} value - Valor bruto de la celda.
     * @param {object} row - Registro completo de la fila.
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración de la columna.
     * @returns {string} Representación final visible.
     */
    _formatCellValue(value, row, columnName, columnConfig) {
        if (columnConfig.table?.formatter) {
            return columnConfig.table.formatter(
                value,
                row,
                columnName
            );
        }

        if (columnConfig.master_key) {
            return this._formatApiValue(
                value,
                columnConfig
            );
        }

        if (value === null || value === undefined) {
            return "";
        }

        // Aplicar formateos a los campos de tipo fecha.
        if (
            columnConfig.type === "date" ||
            columnConfig.type === "datetime" ||
            columnConfig.type === "time"
        ) {
            return DateFormatter.format(
                value,
                columnConfig.type
            );
        }

        if (columnConfig.type === "boolean") {
            return this._formatBooleanValue(value, columnConfig);
        }

        return String(value);
    }

    /**
     * Traduce un identificador de catálogo a su etiqueta visible.
     *
     * @param {*} value - Valor almacenado.
     * @param {object} [columnConfig={}] - Configuración de la columna.
     * @returns {string} Etiqueta resuelta o valor original serializado.
     */
    _formatApiValue(value, columnConfig = {}) {
        if (value === null || value === undefined || value === "") {
            return "";
        }

        const masterKey = String(columnConfig.master_key || "").trim().toUpperCase();
        const records = this.apiValueRecords[masterKey] || [];
        const resolvedLabel = getApiValueLabel(records, value);

        if (resolvedLabel !== null && resolvedLabel !== undefined) {
            return String(resolvedLabel);
        }

        return String(value);
    }

    /**
     * Detecta los catálogos requeridos por la tabla y lanza su carga.
     *
     * @returns {void}
     */
    _ensureApiValueMastersLoaded() {
        const mastersToLoad = this.columns
            .map((columnName) => this.entityConfig[columnName] || {})
            .map((columnConfig) => columnConfig.master_key)
            .filter(Boolean);

        const uniqueMasters = [...new Set(mastersToLoad)];

        uniqueMasters.forEach((masterKey) => {
            this._loadApiValueMaster(masterKey);
        });
    }

    /**
     * Carga un catálogo concreto y refresca el cuerpo cuando esté disponible.
     *
     * @async
     * @param {string} masterKey - Clave del catálogo.
     * @returns {Promise<void>}
     */
    async _loadApiValueMaster(masterKey) {
        const normalizedMasterKey = String(masterKey || "").trim().toUpperCase();

        if (!normalizedMasterKey) {
            return;
        }

        try {
            const records = await fetchApiValueRecords(
                normalizedMasterKey,
                { baseUrl: this.apiValueBaseUrl }
            );

            this.apiValueRecords[normalizedMasterKey] = records;

            if (this.tbodyElement) {
                this._renderBody();
            }
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "No se pudo cargar el catalogo",
                fallbackMessage: "No se pudieron resolver algunos valores de apoyo."
            });
        }
    }

    /**
     * Convierte un valor booleano configurado a su etiqueta visible.
     *
     * @param {*} value - Valor de origen.
     * @param {object} [columnConfig={}] - Configuración booleana de la columna.
     * @returns {string} Texto visible resultante.
     */
    _formatBooleanValue(value, columnConfig = {}) {
        const booleanConfig = this._getBooleanConfig(columnConfig);

        const logicalValue = this._resolveBooleanLogicalValue(
            value,
            booleanConfig
        );

        if (logicalValue === "true") {
            return booleanConfig.display.true;
        }

        if (logicalValue === "false") {
            return booleanConfig.display.false;
        }

        return String(value ?? "");
    }

    /**
     * Resuelve un valor arbitrario a una representación lógica `true` o `false`.
     *
     * @param {*} value - Valor a interpretar.
     * @param {object} [booleanConfig={}] - Configuración booleana activa.
     * @returns {"true"|"false"|null} Valor lógico normalizado.
     */
    _resolveBooleanLogicalValue(value, booleanConfig = {}) {
        if (value === null || value === undefined || value === "") {
            return null;
        }

        if (value === true) {
            return "true";
        }

        if (value === false) {
            return "false";
        }

        const configuredTrueValue = booleanConfig.values?.true;
        const configuredFalseValue = booleanConfig.values?.false;

        if (this._isSameValue(value, configuredTrueValue)) {
            return "true";
        }

        if (this._isSameValue(value, configuredFalseValue)) {
            return "false";
        }

        const normalizedValue = String(value).trim().toLowerCase();

        if ([
            "true",
            "1",
            "yes",
            "y",
            "s",
            "si",
            "sí"
        ].includes(normalizedValue)) {
            return "true";
        }

        if ([
            "false",
            "0",
            "no",
            "n"
        ].includes(normalizedValue)) {
            return "false";
        }

        return null;
    }

    /**
     * Obtiene la configuración efectiva de valores y etiquetas booleanas.
     *
     * @param {object} [columnConfig={}] - Configuración de columna.
     * @returns {{values: {true: *, false: *}, display: {true: string, false: string}}}
     */
    _getBooleanConfig(columnConfig = {}) {
        const booleanConfig = columnConfig.boolean_config || {};

        return {
            values: {
                true: Object.prototype.hasOwnProperty.call(booleanConfig?.values || {}, "true")
                    ? booleanConfig.values.true
                    : true,
                false: Object.prototype.hasOwnProperty.call(booleanConfig?.values || {}, "false")
                    ? booleanConfig.values.false
                    : false
            },
            display: {
                true: Object.prototype.hasOwnProperty.call(booleanConfig?.display || {}, "true")
                    ? booleanConfig.display.true
                    : "Sí",
                false: Object.prototype.hasOwnProperty.call(booleanConfig?.display || {}, "false")
                    ? booleanConfig.display.false
                    : "No"
            }
        };
    }

    /**
     * Compara dos valores de forma tolerante para detectar equivalencia lógica.
     *
     * @param {*} leftValue - Primer valor.
     * @param {*} rightValue - Segundo valor.
     * @returns {boolean} `true` si ambos representan lo mismo.
     */
    _isSameValue(leftValue, rightValue) {
        if (leftValue === rightValue) {
            return true;
        }

        if (leftValue === null || leftValue === undefined || rightValue === null || rightValue === undefined) {
            return false;
        }

        return String(leftValue).trim().toLowerCase() === String(rightValue).trim().toLowerCase();
    }

    /**
     * Une nombres de clase descartando valores vacíos o falsy.
     *
     * @param {...string} classNames - Clases candidatas.
     * @returns {string} Cadena final de clases.
     */
    _joinClassNames(...classNames) {
        return classNames.filter(Boolean).join(" ");
    }
}
