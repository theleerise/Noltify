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
            <div class="modal fade" id="${this.modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog ${this.size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.title}</h5>
                            ${this.closeButton
                                ? '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>'
                                : ""}
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

    render() {
        const container = this._getContainer();
        container.insertAdjacentHTML("beforeend", this._getModalHtml());

        this.modalElement = document.getElementById(this.modalId);

        if (!this.modalElement) {
            throw new Error("No se pudo renderizar el modal.");
        }

        this.modalElement.addEventListener("hidden.bs.modal", () => {
            if (this.destroyOnClose) {
                this.destroy();
            }
        });

        this.modalInstance = new bootstrap.Modal(this.modalElement, {
            backdrop: this.backdrop,
            keyboard: this.keyboard
        });
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

        console.error(error);
        return null;
    }
}

export { CustomModal };