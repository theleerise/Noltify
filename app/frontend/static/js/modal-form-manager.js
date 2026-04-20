import { alertMessage } from "./alert-message.js";

export default class ModalFormManager {
    constructor(options = {}) {
        this.containerName = options.containerName;
        this.container = document.querySelector(`#${this.containerName}`);

        if (!this.containerName || !this.container) {
            throw new Error("Debes indicar un containerName válido");
        }

        this.entityConfig = options.entityConfig || {};
        this.formUrl = options.formUrl || null;
        this.dataUrls = options.dataUrls || {};
        this.submitUrl = options.submitUrl || null;
        this.headers = options.headers || {};
        this.mode = options.mode || "new";

        this.modal = null;
        this.modalElement = null;
        this.modalDialog = null;
        this.modalHeader = null;
        this.maximizeButton = null;
        this.formElement = null;
        this.currentId = null;
        this.initialData = {};
        this.windowState = {
            isDragging: false,
            isMaximized: false,
            startX: 0,
            startY: 0,
            startLeft: 0,
            startTop: 0,
            bounds: null,
            restorePosition: null
        };

        this._boundHandleDragMove = this._handleDragMove.bind(this);
        this._boundStopDragging = this._stopDragging.bind(this);

        this.onLoad = options.onLoad || null;
        this.onAfterHtmlLoad = options.onAfterHtmlLoad || null;
        this.onAfterPrefill = options.onAfterPrefill || null;
        this.onBeforeSubmit = options.onBeforeSubmit || null;
        this.onSuccess = options.onSuccess || null;
        this.onError = options.onError || null;
        this.onClose = options.onClose || null;

        this.modalConfig = Object.assign(
            {
                id: `${this.containerName}-modal`,
                titleNew: "Nuevo registro",
                titleEdit: "Editar registro",
                titleShow: "Detalle",
                size: "modal-lg",
                backdrop: "static",
                keyboard: false,
                saveButtonText: "Guardar",
                closeButtonText: "Cerrar",
                resetButtonText: "Limpiar",
                showFooter: true
            },
            options.modal || {}
        );

        this._ensureDraggableStyles();
        this._ensureModal();
    }

