import { alertMessage } from "./alert-message.js";

class CustomModal {
    constructor({
        containerName,
        title = "",
        body = "",
        footer = "",
        size = "",
        closeButton = true,
        destroyOnClose = true,
        backdrop = "static",
        keyboard = false
    } = {}) {
        this.containerName = containerName;
        this.title = title;
        this.body = body;
        this.footer = footer;
        this.size = size;
        this.closeButton = closeButton;
        this.destroyOnClose = destroyOnClose;
        this.backdrop = backdrop;
        this.keyboard = keyboard;

        this.modalId = `custom-modal-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        this.modalElement = null;
        this.modalInstance = null;
        this.modalDialog = null;
        this.modalHeader = null;
        this.maximizeButton = null;
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
        this._ensureDraggableStyles();
    }

    _getContainer() {
        const container = document.getElementById(this.containerName);

        if (!container) {
            throw new Error(`No se encontró el contenedor del modal con id '${this.containerName}'.`);
        }

        return container;
    }

    _getModalHtml() {
        return `
            <div class="modal fade draggable-custom-modal" id="${this.modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog ${this.size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.title}</h5>
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
                                ${this.closeButton
                                    ? '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>'
                                    : ""}
                            </div>
                        </div>
                        <div class="modal-body">
                            ${this.body}
                        </div>
                        <div class="modal-footer">
                            ${this.footer}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    _ensureDraggableStyles() {
        if (document.getElementById("custom-modal-window-styles")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "custom-modal-window-styles";
        style.textContent = `
            .draggable-custom-modal .modal-dialog {
                position: fixed;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                margin: 0;
                transition: none !important;
            }

            .draggable-custom-modal .modal-content {
                max-height: calc(100vh - 32px);
                display: flex;
                flex-direction: column;
            }

            .draggable-custom-modal .modal-body {
                overflow: auto;
                -webkit-overflow-scrolling: touch;
            }

            .draggable-custom-modal .modal-header {
                display: flex;
                align-items: center;
                cursor: move;
                user-select: none;
            }

            .draggable-custom-modal .modal-title {
                flex: 1 1 auto;
                min-width: 0;
                margin-bottom: 0;
                padding-right: 12px;
            }

            .draggable-custom-modal .modal-window-actions {
                margin-left: auto;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex: 0 0 auto;
            }

            .draggable-custom-modal .modal-window-actions button {
                cursor: pointer;
            }

            .draggable-custom-modal.is-maximized .modal-dialog {
                left: 16px !important;
                top: 16px !important;
                right: 16px !important;
                bottom: 16px !important;
                width: auto !important;
                height: auto !important;
                max-width: none !important;
                transform: none !important;
            }

            .draggable-custom-modal.is-maximized .modal-content {
                height: 100%;
                max-height: none;
            }

            .draggable-custom-modal.is-maximized .modal-body {
                flex: 1 1 auto;
            }
        `;

        document.head.appendChild(style);
    }

    render() {
        const container = this._getContainer();
        container.insertAdjacentHTML("beforeend", this._getModalHtml());

        this.modalElement = document.getElementById(this.modalId);

        if (!this.modalElement) {
            throw new Error("No se pudo renderizar el modal.");
        }

        this._cacheModalWindowElements();
        this._bindModalWindowEvents();

        this.modalElement.addEventListener("hidden.bs.modal", () => {
            this._resetWindowState();
            if (this.destroyOnClose) {
                this.destroy();
            }
        });

        this.modalInstance = new bootstrap.Modal(this.modalElement, {
            backdrop: this.backdrop,
            keyboard: this.keyboard
        });
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

    open() {
        if (!this.modalElement) {
            this.render();
        }

        this.modalInstance.show();
    }

    close() {
        if (this.modalInstance) {
            this.modalInstance.hide();
        }
    }

    destroy() {
        if (this.modalInstance) {
            this.modalInstance.dispose();
        }

        if (this.modalElement) {
            this.modalElement.remove();
        }

        this.modalElement = null;
        this.modalInstance = null;
    }

    setBody(html) {
        this.body = html;

        if (!this.modalElement) {
            return;
        }

        const bodyElement = this.modalElement.querySelector(".modal-body");

        if (bodyElement) {
            bodyElement.innerHTML = html;
        }
    }

    setFooter(html) {
        this.footer = html;

        if (!this.modalElement) {
            return;
        }

        const footerElement = this.modalElement.querySelector(".modal-footer");

        if (footerElement) {
            footerElement.innerHTML = html;
        }
    }

    getElement() {
        return this.modalElement;
    }
}

export async function deleteModal({
    containerName,
    url,
    headers = {},
    method = "DELETE",
    title = "Eliminar registro",
    message = "¿Seguro que deseas eliminar este registro?",
    confirmText = "Eliminar",
    cancelText = "Cancelar",
    size = "",
    onSuccess = null,
    onError = null
} = {}) {
    let modal = null;

    try {
        modal = new CustomModal({
            containerName,
            title,
            size,
            body: `
                <div class="d-flex align-items-start gap-3">
                    <div class="text-danger fs-3">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                    </div>
                    <div class="w-100">
                        <div class="mb-0">${message}</div>
                        <div class="alert alert-danger mt-3 d-none" modal-role="error-box"></div>
                    </div>
                </div>
            `,
            footer: `
                <button type="button" class="btn btn-secondary" modal-role="cancel-btn">
                    ${cancelText}
                </button>
                <button type="button" class="btn btn-danger" modal-role="confirm-btn">
                    ${confirmText}
                </button>
            `
        });

        modal.open();

        const modalElement = modal.getElement();
        const confirmButton = modalElement.querySelector('[modal-role="confirm-btn"]');
        const cancelButton = modalElement.querySelector('[modal-role="cancel-btn"]');
        const errorBox = modalElement.querySelector('[modal-role="error-box"]');

        const showError = (error) => {
            if (!errorBox) {
                return;
            }

            errorBox.classList.remove("d-none");
            errorBox.textContent = error instanceof Error ? error.message : String(error);
        };

        const clearError = () => {
            if (!errorBox) {
                return;
            }

            errorBox.classList.add("d-none");
            errorBox.textContent = "";
        };

        cancelButton.addEventListener("click", () => {
            modal.close();
        });

        confirmButton.addEventListener("click", async () => {
            try {
                clearError();

                confirmButton.disabled = true;
                cancelButton.disabled = true;
                confirmButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                    Eliminando...
                `;

                const response = await fetch(url, {
                    method,
                    headers
                });

                let result = null;
                const contentType = response.headers.get("content-type") || "";

                if (contentType.includes("application/json")) {
                    result = await response.json();
                } else {
                    result = await response.text();
                }

                if (!response.ok) {
                    const errorMessage =
                        result?.message ||
                        result?.error ||
                        "No se pudo eliminar el registro.";

                    throw new Error(errorMessage);
                }

                alertMessage.notifyResponse(result, {
                    type: "success",
                    message: "Registro eliminado correctamente."
                });

                if (typeof onSuccess === "function") {
                    onSuccess(result, modal);
                } else {
                    modal.close();
                }
            } catch (error) {
                confirmButton.disabled = false;
                cancelButton.disabled = false;
                confirmButton.innerHTML = confirmText;

                showError(error);
                alertMessage.notifyError(error, {
                    title: "No se pudo eliminar",
                    fallbackMessage: "La eliminacion no pudo completarse."
                });

                if (typeof onError === "function") {
                    onError(error, modal);
                }
            }
        });

        return modal;
    } catch (error) {
        if (typeof onError === "function") {
            onError(error, modal);
            return null;
        }

        alertMessage.notifyError(error, {
            title: "No se pudo abrir la confirmacion",
            fallbackMessage: "No se pudo preparar la ventana de confirmacion."
        });
        return null;
    }
}

export { CustomModal };
