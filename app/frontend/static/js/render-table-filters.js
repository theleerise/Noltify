/**
 * @module render-table-filters
 * @description Constructor de formularios de filtrado para tablas.
 * Genera dinámicamente operadores e inputs a partir de los metadatos de las
 * columnas, normalizando después los valores para su envío al backend.
 */

import { fetchApiValueRecords } from "./api-value-service.js";
import { alertMessage } from "./alert-message.js";

/**
 * Genera y administra un formulario de filtros asociado a una tabla.
 */
export class RenderTableFilters {

    /**
     * @param {object} [options={}] - Configuración del formulario de filtros.
     * @param {string} options.filtersName - Nombre lógico del filtro.
     * @param {Object<string, object>} [options.entityConfig={}] - Configuración de columnas.
     * @param {string[]} [options.columns=[]] - Columnas disponibles.
     * @param {Function|null} [options.onSubmit=null] - Callback al enviar.
     * @param {Function|null} [options.onReset=null] - Callback al resetear.
     */
    constructor(options = {}) {
        this.filtersName = options.filtersName || null;
        this.entityConfig = options.entityConfig || {};
        this.columns = Array.isArray(options.columns) ? options.columns : [];

        this.onSubmit = typeof options.onSubmit === "function" ? options.onSubmit : null;
        this.onReset = typeof options.onReset === "function" ? options.onReset : null;

        this.submitText = options.submitText || "Buscar";
        this.resetText = options.resetText || "Limpiar";
        this.formClassName = options.formClassName || "rt-filters";
        this.gridClassName = options.gridClassName || "d-flex flex-column gap-3";
        this.rowClassName = "row g-2 align-items-center mb-1";
        this.apiValueBaseUrl = options.apiValueBaseUrl || "/api_value/data/";
        this.apiValueRecords = {};

        this.container = this._resolveContainer();
        this.formContainer = this._resolveFormContainer();
        this.actionsContainer = this._resolveActionsContainer();
        this.form = null;
        this.formId = `${this.filtersName}-internal-form`;
    }

    /**
     * Localiza el contenedor principal de filtros en el DOM.
     *
     * @returns {HTMLElement} Contenedor raíz del componente.
     * @throws {Error} Si no existe un contenedor válido.
     */
    _resolveContainer() {
        if (!this.filtersName) {
            throw new Error("Debes informar 'filtersName'.");
        }

        const container = document.querySelector(`[filters_name="${this.filtersName}"]`);
        if (!container) {
            throw new Error(`No existe ningún contenedor con filters_name="${this.filtersName}".`);
        }

        return container;
    }

    /**
     * Busca el subcontenedor reservado al formulario de filtros.
     *
     * @returns {HTMLElement|null} Contenedor del formulario o `null`.
     */
    _resolveFormContainer() {
        return this.container.querySelector(`[filters_form="${this.filtersName}-form"]`);
    }

    /**
     * Busca el subcontenedor reservado a las acciones del formulario.
     *
     * @returns {HTMLElement|null} Contenedor de acciones o `null`.
     */
    _resolveActionsContainer() {
        return this.container.querySelector(`[filters_actions="${this.filtersName}-actions"]`);
    }

    /**
     * Construye y renderiza el formulario de filtros.
     *
     * @returns {RenderTableFilters} Instancia actual.
     */
    render() {
        if (this.formContainer) {
            this.formContainer.innerHTML = "";
        }

        if (this.actionsContainer) {
            this.actionsContainer.innerHTML = "";
        }

        if (!this.formContainer && !this.actionsContainer) {
            this.container.innerHTML = "";
        }

        this.form = document.createElement("form");
        this.form.className = this.formClassName;
        this.form.id = this.formId;

        const grid = document.createElement("div");
        grid.className = this.gridClassName;

        const filterableColumns = this._getFilterableColumns();

        for (const columnName of filterableColumns) {
            const columnConfig = this.entityConfig[columnName] || {};

            grid.appendChild(
                this._buildFilterField(
                    columnName,
                    columnConfig
                )
            );
        }

        this.form.appendChild(grid);
        this.form.addEventListener(
            "submit",
            (event) => {
                event.preventDefault();
                const filters = this.getFilters();
                if (this.onSubmit) {
                    this.onSubmit(filters, this);
                }
            }
        );

        if (this.formContainer) {
            this.formContainer.appendChild(this.form);
        } else {
            this.container.appendChild(this.form);
        }

        const actions = this._buildActions();
        if (this.actionsContainer) {
            this.actionsContainer.appendChild(actions);
        } else {
            this.form.appendChild(actions);
        }
    
        return this;
    }

