/**
 * @module render-paginate-table
 * @description Extensión de `RenderTable` orientada a listados remotos.
 * Añade carga desde API, mantenimiento de filtros y órdenes, cálculo de
 * paginación y renderizado del resumen de resultados.
 */

import RenderTable from "./render-table.js";
import RenderOrderTable from "./render-order-table.js";
import { alertMessage } from "./alert-message.js";


/**
 * Tabla paginada que consulta datos remotos y renderiza resumen y paginación.
 */
export class RenderPaginateTable extends RenderTable {

    /**
     * @param {object} [options={}] - Configuración de la tabla paginada.
     * @param {string} options.url - Endpoint de consulta.
     * @param {string} [options.method="GET"] - Método HTTP.
     * @param {number} [options.page=1] - Página inicial.
     * @param {number} [options.rows=0] - Total de filas conocidas.
     * @param {number} [options.rowsPerPage=10] - Filas por página.
     * @param {object} [options.extraParams={}] - Parámetros adicionales.
     * @param {boolean} [options.autoLoad=true] - Indica si debe cargar automáticamente.
     */
    constructor(options = {}) {
        super(options);

        this.url = options.url || null;
        this.method = (options.method || "GET").toUpperCase();
        this.page = Number(options.page || 1);
        this.rows = Number(options.rows || 0);
        this.rowsPerPage = Number(options.rowsPerPage || 10);
        this.totalPages = 1;

        this.filters = {};
        this.orders = {};
        this.extraParams = options.extraParams || {};
        this.autoLoad = options.autoLoad !== false;

        this.paginationContainerName = options.paginationContainerName || `${this.tableName}-pagination`;
        this.summaryContainerName = options.summaryContainerName || `${this.tableName}-summary`;

        this.beforeFetch = typeof options.beforeFetch === "function" ? options.beforeFetch : null;
        this.afterFetch = typeof options.afterFetch === "function" ? options.afterFetch : null;
        this.onFetchError = typeof options.onFetchError === "function" ? options.onFetchError : null;

        this.paginationContainer = this._resolveOptionalContainer("pagination_name", this.paginationContainerName);
        this.summaryContainer = this._resolveOptionalContainer("summary_name", this.summaryContainerName);

        this.orderManager = new RenderOrderTable({
            table: this,
            mode: "single"
        });

        if (!this.url) {
            throw new Error("Debes informar la propiedad 'url' para RenderPaginateTable.");
        }

        if (this.autoLoad) {
            this.load();
        }
    }

    /**
     * Resuelve un contenedor opcional a partir de un atributo del DOM.
     *
     * @param {string} attrName - Nombre del atributo a buscar.
     * @param {string} attrValue - Valor esperado del atributo.
     * @returns {HTMLElement|null} Contenedor encontrado o `null`.
     */
    _resolveOptionalContainer(attrName, attrValue) {
        if (!attrValue) {
            return null;
        }

        return document.querySelector(`[${attrName}="${attrValue}"]`);
    }

    /**
     * Define los filtros actuales sin lanzar carga.
     *
     * @param {Object<string, object>} [filters={}] - Mapa de filtros.
     * @returns {RenderPaginateTable} Instancia actual.
     */
    setFilters(filters = {}) {
        this.filters = filters || {};
        return this;
    }

    /**
     * Define los órdenes actuales sin lanzar carga.
     *
     * @param {Object<string, string>} [orders={}] - Mapa de órdenes.
     * @returns {RenderPaginateTable} Instancia actual.
     */
    setOrders(orders = {}) {
        this.orders = orders || {};
        return this;
    }

    /**
     * Establece la página activa sin lanzar carga.
     *
     * @param {number} [page=1] - Página objetivo.
     * @returns {RenderPaginateTable} Instancia actual.
     */
    setPage(page = 1) {
        this.page = Number(page) || 1;
        return this;
    }

    /**
     * Define parámetros adicionales para futuras consultas.
     *
     * @param {object} [extraParams={}] - Parámetros extra.
     * @returns {RenderPaginateTable} Instancia actual.
     */
    setExtraParams(extraParams = {}) {
        this.extraParams = extraParams || {};
        return this;
    }

