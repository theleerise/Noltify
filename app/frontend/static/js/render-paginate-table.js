import RenderTable from "./render-table.js";
import RenderOrderTable from "./render-order-table.js";
import { alertMessage } from "./alert-message.js";


export class RenderPaginateTable extends RenderTable {
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

    _resolveOptionalContainer(attrName, attrValue) {
        if (!attrValue) {
            return null;
        }

        return document.querySelector(`[${attrName}="${attrValue}"]`);
    }

    setFilters(filters = {}) {
        this.filters = filters || {};
        return this;
    }

    setOrders(orders = {}) {
        this.orders = orders || {};
        return this;
    }

    setPage(page = 1) {
        this.page = Number(page) || 1;
        return this;
    }

    setExtraParams(extraParams = {}) {
        this.extraParams = extraParams || {};
        return this;
    }

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

    async reload() {
        return this.load({
            page: this.page,
            filters: this.filters,
            orders: this.orders,
            extraParams: this.extraParams
        });
    }

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

    async applyFilters(filters = {}) {
        this.filters = filters || {};
        this.page = 1;

        return this.load({
            page: 1,
            filters: this.filters
        });
    }

    async applyOrders(orders = {}) {
        this.orders = orders || {};
        this.page = 1;

        return this.load({
            page: 1,
            orders: this.orders
        });
    }

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

    _buildPayload() {
        return {
            filters: this.filters || {},
            orders: this.orders || {},
            page: this.page,
            ...this.extraParams
        };
    }

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