    /**
     * Lee el formulario y devuelve la estructura de filtros normalizada para backend.
     *
     * @returns {Object<string, object>} Mapa de filtros por columna.
     */
    getFilters() {
        if (!this.form) {
            return {};
        }

        const filters = {};
        const filterableColumns = this._getFilterableColumns();

        for (const columnName of filterableColumns) {
            const columnConfig = this.entityConfig[columnName] || {};
            const operator = this.form.querySelector(`[name="${columnName}__operator"]`)?.value;

            if (!operator) {
                continue;
            }

            const normalizedType = this._normalizeFilterType(columnConfig.type);
            const booleanConfig = this._getBooleanConfig(columnConfig);

            if (operator === "IS_NULL" || operator === "IS_NOT_NULL") {
                filters[columnName.toUpperCase()] = {
                    type: normalizedType,
                    filter: operator,
                    values: null,
                    boolean_config: columnConfig.type === "boolean" ? booleanConfig : undefined
                };
                continue;
            }

            if (operator === "BETWEEN") {
                const startValueRaw = this.form.querySelector(`[name="${columnName}__start"]`)?.value;
                const endValueRaw = this.form.querySelector(`[name="${columnName}__end"]`)?.value;
                const startValue = this._normalizeInputValue(startValueRaw, columnConfig);
                const endValue = this._normalizeInputValue(endValueRaw, columnConfig);

                if (this._isEmptyValue(startValue) && this._isEmptyValue(endValue)) {
                    continue;
                }

                const filterConfig = {
                    type: normalizedType,
                    filter: operator,
                    values: [
                        this._isEmptyValue(startValue) ? null : startValue,
                        this._isEmptyValue(endValue) ? null : endValue
                    ]
                };

                if (columnConfig.type === "boolean") {
                    filterConfig.boolean_config = booleanConfig;
                }

                filters[columnName.toUpperCase()] = filterConfig;
                continue;
            }

            const input = this.form.querySelector(`[name="${columnName}"]`);

            if (!input) {
                continue;
            }

            const value = this._normalizeInputValue(input.value, columnConfig);

            if (this._isEmptyValue(value)) {
                continue;
            }

            const filterConfig = {
                type: normalizedType,
                filter: operator,
                values: value
            };

            if (columnConfig.type === "boolean") {
                filterConfig.boolean_config = booleanConfig;
            }

            filters[columnName.toUpperCase()] = filterConfig;
        }
        return filters;
    }

    /**
     * Limpia el formulario y vuelve a renderizar los inputs dependientes del operador.
     *
     * @returns {void}
     */
    reset() {
        if (!this.form) {
            return;
        }

        this.form.reset();

        const filterableColumns = this._getFilterableColumns();
        for (const columnName of filterableColumns) {
            const columnConfig = this.entityConfig[columnName] || {};
            const operatorSelect = this.form.querySelector(`[name="${columnName}__operator"]`);
            const inputContainer = this.form.querySelector(`[data-filter-input-container="${columnName}"]`);

            if (operatorSelect && inputContainer) {
                this._renderInput(
                    columnName,
                    columnConfig,
                    operatorSelect.value,
                    inputContainer
                );
            }
        }

        if (this.onReset) {
            this.onReset(this);
        }
    }