    /**
     * Carga datos desde el servidor y renderiza tabla, resumen y paginación.
     *
     * @async
     * @param {{page?: number|null, filters?: object|null, orders?: object|null, extraParams?: object|null}} [options={}] - Estado a aplicar antes de la consulta.
     * @returns {Promise<object>} Respuesta JSON de la API.
     */
    async load({ page = null, filters = null, orders = null, extraParams = null } = {}) {
        if (page !== null) {
            this.page = Number(page) || 1;
        }

        if (filters !== null) {
            this.filters = filters || {};
        }

        if (orders !== null) {
            this.orders = orders || {};
        }

        if (extraParams !== null) {
            this.extraParams = extraParams || {};
        }

        try {
            this.showLoading();

            if (this.beforeFetch) {
                this.beforeFetch(this);
            }

            const responseData = await this._fetchData();

            this.data = Array.isArray(responseData.data) ? responseData.data : [];
            this.rows = Number(responseData.rows || 0);
            this.page = Number(responseData.page || this.page || 1);
            this.totalPages = Math.max(1, Math.ceil(this.rows / this.rowsPerPage));

            this.render();
            this.orderManager.setOrders(this.orders);
            this.orderManager.bind();

            this.renderPagination();
            this.renderSummary();

            if (this.afterFetch) {
                this.afterFetch(responseData, this);
            }

            return responseData;
        } catch (error) {
            const errorMessage = error?.message || "No se pudo cargar la tabla.";

            this.showError(errorMessage);
            alertMessage.notifyError(error, {
                title: "Error al cargar datos",
                fallbackMessage: errorMessage
            });

            if (this.paginationContainer) {
                this.paginationContainer.innerHTML = "";
            }

            if (this.summaryContainer) {
                this.summaryContainer.innerHTML = `
                    <div class="alert alert-danger mb-0">${errorMessage}</div>
                `;
            }

            if (this.onFetchError) {
                this.onFetchError(error, this);
            }

            throw error;
        }
    }

    /**
     * Recarga la tabla conservando página, filtros, órdenes y parámetros actuales.
     *
     * @async
     * @returns {Promise<object>}
     */
    async reload() {
        return this.load({
            page: this.page,
            filters: this.filters,
            orders: this.orders,
            extraParams: this.extraParams
        });
    }

    /**
     * Navega a una página concreta.
     *
     * @async
     * @param {number} page - Página destino.
     * @returns {Promise<object>|undefined}
     */
    async goToPage(page) {
        const targetPage = Number(page) || 1;

        if (targetPage < 1) {
            return;
        }

        if (targetPage > this.totalPages) {
            return;
        }

        return this.load({
            page: targetPage
        });
    }

    /**
     * Aplica filtros y reinicia la paginación a la primera página.
     *
     * @async
     * @param {Object<string, object>} [filters={}] - Filtros a aplicar.
     * @returns {Promise<object>}
     */
    async applyFilters(filters = {}) {
        this.filters = filters || {};
        this.page = 1;

        return this.load({
            page: 1,
            filters: this.filters
        });
    }

    /**
     * Aplica un nuevo orden y reinicia la paginación a la primera página.
     *
     * @async
     * @param {Object<string, string>} [orders={}] - Órdenes a aplicar.
     * @returns {Promise<object>}
     */
    async applyOrders(orders = {}) {
        this.orders = orders || {};
        this.page = 1;

        return this.load({
            page: 1,
            orders: this.orders
        });
    }

    /**
     * Ejecuta la petición remota según el método HTTP configurado.
     *
     * @async
     * @returns {Promise<object>} Respuesta normalizada de la API.
     */
    async _fetchData() {
        if (this.method === "GET") {
            const url = this._buildGetUrl();
            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            return this._handleResponse(response);
        }

        const response = await fetch(this.url, {
            method: this.method,
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify(this._buildPayload())
        });

        return this._handleResponse(response);
    }

    /**
     * Construye la URL final para peticiones GET con filtros y paginación.
     *
     * @returns {string} URL lista para consultar.
     */
    _buildGetUrl() {
        const urlObject = new URL(this.url, window.location.origin);

        urlObject.searchParams.set("page", this.page);

        const mergedPayload = this._buildPayload();

        if (mergedPayload.filters) {
            urlObject.searchParams.set("filters", JSON.stringify(mergedPayload.filters));
        }

        if (mergedPayload.orders) {
            urlObject.searchParams.set("orders", JSON.stringify(mergedPayload.orders));
        }

        for (const [paramName, paramValue] of Object.entries(this.extraParams || {})) {
            if (paramValue === null || paramValue === undefined) {
                continue;
            }

            urlObject.searchParams.set(paramName, String(paramValue));
        }

        return urlObject.toString();
    }

