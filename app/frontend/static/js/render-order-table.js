export default class RenderOrderTable {

    constructor(options = {}) {
        this.table = options.table || null;
        this.mode = options.mode || "single";

        if (!this.table) {
            throw new Error("Debes informar la propiedad 'table' en RenderOrderTable.");
        }

        this.orders = {};
    }

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

    setOrders(orders = {}) {
        this.orders = orders || {};
        this.refreshHeaderIndicators();
        return this;
    }

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