    /**
     * Construye la fila visual completa de un filtro.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @returns {HTMLDivElement} Fila generada.
     */
    _buildFilterField(columnName, columnConfig) {
        const wrapper = document.createElement("div");
        wrapper.className = this.rowClassName;

        const labelColumn = document.createElement("div");
        labelColumn.className = columnConfig.filter?.labelColumnClassName || "col-12 col-lg-3";

        const operatorColumn = document.createElement("div");
        operatorColumn.className = columnConfig.filter?.operatorColumnClassName || "col-12 col-lg-3";

        const valueColumn = document.createElement("div");
        valueColumn.className = columnConfig.filter?.valueColumnClassName || "col-12 col-lg-6";

        const label = document.createElement("label");
        label.className = "form-label mb-0 fw-semibold";
        label.textContent = columnConfig.title || columnName;

        const operatorSelect = this._buildOperatorSelect(columnName, columnConfig);
        const inputContainer = document.createElement("div");
        inputContainer.setAttribute("data-filter-input-container", columnName);

        labelColumn.appendChild(label);
        operatorColumn.appendChild(operatorSelect);
        valueColumn.appendChild(inputContainer);

        wrapper.appendChild(labelColumn);
        wrapper.appendChild(operatorColumn);
        wrapper.appendChild(valueColumn);

        this._renderInput(
            columnName,
            columnConfig,
            operatorSelect.value,
            inputContainer
        );

        operatorSelect.addEventListener("change", () => {
            this._renderInput(
                columnName,
                columnConfig,
                operatorSelect.value,
                inputContainer);
        });
        return wrapper;
    }

    /**
     * Genera el selector de operadores de una columna filtrable.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @returns {HTMLSelectElement} Selector de operadores.
     */
    _buildOperatorSelect(columnName, columnConfig) {
        const select = document.createElement("select");
        select.className = columnConfig.filter?.operatorClassName || "form-select";
        select.name = `${columnName}__operator`;

        const operators = columnConfig.filter?.operators || this._getDefaultOperators(columnConfig.type);
        for (const operator of operators) {
            const option = document.createElement("option");
            option.value = operator;
            option.textContent = this._getOperatorLabel(operator);
            select.appendChild(option);
        }
        return select;
    }

    /**
     * Renderiza el input adecuado según el operador y el tipo de columna.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @param {string} operator - Operador seleccionado.
     * @param {HTMLElement} container - Contenedor donde pintar el input.
     * @returns {void}
     */
    _renderInput(columnName, columnConfig, operator, container) {
        container.innerHTML = "";

        if (operator === "IS_NULL" || operator === "IS_NOT_NULL") {
            const placeholder = document.createElement("div");
            placeholder.className = "form-control bg-light";
            placeholder.textContent = "Este filtro no requiere valor";
            container.appendChild(placeholder);
            return;
        }

        if (operator === "BETWEEN") {
            container.appendChild(
                this._buildBetweenRange(columnName, columnConfig)
            );
            return;
        }
        if (columnConfig.type === "boolean") {
            container.appendChild(
                this._buildBooleanSelect(columnName, columnConfig));
            return;
        }

        if (columnConfig.master_key) {
            container.appendChild(
                this._buildApiValueSelect(columnName, columnConfig)
            );
            return;
        }

        container.appendChild(
            this._buildSingleInput(
                columnName,
                columnConfig,
                this._resolveInputType(columnConfig)
            )
        );
    }

    /**
     * Construye un campo simple de entrada para un filtro.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @param {string} inputType - Tipo HTML del input.
     * @returns {HTMLInputElement} Campo generado.
     */
    _buildSingleInput(columnName, columnConfig, inputType) {
        const input = document.createElement("input");
        input.className = this._getInputClassName(columnConfig);

        input.name = columnName;
        input.type = inputType;
        input.placeholder = this._getPlaceholder(columnConfig);

        if (columnConfig.filter?.attrs) {
            for (const [attrName, attrValue] of Object.entries(columnConfig.filter.attrs)) {
                if ( attrValue !== null && attrValue !== undefined) {
                    input.setAttribute(attrName, String(attrValue));
                }
            }
        }
        return input;
    }

