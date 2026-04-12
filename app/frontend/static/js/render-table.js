import { DateFormatter } from "./formater.js";


export default class RenderTable {

    constructor(options = {}) {
        this.tableName = options.tableName;
        this.entityConfig = options.entityConfig || {};
        this.columns = Array.isArray(options.columns) ? options.columns : [];
        this.buttons = options.buttons || {};
        this.onRowRender = options.onRowRender || null;
        this.onTableRendered = options.onTableRendered || null;
        this.container = this._resolveContainer();
        this.tableElement = null;
        this.tbodyElement = null;
        this.theadElement = null;
        this.data = [];
    }

    /*
        PUBLIC API
    */
    render(data = null) {
        if (data !== null) {
            this.data = Array.isArray(data) ? data : [];
        }

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

    setData(data) {
        this.data = Array.isArray(data) ? data : [];
        this._renderBody();
        return this;
    }

    clear() {
        this.container.innerHTML = "";
    }

    showLoading() {
        this.container.innerHTML = `<div class="alert alert-light mb-0">Cargando...</div>`;
    }

    showError(message = "Error renderizando tabla") {
        this.container.innerHTML = `<div class="alert alert-danger mb-0">${message}</div>`;
    }

    /*
        BUILD
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
    _resolveContainer() {
        const element = document.querySelector(
            `[table_name="${this.tableName}"]`
        );

        if (!element) {
            throw new Error(`No existe table_name="${this.tableName}"`);
        }

        return element;
    }

    _getButtonsEntries() {
        return Object.entries(this.buttons).map(([buttonName, buttonConfig]) => {
            return {
                name: buttonName,
                config: buttonConfig || {}
            };
        });
    }

    _getButtonsByPosition(position) {
        return this._getButtonsEntries().filter((buttonEntry) => {
            const currentPosition = buttonEntry.config.position || "end";
            return currentPosition === position;
        });
    }

    _getVisibleColumnsCount() {
        return this.columns.filter((columnName) => {
            const columnConfig = this.entityConfig[columnName] || {};
            return columnConfig.hidden !== true;
        }).length;
    }

    _getButtonsCount() {
        return this._getButtonsEntries().length;
    }

    _getTotalRenderedColumnsCount() {
        return this._getVisibleColumnsCount() + this._getButtonsCount();
    }

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

    _formatCellValue(value, row, columnName, columnConfig) {
        if (columnConfig.table?.formatter) {
            return columnConfig.table.formatter(
                value,
                row,
                columnName
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
            return value ? "Sí" : "No";
        }

        return String(value);
    }

    _joinClassNames(...classNames) {
        return classNames.filter(Boolean).join(" ");
    }
}