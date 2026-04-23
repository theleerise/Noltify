/**
 * @module render-order-table
 * @description Gestor del orden visual y funcional de tablas renderizadas.
 * Controla el estado de ordenación por columna y sincroniza los indicadores
 * de cabecera con la lógica de carga o refresco de datos.
 */

/**
 * Controla el estado de ordenación de una tabla y actualiza sus indicadores visuales.
 */
export default class RenderOrderTable {

    /**
     * @param {{table: object, mode?: "single"|"multiple"}} [options={}] - Configuración del orden.
     */
    constructor(options = {}) {
        this.table = options.table || null;
        this.mode = options.mode || "single";

        if (!this.table) {
            throw new Error("Debes informar la propiedad 'table' en RenderOrderTable.");
        }

        this.orders = {};
    }

    /**
     * Vincula los eventos de doble clic sobre las cabeceras ordenables.
     *
     * @returns {RenderOrderTable} Instancia actual.
     */
    bind() {
        if (!this.table.theadElement) {
            return this;
        }

        const headerCells = this.table.theadElement.querySelectorAll("th[data-column-name]");

        for (const headerCell of headerCells) {
            headerCell.addEventListener("dblclick", () => {
                const columnName = headerCell.getAttribute("data-column-name");

                if (!columnName) {
                    return;
                }

                this.toggleColumnOrder(columnName);
            });
        }

        this.refreshHeaderIndicators();

        return this;
    }

    /**
     * Alterna el orden de una columna entre ascendente, descendente y sin orden.
     *
     * @param {string} columnName - Nombre de columna.
     * @returns {void}
     */
    toggleColumnOrder(columnName) {
        const currentOrder = this.orders[columnName] || null;
        let nextOrder = null;

        if (currentOrder === null) {
            nextOrder = "ASC";
        } else if (currentOrder === "ASC") {
            nextOrder = "DESC";
        } else {
            nextOrder = null;
        }

        if (this.mode === "single") {
            this.orders = {};
        }

        if (nextOrder) {
            this.orders[columnName] = nextOrder;
        } else {
            delete this.orders[columnName];
        }

        this.refreshHeaderIndicators();

        if (typeof this.table.applyOrders === "function") {
            this.table.applyOrders(this.orders);
        } else if (typeof this.table.load === "function") {
            this.table.load();
        }
    }

    /**
     * Establece un conjunto de órdenes de forma explícita.
     *
     * @param {Object<string, string>} [orders={}] - Mapa columna/orden.
     * @returns {RenderOrderTable} Instancia actual.
     */
    setOrders(orders = {}) {
        this.orders = orders || {};
        this.refreshHeaderIndicators();
        return this;
    }

    /**
     * Elimina todos los criterios de ordenación activos.
     *
     * @returns {RenderOrderTable} Instancia actual.
     */
    clearOrders() {
        this.orders = {};
        this.refreshHeaderIndicators();

        if (typeof this.table.applyOrders === "function") {
            this.table.applyOrders({});
        } else if (typeof this.table.load === "function") {
            this.table.load();
        }

        return this;
    }

    /**
     * Refresca el HTML de las cabeceras para representar el estado del orden.
     *
     * @returns {void}
     */
    refreshHeaderIndicators() {
        if (!this.table.theadElement) {
            return;
        }

        const headerCells = this.table.theadElement.querySelectorAll("th[data-column-name]");

        for (const headerCell of headerCells) {
            const columnName = headerCell.getAttribute("data-column-name");
            const baseTitle = headerCell.getAttribute("data-column-title") || columnName || "";
            const currentOrder = this.orders[columnName] || null;

            headerCell.classList.remove("rt-order-asc", "rt-order-desc");

            if (currentOrder === "ASC") {
                headerCell.classList.add("rt-order-asc");
                headerCell.innerHTML = `${baseTitle} <span class="ms-1">▲</span>`;
            } else if (currentOrder === "DESC") {
                headerCell.classList.add("rt-order-desc");
                headerCell.innerHTML = `${baseTitle} <span class="ms-1">▼</span>`;
            } else {
                headerCell.innerHTML = `${baseTitle}`;
            }
        }
    }
}