    /**
     * Construye un rango doble para filtros tipo `BETWEEN`.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @returns {HTMLDivElement} Contenedor del rango.
     */
    _buildBetweenRange(columnName, columnConfig) {
        const wrapper = document.createElement("div");
        wrapper.className = "row g-2";

        const startColumn = document.createElement("div");
        startColumn.className = "col-12 col-xl-6";

        const endColumn = document.createElement("div");
        endColumn.className = "col-12 col-xl-6";

        const startInput = document.createElement("input");
        startInput.className = this._getInputClassName(columnConfig);
        startInput.name = `${columnName}__start`;
        startInput.type = this._resolveInputType(columnConfig);
        startInput.placeholder = "Desde";

        const endInput = document.createElement("input");
        endInput.className = this._getInputClassName(columnConfig);
        endInput.name = `${columnName}__end`;
        endInput.type = this._resolveInputType(columnConfig);
        endInput.placeholder = "Hasta";

        if (columnConfig.filter?.attrs) {
            for (const [attrName, attrValue] of Object.entries(columnConfig.filter.attrs)) {
                if (attrValue !== null && attrValue !== undefined) {
                    startInput.setAttribute(attrName, String(attrValue));
                    endInput.setAttribute(attrName, String(attrValue));
                }
            }
        }

        startColumn.appendChild(startInput);
        endColumn.appendChild(endInput);

        wrapper.appendChild(startColumn);
        wrapper.appendChild(endColumn);

        return wrapper;
    }

    /**
     * Construye un selector específico para filtros booleanos.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @returns {HTMLSelectElement} Selector generado.
     */
    _buildBooleanSelect(columnName, columnConfig) {
        const select = document.createElement("select");
        select.className = this._getInputClassName(columnConfig, "form-select");
        select.name = columnName;

        const options = columnConfig.filter?.options || this._getDefaultBooleanOptions(columnConfig);

        for (const optionConfig of options) {
            const option = document.createElement("option");
            option.value = optionConfig.value;
            option.textContent = optionConfig.label;

            select.appendChild(option);
        }

        return select;
    }

    /**
     * Construye un selector dependiente de un catálogo remoto.
     *
     * @param {string} columnName - Nombre de la columna.
     * @param {object} columnConfig - Configuración del filtro.
     * @returns {HTMLSelectElement} Selector generado.
     */
    _buildApiValueSelect(columnName, columnConfig) {
        const select = document.createElement("select");
        select.className = this._getInputClassName(columnConfig, "form-select");
        select.name = columnName;

        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = columnConfig.filter?.placeholder || "Todos";
        select.appendChild(emptyOption);

        this._loadApiValueOptions(select, columnConfig);

        return select;
    }

    /**
     * Crea el bloque de acciones del formulario de filtros.
     *
     * @returns {HTMLDivElement} Contenedor con botones de acción.
     */
    _buildActions() {
        const wrapper = document.createElement("div");

        wrapper.className = "d-flex gap-2";

        const submitButton = document.createElement("button");
        submitButton.type = "submit";
        submitButton.className = "btn btn-primary";
        submitButton.textContent = this.submitText;
        submitButton.setAttribute("form", this.formId);

        const resetButton = document.createElement("button");
        resetButton.type ="button";
        resetButton.className = "btn btn-outline-secondary";
        resetButton.textContent = this.resetText;
        resetButton.addEventListener("click", () => this.reset());

        wrapper.appendChild(submitButton);
        wrapper.appendChild(resetButton);

        return wrapper;
    }