    async openNew(paramsUrl = null) {
        try {
            this.mode = "new";
            this.currentId = null;

            await this._loadFormHtml(paramsUrl);
            this._applyConfigToForm();

            const data = await this._loadData("new");
            if (data) {
                this.setData(data);
            } else {
                this._applyDefaults();
            }

            this._snapshotInitialData();
            this._updateModalTitle();
            this._toggleFooterByMode();
            this._showModal();
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "No se pudo abrir el formulario",
                fallbackMessage: "No se pudo preparar el formulario para crear el registro."
            });
            throw error;
        }
    }

    async openEdit(id, paramsUrl = null) {
        try {
            this.mode = "edit";
            this.currentId = id;

            await this._loadFormHtml(paramsUrl);
            this._applyConfigToForm();

            const data = await this._loadData("edit", id);
            if (data) {
                this.setData(data);
            }

            this._snapshotInitialData();
            this._updateModalTitle();
            this._toggleFooterByMode();
            this._showModal();
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "No se pudo abrir el formulario",
                fallbackMessage: "No se pudo cargar el registro solicitado."
            });
            throw error;
        }
    }

    async openShow(id, paramsUrl = null) {
        try {
            this.mode = "show";
            this.currentId = id;

            await this._loadFormHtml(paramsUrl);
            this._applyConfigToForm();

            const data = await this._loadData("show", id);
            if (data) {
                this.setData(data);
            }

            this.setReadOnly(true);
            this._snapshotInitialData();
            this._updateModalTitle();
            this._toggleFooterByMode();
            this._showModal();
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "No se pudo abrir el detalle",
                fallbackMessage: "No se pudo cargar la informacion del registro."
            });
            throw error;
        }
    }

    close() {
        if (this.modal) {
            this.modal.hide();
        }
    }

    reset() {
        if (!this.formElement) return;
        this.setData(this.initialData);
        this.formElement.classList.remove("was-validated");
    }

    setReadOnly(flag = true) {
        if (!this.formElement) return;

        const elements = this.formElement.querySelectorAll("input, select, textarea, button");
        elements.forEach((element) => {
            if (element.dataset.ignoreReadonly === "true") {
                return;
            }

            if (element.tagName === "BUTTON") {
                if (element.type === "submit" || element.dataset.role === "save") {
                    element.disabled = flag;
                }
                return;
            }

            if (flag) {
                element.setAttribute("disabled", "disabled");
            } else {
                const fieldName = element.name;
                const fieldConfig = this.entityConfig[fieldName] || {};

                if (fieldConfig.readonly) {
                    element.setAttribute("disabled", "disabled");
                } else {
                    element.removeAttribute("disabled");
                }
            }
        });
    }

    setData(data = {}) {
        if (!this.formElement) return;

        Object.entries(data).forEach(([fieldName, fieldValue]) => {
            const input = this._findField(fieldName);
            if (!input) return;

            this._writeFieldValue(input, fieldValue, fieldName);
        });

        if (typeof this.onAfterPrefill === "function") {
            this.onAfterPrefill(data, this.mode, this);
        }
    }

    getData() {
        if (!this.formElement) return {};

        const data = {};
        const fields = this.formElement.querySelectorAll("[name]");

        fields.forEach((field) => {
            const fieldName = field.name;
            if (!fieldName) return;

            if (this._isFileField(field)) {
                return;
            }

            if (field.type === "radio") {
                if (!Object.prototype.hasOwnProperty.call(data, fieldName)) {
                    data[fieldName] = this._readFieldValue(field, fieldName);
                }
                return;
            }

            data[fieldName] = this._readFieldValue(field, fieldName);
        });

        return this._normalizeDataByConfig(data);
    }

    hasChanges() {
        const currentData = this.getData();
        return JSON.stringify(currentData) !== JSON.stringify(this.initialData);
    }

    async save(method = null) {
        try {
            if (!this.formElement) {
                throw new Error("No hay formulario cargado");
            }

            if (!this.formElement.checkValidity()) {
                this.formElement.classList.add("was-validated");
                alertMessage.warning("Revisa los campos obligatorios antes de guardar.", {
                    title: "Formulario incompleto"
                });
                return;
            }

            let payload = this.getData();

            if (typeof this.onBeforeSubmit === "function") {
                const modifiedPayload = await this.onBeforeSubmit(payload, this.mode, this.currentId, this);
                if (modifiedPayload === false) {
                    return;
                }
                if (modifiedPayload && typeof modifiedPayload === "object") {
                    payload = modifiedPayload;
                }
            }

            const finalUrl = typeof this.submitUrl === "function"
                ? this.submitUrl(this.mode, this.currentId)
                : this.submitUrl;

            if (!finalUrl) {
                throw new Error("No se ha definido submitUrl");
            }

            const finalMethod = method || (this.mode === "new" ? "POST" : "PUT");
            const shouldUseMultipart = this._hasSelectedFiles();

            const requestConfig = {
                method: finalMethod,
                headers: {
                    ...this.headers
                }
            };

            if (shouldUseMultipart) {
                requestConfig.body = this._buildMultipartPayload(payload);
            } else {
                requestConfig.headers["Content-Type"] = "application/json";
                requestConfig.body = JSON.stringify({
                    mode: this.mode,
                    id: this.currentId,
                    data: payload
                });
            }

            const response = await fetch(finalUrl, requestConfig);

            const json = await this._safeJson(response);

            if (!response.ok) {
                throw new Error(json?.error || json?.message || `Error HTTP ${response.status}`);
            }

            this._snapshotInitialData();
            alertMessage.notifyResponse(json, {
                type: "success"
            });

            if (typeof this.onSuccess === "function") {
                this.onSuccess(json, this);
            }

            return json;
        } catch (error) {
            alertMessage.notifyError(error, {
                title: "No se pudo guardar",
                fallbackMessage: "La operacion no pudo completarse."
            });
            if (typeof this.onError === "function") {
                this.onError(error, this);
            } else {
                console.error(error);
            }
            throw error;
        }
    }

    async _loadFormHtml(paramsUrl = null) {
        if (!this.formUrl) {
            throw new Error("No se ha definido formUrl");
        }

        let url = this.formUrl;

        if (paramsUrl) {
            const queryString = new URLSearchParams(paramsUrl).toString();
            url = `${url}${url.includes("?") ? "&" : "?"}${queryString}`;
        }

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "text/html"
            },
            credentials: "include"
        });

        if (!response.ok) {
            throw new Error(`No se pudo cargar el formulario. HTTP ${response.status}`);
        }

        const html = await response.text();
        const modalBody = this.modalElement.querySelector(".modal-body");

        modalBody.innerHTML = html;

        await this._executeEmbeddedScripts(modalBody);

        this.formElement = modalBody.querySelector("form") || modalBody;

        this._bindInternalEvents();

        if (typeof this.onAfterHtmlLoad === "function") {
            this.onAfterHtmlLoad(html, this);
        }

        if (typeof this.onLoad === "function") {
            this.onLoad(this.mode, this.currentId, this);
        }
    }

    async _executeEmbeddedScripts(scopeElement) {
        const scripts = Array.from(scopeElement.querySelectorAll("script"));

        for (const oldScript of scripts) {
            const newScript = document.createElement("script");

            for (const attribute of Array.from(oldScript.attributes)) {
                newScript.setAttribute(attribute.name, attribute.value);
            }

            if (oldScript.src) {
                await new Promise((resolve, reject) => {
                    newScript.onload = resolve;
                    newScript.onerror = reject;
                    oldScript.parentNode.replaceChild(newScript, oldScript);
                });
            } else {
                newScript.textContent = oldScript.textContent;
                oldScript.parentNode.replaceChild(newScript, oldScript);
            }
        }
    }

    async _loadData(mode, id = null) {
        let url = null;

        if (mode === "new" && this.dataUrls.new) {
            url = typeof this.dataUrls.new === "function"
                ? this.dataUrls.new()
                : this.dataUrls.new;
        }

        if ((mode === "edit" || mode === "show") && this.dataUrls.edit) {
            url = typeof this.dataUrls.edit === "function"
                ? this.dataUrls.edit(id)
                : this.dataUrls.edit;
        }

        if (!url) {
            return null;
        }

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            credentials: "include"
        });

        const json = await this._safeJson(response);

        if (!response.ok) {
            throw new Error(json?.error || json?.message || `No se pudo cargar el registro. HTTP ${response.status}`);
        }

        return json?.data || json;
    }

    _applyConfigToForm() {
        if (!this.formElement) return;

        Object.entries(this.entityConfig).forEach(([fieldName, fieldConfig]) => {
            const field = this._findField(fieldName);
            if (!field) return;

            const isRequired = fieldConfig.required === true
                || (fieldConfig.required_on_create === true && this.mode === "new");

            if (isRequired) {
                field.setAttribute("required", "required");
            } else {
                field.removeAttribute("required");
            }

            if (fieldConfig.readonly === true) {
                field.setAttribute("disabled", "disabled");
            }

            if (fieldConfig.placeholder) {
                field.setAttribute("placeholder", fieldConfig.placeholder);
            }

            if (fieldConfig.maxlength) {
                field.setAttribute("maxlength", fieldConfig.maxlength);
            }

            if (fieldConfig.minlength) {
                field.setAttribute("minlength", fieldConfig.minlength);
            }

            if (fieldConfig.min !== undefined) {
                field.setAttribute("min", fieldConfig.min);
            }

            if (fieldConfig.max !== undefined) {
                field.setAttribute("max", fieldConfig.max);
            }

            if (fieldConfig.step !== undefined) {
                field.setAttribute("step", fieldConfig.step);
            }

            if (field.tagName === "TEXTAREA" && fieldConfig.rows) {
                field.setAttribute("rows", fieldConfig.rows);
            }

            if (fieldConfig.className) {
                field.classList.add(...fieldConfig.className.split(" "));
            }

            if (fieldConfig.create_only === true) {
                const isNewMode = this.mode === "new";
                this._toggleFieldVisibility(fieldName, isNewMode);

                if (isNewMode) {
                    field.removeAttribute("disabled");
                    if (fieldConfig.required === true) {
                        field.setAttribute("required", "required");
                    }
                } else {
                    field.setAttribute("disabled", "disabled");
                    field.removeAttribute("required");
                }
            }

            if (fieldConfig.type === "boolean") {
                this._applyBooleanFieldConfig(field, fieldName, fieldConfig);
            }
        });
    }

    _applyDefaults() {
        if (!this.formElement) return;

        Object.entries(this.entityConfig).forEach(([fieldName, fieldConfig]) => {
            if (!Object.prototype.hasOwnProperty.call(fieldConfig, "default")) {
                return;
            }

            const field = this._findField(fieldName);
            if (!field) return;

            this._writeFieldValue(field, fieldConfig.default, fieldName);
        });
    }

    _normalizeDataByConfig(data) {
        const normalized = {};

        Object.entries(data).forEach(([fieldName, value]) => {
            const fieldConfig = this.entityConfig[fieldName] || {};
            const fieldType = fieldConfig.type || "string";

            if (value === "" || value === undefined) {
                normalized[fieldName] = null;
                return;
            }

            switch (fieldType) {
                case "integer":
                    normalized[fieldName] = Number.isFinite(Number(value)) ? parseInt(value, 10) : null;
                    break;

                case "number":
                case "decimal":
                    normalized[fieldName] = Number.isFinite(Number(value)) ? Number(value) : null;
                    break;

                case "boolean":
                    normalized[fieldName] = this._normalizeBooleanValue(value, fieldConfig);
                    break;

                case "date":
                case "datetime":
                case "time":
                    normalized[fieldName] = value;
                    break;

                default:
                    normalized[fieldName] = value;
                    break;
            }
        });

        return normalized;
    }

    _findField(fieldName) {
        if (!this.formElement) return null;

        return this.formElement.querySelector(`[name="${fieldName}"]`)
            || this.formElement.querySelector(`[data-field="${fieldName}"]`)
            || this.formElement.querySelector(`#id_${fieldName}`);
    }

    _readFieldValue(field, fieldName = null) {
        if (!field) return null;

        const tagName = field.tagName.toLowerCase();
        const type = (field.type || "").toLowerCase();
        const fieldConfig = this.entityConfig[fieldName || field.name] || {};

        if (tagName === "input") {
            if (type === "file") {
                return null;
            }

            if (type === "checkbox") {
                return this._normalizeBooleanValue(field.checked, fieldConfig);
            }

            if (type === "radio") {
                const checked = this.formElement.querySelector(`input[name="${field.name}"]:checked`);
                if (!checked) {
                    return null;
                }

                if (fieldConfig.type === "boolean") {
                    return this._normalizeBooleanValue(checked.value, fieldConfig);
                }

                return checked.value;
            }

            return field.value;
        }

        if (tagName === "select") {
            if (field.dataset.apiValueSelect === "true") {
                const selectedValue = field.value
                    || field.dataset.selectedValue
                    || field.dataset.initialValue
                    || "";

                if (field.multiple) {
                    return Array.from(field.selectedOptions).map((option) => option.value);
                }

                if (fieldConfig.type === "boolean") {
                    return this._normalizeBooleanValue(selectedValue, fieldConfig);
                }

                return selectedValue;
            }

            if (field.multiple) {
                return Array.from(field.selectedOptions).map((option) => option.value);
            }

            if (fieldConfig.type === "boolean") {
                return this._normalizeBooleanValue(field.value, fieldConfig);
            }

            return field.value;
        }

        if (tagName === "textarea") {
            return field.value;
        }

        return null;
    }

    _writeFieldValue(field, value, fieldName = null) {
        const tagName = field.tagName.toLowerCase();
        const type = (field.type || "").toLowerCase();
        const fieldConfig = this.entityConfig[fieldName || field.name] || {};

        if (tagName === "input") {
            if (type === "file") {
                return;
            }

            if (type === "checkbox") {
                field.checked = this._resolveBooleanLogicalValue(value, fieldConfig) === "true";
                return;
            }

            if (type === "radio") {
                const logicalValue = fieldConfig.type === "boolean"
                    ? this._resolveBooleanLogicalValue(value, fieldConfig)
                    : value;

                const radio = this.formElement.querySelector(`input[name="${field.name}"][value="${logicalValue}"]`);
                if (radio) {
                    radio.checked = true;
                }
                return;
            }

            if (type === "datetime-local") {
                field.value = this._toDatetimeLocal(value);
                return;
            }

            field.value = value ?? "";
            return;
        }

        if (tagName === "select") {
            if (field.dataset.apiValueSelect === "true") {
                field.dataset.selectedValue = value ?? "";
                field.dataset.initialValue = value ?? "";
            }

            if (field.multiple && Array.isArray(value)) {
                Array.from(field.options).forEach((option) => {
                    option.selected = value.includes(option.value);
                });
            } else {
                if (fieldConfig.type === "boolean") {
                    const logicalValue = this._resolveBooleanLogicalValue(value, fieldConfig);
                    field.value = logicalValue ?? "";
                } else {
                    field.value = value ?? "";
                }
            }

            field.dispatchEvent(new Event("change", { bubbles: true }));
            return;
        }

        if (tagName === "textarea") {
            field.value = value ?? "";

            const richEditor = field.id
                ? this.formElement.querySelector(`[data-rich-editor][data-textarea-id="${field.id}"]`)
                : null;

            if (richEditor) {
                richEditor.innerHTML = value ?? "";
                richEditor.dispatchEvent(new Event("input", { bubbles: true }));
            }
        }
    }

    _toDatetimeLocal(value) {
        if (!value) return "";
        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    _snapshotInitialData() {
        this.initialData = this.getData();
    }

    _buildMultipartPayload(payload) {
        const formData = new FormData();
        formData.append("mode", this.mode);

        if (this.currentId !== null && this.currentId !== undefined) {
            formData.append("id", String(this.currentId));
        }

        formData.append("data", JSON.stringify(payload));

        const fileFields = this.formElement.querySelectorAll('input[type="file"][name]');
        fileFields.forEach((field) => {
            if (!field.files || field.files.length === 0) {
                return;
            }

            Array.from(field.files).forEach((file) => {
                formData.append(field.name, file);
            });
        });

        return formData;
    }

    _hasSelectedFiles() {
        if (!this.formElement) return false;

        return Array.from(this.formElement.querySelectorAll('input[type="file"]'))
            .some((field) => field.files && field.files.length > 0);
    }

    _isFileField(field) {
        return field?.tagName?.toLowerCase() === "input"
            && (field.type || "").toLowerCase() === "file";
    }

    _toggleFieldVisibility(fieldName, visible) {
        const wrapper = this.formElement?.querySelector(`[data-field-wrapper="${fieldName}"]`);
        if (!wrapper) return;

        wrapper.classList.toggle("d-none", !visible);
    }

    _bindInternalEvents() {
        if (!this.formElement) return;

        this.formElement.addEventListener("submit", async (event) => {
            event.preventDefault();
            await this.save();
        });

        const resetButtons = this.modalElement.querySelectorAll('[data-role="reset"]');
        resetButtons.forEach((button) => {
            button.onclick = () => this.reset();
        });

        const saveButtons = this.modalElement.querySelectorAll('[data-role="save"]');
        saveButtons.forEach((button) => {
            button.onclick = async () => {
                await this.save();
            };
        });
    }

    _toggleFooterByMode() {
        const footer = this.modalElement.querySelector(".modal-footer");
        const saveButton = this.modalElement.querySelector('[data-role="save"]');
        const resetButton = this.modalElement.querySelector('[data-role="reset"]');

        if (!footer) return;

        if (this.modalConfig.showFooter === false) {
            footer.classList.add("d-none");
            return;
        }

        footer.classList.remove("d-none");

        if (this.mode === "show") {
            if (saveButton) saveButton.classList.add("d-none");
            if (resetButton) resetButton.classList.add("d-none");
        } else {
            if (saveButton) saveButton.classList.remove("d-none");
            if (resetButton) resetButton.classList.remove("d-none");
        }
    }

    _updateModalTitle() {
        const titleElement = this.modalElement.querySelector(".modal-title");
        if (!titleElement) return;

        if (this.mode === "new") {
            titleElement.textContent = this.modalConfig.titleNew;
            return;
        }

        if (this.mode === "edit") {
            titleElement.textContent = this.modalConfig.titleEdit;
            return;
        }

        if (this.mode === "show") {
            titleElement.textContent = this.modalConfig.titleShow;
        }
    }

    _showModal() {
        this.modal.show();
    }

    _ensureDraggableStyles() {
        if (document.getElementById("modal-form-manager-window-styles")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "modal-form-manager-window-styles";
        style.textContent = `
            .draggable-form-modal .modal-dialog {
                position: fixed;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                margin: 0;
                transition: none !important;
            }

            .draggable-form-modal .modal-content {
                max-height: calc(100vh - 32px);
                display: flex;
                flex-direction: column;
            }

            .draggable-form-modal .modal-body {
                overflow: auto;
                -webkit-overflow-scrolling: touch;
            }

            .draggable-form-modal .modal-header {
                display: flex;
                align-items: center;
                cursor: move;
                user-select: none;
            }

            .draggable-form-modal .modal-title {
                flex: 1 1 auto;
                min-width: 0;
                margin-bottom: 0;
                padding-right: 12px;
            }

            .draggable-form-modal .modal-window-actions {
                margin-left: auto;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex: 0 0 auto;
            }

            .draggable-form-modal .modal-window-actions button {
                cursor: pointer;
            }

            .draggable-form-modal.is-maximized .modal-dialog {
                left: 16px !important;
                top: 16px !important;
                right: 16px !important;
                bottom: 16px !important;
                width: auto !important;
                height: auto !important;
                max-width: none !important;
                transform: none !important;
            }

            .draggable-form-modal.is-maximized .modal-content {
                height: 100%;
                max-height: none;
            }

            .draggable-form-modal.is-maximized .modal-body {
                flex: 1 1 auto;
            }
        `;

        document.head.appendChild(style);
    }

    _ensureModal() {
        if (document.getElementById(this.modalConfig.id)) {
            this.modalElement = document.getElementById(this.modalConfig.id);
            this.modal = bootstrap.Modal.getOrCreateInstance(this.modalElement, {
                backdrop: this.modalConfig.backdrop,
                keyboard: this.modalConfig.keyboard
            });
            this._cacheModalWindowElements();
            this._bindModalWindowEvents();
            return;
        }

        const html = `
            <div class="modal fade draggable-form-modal" id="${this.modalConfig.id}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog ${this.modalConfig.size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"></h5>
                            <div class="modal-window-actions">
                                <button
                                    type="button"
                                    class="btn btn-sm btn-link text-body text-decoration-none p-0"
                                    data-role="toggle-maximize"
                                    aria-label="Maximizar"
                                    title="Maximizar"
                                >
                                    <i class="bi bi-fullscreen"></i>
                                </button>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                            </div>
                        </div>
                        <div class="modal-body"></div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-role="reset">
                                ${this.modalConfig.resetButtonText}
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                ${this.modalConfig.closeButtonText}
                            </button>
                            <button type="button" class="btn btn-primary" data-role="save">
                                ${this.modalConfig.saveButtonText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.container.insertAdjacentHTML("beforeend", html);

        this.modalElement = document.getElementById(this.modalConfig.id);
        this.modal = new bootstrap.Modal(this.modalElement, {
            backdrop: this.modalConfig.backdrop,
            keyboard: this.modalConfig.keyboard
        });
        this._cacheModalWindowElements();
        this._bindModalWindowEvents();
    }

    _cacheModalWindowElements() {
        if (!this.modalElement) return;

        this.modalDialog = this.modalElement.querySelector(".modal-dialog");
        this.modalHeader = this.modalElement.querySelector(".modal-header");
        this.maximizeButton = this.modalElement.querySelector('[data-role="toggle-maximize"]');
    }

    _bindModalWindowEvents() {
        if (!this.modalElement || this.modalElement.dataset.windowEventsBound === "true") {
            return;
        }

        this.modalElement.dataset.windowEventsBound = "true";

        if (this.modalHeader) {
            this.modalHeader.style.cursor = "move";
            this.modalHeader.addEventListener("mousedown", (event) => this._startDragging(event));
        }

        if (this.maximizeButton) {
            this.maximizeButton.addEventListener("click", () => this._toggleMaximize());
        }

        this.modalElement.addEventListener("shown.bs.modal", () => {
            this._setDefaultWindowPosition();
        });

        this.modalElement.addEventListener("hidden.bs.modal", () => {
            this._resetWindowState();

            if (typeof this.onClose === "function") {
                this.onClose(this);
            }
        });
    }

    _setDefaultWindowPosition() {
        if (!this.modalDialog) return;

        this.modalElement.classList.remove("is-maximized");
        this.modalDialog.style.right = "";
        this.modalDialog.style.bottom = "";
        this.modalDialog.style.left = "50%";
        this.modalDialog.style.top = "50%";
        this.modalDialog.style.transform = "translate(-50%, -50%)";
        this.modalDialog.style.width = "";
        this.modalDialog.style.height = "";

        this.windowState.isMaximized = false;
        this.windowState.restorePosition = null;
        this._updateMaximizeButton();
    }

    _startDragging(event) {
        if (!this.modalDialog || this.windowState.isMaximized) {
            return;
        }

        if (event.target.closest(".btn-close, [data-role=\"toggle-maximize\"]")) {
            return;
        }

        const rect = this.modalDialog.getBoundingClientRect();
        const margin = 8;
        const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

        this.modalDialog.style.transform = "none";
        this.modalDialog.style.left = `${rect.left}px`;
        this.modalDialog.style.top = `${rect.top}px`;

        this.windowState.isDragging = true;
        this.windowState.startX = event.clientX;
        this.windowState.startY = event.clientY;
        this.windowState.startLeft = rect.left;
        this.windowState.startTop = rect.top;
        this.windowState.bounds = {
            minLeft: margin,
            maxLeft: window.innerWidth - rect.width - margin,
            minTop: margin,
            maxTop: window.innerHeight - rect.height - margin
        };

        if (this.windowState.bounds.maxLeft < this.windowState.bounds.minLeft) {
            const left = clamp(rect.left, 0, Math.max(window.innerWidth - rect.width, 0));
            this.windowState.bounds.minLeft = left;
            this.windowState.bounds.maxLeft = left;
        }

        if (this.windowState.bounds.maxTop < this.windowState.bounds.minTop) {
            const top = clamp(rect.top, 0, Math.max(window.innerHeight - rect.height, 0));
            this.windowState.bounds.minTop = top;
            this.windowState.bounds.maxTop = top;
        }

        document.addEventListener("mousemove", this._boundHandleDragMove);
        document.addEventListener("mouseup", this._boundStopDragging);
        event.preventDefault();
    }

    _handleDragMove(event) {
        if (!this.windowState.isDragging || !this.modalDialog) {
            return;
        }

        const bounds = this.windowState.bounds || {
            minLeft: 0,
            maxLeft: 0,
            minTop: 0,
            maxTop: 0
        };
        const dx = event.clientX - this.windowState.startX;
        const dy = event.clientY - this.windowState.startY;
        const left = Math.min(Math.max(this.windowState.startLeft + dx, bounds.minLeft), bounds.maxLeft);
        const top = Math.min(Math.max(this.windowState.startTop + dy, bounds.minTop), bounds.maxTop);

        this.modalDialog.style.left = `${left}px`;
        this.modalDialog.style.top = `${top}px`;
    }

    _stopDragging() {
        if (!this.windowState.isDragging) {
            return;
        }

        this.windowState.isDragging = false;
        this.windowState.restorePosition = this._captureCurrentDialogPosition();
        this.windowState.bounds = null;

        document.removeEventListener("mousemove", this._boundHandleDragMove);
        document.removeEventListener("mouseup", this._boundStopDragging);
    }

    _toggleMaximize() {
        if (!this.modalDialog) return;

        if (this.windowState.isMaximized) {
            this.windowState.isMaximized = false;
            this.modalElement.classList.remove("is-maximized");
            this._applyRestoredLayout();
            this._updateMaximizeButton();
            return;
        }

        this.windowState.restorePosition = this._captureCurrentDialogPosition();
        this.windowState.isMaximized = true;
        this.modalElement.classList.add("is-maximized");
        this._updateMaximizeButton();
    }

    _applyRestoredLayout() {
        if (!this.modalDialog) return;

        const restoredPosition = this.windowState.restorePosition;
        if (!restoredPosition) return;

        this.modalDialog.style.transform = "none";
        this.modalDialog.style.right = "";
        this.modalDialog.style.bottom = "";
        this.modalDialog.style.left = `${restoredPosition.left}px`;
        this.modalDialog.style.top = `${restoredPosition.top}px`;
        this.modalDialog.style.width = `${restoredPosition.width}px`;
        this.modalDialog.style.height = "";
    }

    _captureCurrentDialogPosition() {
        if (!this.modalDialog) {
            return null;
        }

        const dialogRect = this.modalDialog.getBoundingClientRect();

        return {
            left: dialogRect.left,
            top: dialogRect.top,
            width: dialogRect.width,
            height: dialogRect.height
        };
    }

    _updateMaximizeButton() {
        if (!this.maximizeButton) return;

        const icon = this.maximizeButton.querySelector("i");
        const isMaximized = this.windowState.isMaximized;

        this.maximizeButton.setAttribute("aria-label", isMaximized ? "Restaurar" : "Maximizar");
        this.maximizeButton.setAttribute("title", isMaximized ? "Restaurar" : "Maximizar");

        if (icon) {
            icon.className = isMaximized ? "bi bi-fullscreen-exit" : "bi bi-fullscreen";
        }
    }

    _resetWindowState() {
        this._stopDragging();

        this.windowState.isMaximized = false;
        this.windowState.restorePosition = null;
        this.windowState.bounds = null;

        if (!this.modalDialog) return;

        this.modalElement.classList.remove("is-maximized");
        this.modalDialog.style.width = "";
        this.modalDialog.style.height = "";
        this.modalDialog.style.left = "";
        this.modalDialog.style.top = "";
        this.modalDialog.style.right = "";
        this.modalDialog.style.bottom = "";
        this.modalDialog.style.transform = "";

        this._updateMaximizeButton();
    }

    async _safeJson(response) {
        try {
            return await response.json();
        } catch (error) {
            return null;
        }
    }

    _applyBooleanFieldConfig(field, fieldName, fieldConfig) {
        const tagName = field.tagName.toLowerCase();
        const type = (field.type || "").toLowerCase();
        const booleanConfig = this._getBooleanConfig(fieldConfig);

        if (tagName === "select") {
            this._populateBooleanSelectOptions(field, booleanConfig);
            return;
        }

        if (tagName === "input" && type === "radio") {
            this._normalizeBooleanRadioValues(fieldName);
            return;
        }
    }

    _populateBooleanSelectOptions(selectElement, booleanConfig) {
        if (!selectElement) return;

        const preserveExistingOptions = selectElement.options.length > 0;

        if (preserveExistingOptions) {
            Array.from(selectElement.options).forEach((option) => {
                if (option.value === "true") {
                    option.textContent = booleanConfig.display.true;
                }
                if (option.value === "false") {
                    option.textContent = booleanConfig.display.false;
                }
            });

            return;
        }

        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = "";
        selectElement.appendChild(emptyOption);

        const trueOption = document.createElement("option");
        trueOption.value = "true";
        trueOption.textContent = booleanConfig.display.true;
        selectElement.appendChild(trueOption);

        const falseOption = document.createElement("option");
        falseOption.value = "false";
        falseOption.textContent = booleanConfig.display.false;
        selectElement.appendChild(falseOption);
    }

    _normalizeBooleanRadioValues(fieldName) {
        const radios = this.formElement.querySelectorAll(`input[name="${fieldName}"]`);

        radios.forEach((radio) => {
            const normalizedLogicalValue = this._normalizeBooleanLogicalValue(radio.value);

            if (normalizedLogicalValue === "true" || normalizedLogicalValue === "false") {
                radio.value = normalizedLogicalValue;
            }
        });
    }

    _normalizeBooleanValue(value, fieldConfig = {}) {
        if (value === null || value === undefined || value === "") {
            return null;
        }

        const booleanConfig = this._getBooleanConfig(fieldConfig);
        const logicalValue = this._resolveBooleanLogicalValue(value, fieldConfig);

        if (logicalValue === "true") {
            return booleanConfig.values.true;
        }

        if (logicalValue === "false") {
            return booleanConfig.values.false;
        }

        return value;
    }

    _resolveBooleanLogicalValue(value, fieldConfig = {}) {
        if (value === null || value === undefined || value === "") {
            return null;
        }

        const booleanConfig = this._getBooleanConfig(fieldConfig);

        if (value === true) {
            return "true";
        }

        if (value === false) {
            return "false";
        }

        if (this._isSameValue(value, booleanConfig.values.true)) {
            return "true";
        }

        if (this._isSameValue(value, booleanConfig.values.false)) {
            return "false";
        }

        return this._normalizeBooleanLogicalValue(value);
    }

    _normalizeBooleanLogicalValue(value) {
        if (value === null || value === undefined || value === "") {
            return null;
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

    _getBooleanConfig(fieldConfig = {}) {
        const booleanConfig = fieldConfig.boolean_config || {};

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

    _isSameValue(leftValue, rightValue) {
        if (leftValue === rightValue) {
            return true;
        }

        if (leftValue === null || leftValue === undefined || rightValue === null || rightValue === undefined) {
            return false;
        }

        return String(leftValue).trim().toLowerCase() === String(rightValue).trim().toLowerCase();
    }
}