    /**
     * Compone el payload base de consulta con filtros, órdenes y extras.
     *
     * @returns {object} Carga útil de la petición.
     */
    _buildPayload() {
        return {
            filters: this.filters || {},
            orders: this.orders || {},
            page: this.page,
            ...this.extraParams
        };
    }

    /**
     * Interpreta la respuesta HTTP y valida que el JSON sea correcto.
     *
     * @async
     * @param {Response} response - Respuesta recibida de `fetch`.
     * @returns {Promise<object>} JSON parseado.
     * @throws {Error} Cuando la respuesta no es válida o llega con error.
     */
    async _handleResponse(response) {
        let responseJson = null;

        try {
            responseJson = await response.json();
        } catch (error) {
            throw new Error("La respuesta del servidor no es un JSON válido.");
        }

        if (!response.ok) {
            throw new Error(responseJson?.error || "Error al consultar la API.");
        }

        return responseJson;
    }

    /**
     * Renderiza los controles de paginación.
     *
     * @returns {void}
     */
    renderPagination() {
        if (!this.paginationContainer) {
            return;
        }

        this.paginationContainer.innerHTML = "";

        if (this.totalPages <= 1) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "rt-pagination d-flex align-items-center gap-2 flex-wrap";

        wrapper.appendChild(this._createPaginationButton("«", 1, this.page === 1));
        wrapper.appendChild(this._createPaginationButton("‹", this.page - 1, this.page === 1));

        for (const pageNumber of this._getPagesToRender()) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = this._joinClassNames(
                "btn",
                "btn-sm",
                pageNumber === this.page ? "btn-primary" : "btn-outline-primary"
            );
            button.textContent = String(pageNumber);

            button.addEventListener("click", () => {
                this.goToPage(pageNumber);
            });

            wrapper.appendChild(button);
        }

        wrapper.appendChild(this._createPaginationButton("›", this.page + 1, this.page >= this.totalPages));
        wrapper.appendChild(this._createPaginationButton("»", this.totalPages, this.page >= this.totalPages));

        this.paginationContainer.appendChild(wrapper);
    }

    /**
     * Renderiza el resumen textual del rango visible y del total de registros.
     *
     * @returns {void}
     */
    renderSummary() {
        if (!this.summaryContainer) {
            return;
        }

        const startRow = this.rows === 0 ? 0 : ((this.page - 1) * this.rowsPerPage) + 1;
        const endRow = Math.min(this.page * this.rowsPerPage, this.rows);

        this.summaryContainer.innerHTML = `
            <div class="rt-summary text-muted">
                Mostrando ${startRow} - ${endRow} de ${this.rows} registros.
            </div>
        `;
    }

    /**
     * Crea un botón de navegación de paginación.
     *
     * @param {string} label - Texto visible del botón.
     * @param {number} page - Página destino.
     * @param {boolean} [disabled=false] - Indica si debe estar deshabilitado.
     * @returns {HTMLButtonElement} Botón generado.
     */
    _createPaginationButton(label, page, disabled = false) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-sm btn-outline-secondary";
        button.textContent = label;
        button.disabled = disabled;

        button.addEventListener("click", () => {
            if (!disabled) {
                this.goToPage(page);
            }
        });

        return button;
    }

    /**
     * Calcula el conjunto de páginas que deben mostrarse en la paginación.
     *
     * @returns {number[]} Lista ordenada de páginas visibles.
     */
    _getPagesToRender() {
        const totalPages = this.totalPages;
        const currentPage = this.page;
        const pages = new Set();

        pages.add(1);
        pages.add(totalPages);

        for (let currentNumber = currentPage - 2; currentNumber <= currentPage + 2; currentNumber++) {
            if (currentNumber >= 1 && currentNumber <= totalPages) {
                pages.add(currentNumber);
            }
        }

        return [...pages].sort((left, right) => left - right);
    }
}

export default RenderPaginateTable;