    /**
     * Devuelve la lista de operadores por defecto según el tipo de dato.
     *
     * @param {string} type - Tipo lógico de la columna.
     * @returns {string[]} Operadores permitidos.
     */
    _getDefaultOperators(type) {
        const operatorsMap = {
            string: [
                "LIKE_CONTAINS",
                "LIKE_STARTS_WITH",
                "LIKE_ENDS_WITH",
                "EQUAL",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            integer: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            number: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            decimal: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            float: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            date: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            datetime: [
                "EQUAL",
                "GREATER_THAN",
                "GREATER_EQUAL",
                "LESS_THAN",
                "LESS_EQUAL",
                "BETWEEN",
                "IS_NULL",
                "IS_NOT_NULL"
            ],
            boolean: [
                "EQUAL"
            ]
        };

        return operatorsMap[type] || operatorsMap.string;
    }

    /**
     * Traduce una clave de operador a su etiqueta visible.
     *
     * @param {string} operator - Operador interno.
     * @returns {string} Etiqueta legible.
     */
    _getOperatorLabel(operator) {
        const labels = {
            LIKE_CONTAINS:
                "Contiene",
            LIKE_STARTS_WITH:
                "Empieza por",
            LIKE_ENDS_WITH:
                "Termina por",
            EQUAL:
                "Igual",
            GREATER_THAN:
                "Mayor que",
            GREATER_EQUAL:
                "Mayor o igual",
            LESS_THAN:
                "Menor que",
            LESS_EQUAL:
                "Menor o igual",
            BETWEEN:
                "Entre",
            NOT_EQUAL:
                "Distinto",
            IS_NULL:
                "Es nulo",
            IS_NOT_NULL:
                "No es nulo"
        };
        return labels[operator] || operator;
    }

    /**
     * Obtiene únicamente las columnas configuradas como filtrables.
     *
     * @returns {string[]} Lista de columnas visibles en el formulario.
     */
    _getFilterableColumns() {
        const columns = this._getConfiguredColumns();

        return columns.filter(
            (columnName) => {
                const columnConfig = this.entityConfig[columnName] || {};
                return columnConfig.nofilter !== true;
            }
        );
    }

    /**
     * Resuelve la lista base de columnas configuradas para el componente.
     *
     * @returns {string[]} Columnas disponibles.
     */
    _getConfiguredColumns() {
        if (Array.isArray(this.columns) && this.columns.length > 0) {
            return this.columns.filter(
                (columnName) => {
                    return Object.prototype.hasOwnProperty.call(
                        this.entityConfig,
                        columnName
                    );
                }
            );
        }
        return Object.keys(this.entityConfig || {});
    }

    /**
     * Resuelve la clase CSS que debe usar un input del filtro.
     *
     * @param {object} columnConfig - Configuración de columna.
     * @param {string} [defaultClassName="form-control"] - Clase por defecto.
     * @returns {string} Clase CSS final.
     */
    _getInputClassName(columnConfig, defaultClassName = "form-control") {
        return columnConfig.filter?.className || defaultClassName;
    }

    /**
     * Obtiene el placeholder configurado para un filtro.
     *
     * @param {object} columnConfig - Configuración de columna.
     * @returns {string} Placeholder final.
     */
    _getPlaceholder(columnConfig) {
        return columnConfig.filter?.placeholder || "";
    }

    /**
     * Determina el tipo HTML de input más adecuado para una columna.
     *
     * @param {object} columnConfig - Configuración de columna.
     * @returns {string} Tipo de input.
     */
    _resolveInputType(columnConfig) {
        if (columnConfig.filter?.input) {
            return columnConfig.filter.input;
        }
        switch (columnConfig.type) {
            case "integer":
            case "number":
            case "decimal":
            case "float":
                return "number";
            case "date":
                return "date";
            case "datetime":
                return "datetime-local";
            default:
                return "text";
        }
    }

    /**
     * Normaliza el tipo de dato para adaptarlo al formato esperado por backend.
     *
     * @param {string} fieldType - Tipo original de la columna.
     * @returns {string} Tipo normalizado.
     */
    _normalizeFilterType(fieldType) {
        if (fieldType === "datetime") {
            return "date";
        }

        if (fieldType === "number" || fieldType === "decimal") {
            return "float";
        }
        return fieldType
            || "string";
    }

    /**
     * Convierte el valor introducido al tipo lógico de la columna.
     *
     * @param {*} value - Valor bruto del formulario.
     * @param {object} columnConfig - Configuración de columna.
     * @returns {*} Valor normalizado.
     */
    _normalizeInputValue(value, columnConfig) {

        if (value === undefined || value === null) {
            return "";
        }
        const trimmedValue = String(value).trim();

        if (trimmedValue === "") {
            return "";
        }
        if (columnConfig.type === "boolean") {
            return this._mapBooleanLogicalValueToCrudValue(trimmedValue, columnConfig);
        }

        if (columnConfig.type === "integer") {
            return parseInt(trimmedValue, 10);
        }
        if (columnConfig.type === "number" || columnConfig.type === "decimal" || columnConfig.type === "float") {
            return parseFloat(trimmedValue);
        }
        if (columnConfig.type === "datetime") {
            return this._normalizeDateTimeLocal(trimmedValue);
        }
        return trimmedValue;
    }

    /**
     * Convierte un `datetime-local` del navegador al formato esperado por backend.
     *
     * @param {string} value - Valor local recibido.
     * @returns {string} Fecha y hora normalizadas.
     */
    _normalizeDateTimeLocal(value) {
        if (!value) {
            return value;
        }
        const normalizedValue =
            value.replace("T", " ");
        if (normalizedValue.length === 16) {
            return `${normalizedValue}:00`;
        }
        return normalizedValue;
    }

    /**
     * Devuelve las opciones por defecto de un selector booleano.
     *
     * @param {object} [columnConfig={}] - Configuración de columna.
     * @returns {Array<{value: string, label: string}>} Opciones disponibles.
     */
    _getDefaultBooleanOptions(columnConfig = {}) {
        const booleanConfig = this._getBooleanConfig(columnConfig);

        return [
            { value: "", label: "Todos" },
            { value: "true", label: booleanConfig.display.true },
            { value: "false", label: booleanConfig.display.false }
        ];
    }

    /**
     * Convierte un valor lógico booleano al valor CRUD configurado.
     *
     * @param {string} logicalValue - Valor lógico (`true` o `false`).
     * @param {object} [columnConfig={}] - Configuración booleana.
     * @returns {*} Valor persistible correspondiente.
     */
    _mapBooleanLogicalValueToCrudValue(logicalValue, columnConfig = {}) {
        const booleanConfig = this._getBooleanConfig(columnConfig);

        if (logicalValue === "true") {
            return booleanConfig.values.true;
        }

        if (logicalValue === "false") {
            return booleanConfig.values.false;
        }

        return logicalValue;
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
     * Determina si un valor debe considerarse vacío a efectos de filtrado.
     *
     * @param {*} value - Valor a evaluar.
     * @returns {boolean} `true` si no aporta contenido útil.
     */
    _isEmptyValue(value) {
        return value === undefined || value === null || String(value).trim() === "";
    }

    /**
     * Carga las opciones remotas de un selector basado en catálogo.
     *
     * @async
     * @param {HTMLSelectElement} selectElement - Selector a poblar.
     * @param {object} [columnConfig={}] - Configuración de la columna.
     * @returns {Promise<void>}
     */
    async _loadApiValueOptions(selectElement, columnConfig = {}) {
        const masterKey = String(columnConfig.master_key || "").trim().toUpperCase();

        if (!masterKey || !selectElement) {
            return;
        }

        try {
            selectElement.disabled = true;

            const records = await fetchApiValueRecords(
                masterKey,
                { baseUrl: this.apiValueBaseUrl }
            );

            this.apiValueRecords[masterKey] = records;
            this._populateApiValueSelect(selectElement, columnConfig, records);
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "Filtros incompletos",
                fallbackMessage: "No se pudieron cargar los valores del filtro."
            });
            this._populateApiValueError(selectElement);
        } finally {
            selectElement.disabled = false;
        }
    }

    /**
     * Inserta en un selector las opciones recibidas desde la API.
     *
     * @param {HTMLSelectElement} selectElement - Selector destino.
     * @param {object} columnConfig - Configuración de la columna.
     * @param {Array<object>} [records=[]] - Registros del catálogo.
     * @returns {void}
     */
    _populateApiValueSelect(selectElement, columnConfig, records = []) {
        const currentValue = selectElement.value || "";
        const placeholder = columnConfig.filter?.placeholder || "Todos";

        selectElement.innerHTML = "";

        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = placeholder;
        selectElement.appendChild(emptyOption);

        records.forEach((record) => {
            const option = document.createElement("option");
            option.value = record?.ID_ROW ?? record?.id_row ?? "";
            option.textContent = record?.DISPLAY_VALUE ?? record?.display_value ?? "";
            selectElement.appendChild(option);
        });

        if (currentValue) {
            selectElement.value = currentValue;
        }
    }

    /**
     * Deja el selector en un estado de error cuando la carga remota falla.
     *
     * @param {HTMLSelectElement} selectElement - Selector afectado.
     * @returns {void}
     */
    _populateApiValueError(selectElement) {
        selectElement.innerHTML = "";

        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = "No se pudieron cargar los valores";
        selectElement.appendChild(emptyOption);
    }
}

export default RenderTableFilters;
