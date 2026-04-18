const ALERT_CONTAINER_ID = "app-alert-message-container";
const ALERT_STYLE_ID = "app-alert-message-styles";
const FLASH_MESSAGE_SELECTOR = "[data-alert-flash]";

const TYPE_CONFIG = {
    success: {
        icon: "bi bi-check-circle-fill",
        className: "is-success",
        title: "Operacion completada"
    },
    info: {
        icon: "bi bi-info-circle-fill",
        className: "is-info",
        title: "Informacion"
    },
    warning: {
        icon: "bi bi-exclamation-triangle-fill",
        className: "is-warning",
        title: "Advertencia"
    },
    error: {
        icon: "bi bi-x-octagon-fill",
        className: "is-error",
        title: "Error"
    }
};

function normalizeType(type) {
    const normalizedType = String(type || "info").trim().toLowerCase().split(/\s+/)[0];

    if (normalizedType === "danger") {
        return "error";
    }

    if (TYPE_CONFIG[normalizedType]) {
        return normalizedType;
    }

    return "info";
}

function sanitizeMessage(message) {
    if (message instanceof Error) {
        return message.message || "Ha ocurrido un error inesperado.";
    }

    if (message === null || message === undefined) {
        return "";
    }

    return String(message).trim();
}

class AlertMessageManager {
    constructor(options = {}) {
        this.maxVisible = Number(options.maxVisible || 4);
        this.defaultDuration = Number(options.defaultDuration || 5000);
        this.container = null;
        this.initialized = false;
    }

    initialize() {
        if (this.initialized) {
            return this;
        }

        this._ensureStyles();
        this._ensureContainer();
        this.initialized = true;
        this.consumeFlashMessages();

        return this;
    }

    show(message, options = {}) {
        this.initialize();

        const normalizedType = normalizeType(options.type);
        const config = TYPE_CONFIG[normalizedType];
        const finalMessage = sanitizeMessage(message);

        if (!finalMessage) {
            return null;
        }

        this._trimOverflow();

        const alertElement = document.createElement("article");
        alertElement.className = `app-alert-message ${config.className}`;
        alertElement.setAttribute("role", normalizedType === "error" ? "alert" : "status");
        alertElement.setAttribute("aria-live", normalizedType === "error" ? "assertive" : "polite");

        const title = sanitizeMessage(options.title) || config.title;
        const iconClass = sanitizeMessage(options.icon) || config.icon;

        alertElement.innerHTML = `
            <div class="app-alert-message__icon" aria-hidden="true">
                <i class="${iconClass}"></i>
            </div>
            <div class="app-alert-message__content">
                <div class="app-alert-message__title">${title}</div>
                <div class="app-alert-message__text"></div>
            </div>
            <button type="button" class="app-alert-message__close" aria-label="Cerrar notificacion">
                <i class="bi bi-x-lg"></i>
            </button>
        `;

        const textElement = alertElement.querySelector(".app-alert-message__text");
        if (options.allowHtml === true) {
            textElement.innerHTML = finalMessage;
        } else {
            textElement.textContent = finalMessage;
        }

        const closeButton = alertElement.querySelector(".app-alert-message__close");
        closeButton.addEventListener("click", () => {
            this.remove(alertElement);
        });

        this.container.appendChild(alertElement);

        requestAnimationFrame(() => {
            alertElement.classList.add("is-visible");
        });

        const duration = options.sticky === true
            ? 0
            : Number(options.duration ?? this.defaultDuration);

        if (duration > 0) {
            const timeoutId = window.setTimeout(() => {
                this.remove(alertElement);
            }, duration);

            alertElement.dataset.timeoutId = String(timeoutId);
        }

        return alertElement;
    }

    success(message, options = {}) {
        return this.show(message, { ...options, type: "success" });
    }

    info(message, options = {}) {
        return this.show(message, { ...options, type: "info" });
    }

    warning(message, options = {}) {
        return this.show(message, { ...options, type: "warning" });
    }

    error(message, options = {}) {
        return this.show(message, { ...options, type: "error" });
    }

    notifyResponse(response, options = {}) {
        const type = normalizeType(options.type || (response?.success === false ? "error" : "success"));
        const fallbackMessage = type === "success"
            ? "Operacion realizada correctamente."
            : "No se pudo completar la operacion.";
        const message = response?.message || response?.error || options.message || fallbackMessage;

        return this.show(message, {
            ...options,
            type
        });
    }

    notifyError(error, options = {}) {
        const fallbackMessage = options.fallbackMessage || "Ha ocurrido un error inesperado.";
        const message = sanitizeMessage(error) || fallbackMessage;

        if (error instanceof Error) {
            console.error(error);
        } else if (error !== null && error !== undefined) {
            console.error(String(error));
        }

        return this.error(message, options);
    }

    consumeFlashMessages() {
        document.querySelectorAll(FLASH_MESSAGE_SELECTOR).forEach((element) => {
            const message = element.textContent || "";
            const type = element.dataset.alertType || "info";
            const title = element.dataset.alertTitle || "";
            const sticky = element.dataset.alertSticky === "true";

            this.show(message, {
                type,
                title,
                sticky
            });

            element.remove();
        });
    }

    remove(alertElement) {
        if (!alertElement) {
            return;
        }

        const timeoutId = Number(alertElement.dataset.timeoutId || 0);
        if (timeoutId) {
            window.clearTimeout(timeoutId);
        }

        alertElement.classList.remove("is-visible");
        alertElement.classList.add("is-leaving");

        window.setTimeout(() => {
            alertElement.remove();
        }, 180);
    }

    _trimOverflow() {
        if (!this.container) {
            return;
        }

        while (this.container.children.length >= this.maxVisible) {
            this._forceRemove(this.container.firstElementChild);
        }
    }

    _forceRemove(alertElement) {
        if (!alertElement) {
            return;
        }

        const timeoutId = Number(alertElement.dataset.timeoutId || 0);
        if (timeoutId) {
            window.clearTimeout(timeoutId);
        }

        alertElement.remove();
    }

    _ensureContainer() {
        let container = document.getElementById(ALERT_CONTAINER_ID);

        if (!container) {
            container = document.createElement("section");
            container.id = ALERT_CONTAINER_ID;
            container.className = "app-alert-message-stack";
            container.setAttribute("aria-label", "Notificaciones");
            document.body.appendChild(container);
        }

        this.container = container;
    }

    _ensureStyles() {
        if (document.getElementById(ALERT_STYLE_ID)) {
            return;
        }

        const style = document.createElement("style");
        style.id = ALERT_STYLE_ID;
        style.textContent = `
            .app-alert-message-stack {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1095;
                width: min(380px, calc(100vw - 2rem));
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                pointer-events: none;
            }

            .app-alert-message {
                position: relative;
                display: grid;
                grid-template-columns: auto 1fr auto;
                gap: 0.875rem;
                align-items: start;
                padding: 0.95rem 1rem;
                border-radius: 16px;
                border: 1px solid rgba(15, 23, 42, 0.08);
                background: rgba(255, 255, 255, 0.98);
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
                backdrop-filter: blur(10px);
                transform: translateY(-8px) scale(0.98);
                opacity: 0;
                transition: opacity 0.18s ease, transform 0.18s ease;
                pointer-events: auto;
                overflow: hidden;
            }

            .app-alert-message::before {
                content: "";
                position: absolute;
                inset: 0 auto 0 0;
                width: 4px;
                background: currentColor;
                opacity: 0.95;
            }

            .app-alert-message.is-visible {
                opacity: 1;
                transform: translateY(0) scale(1);
            }

            .app-alert-message.is-leaving {
                opacity: 0;
                transform: translateY(-8px) scale(0.98);
            }

            .app-alert-message__icon {
                font-size: 1.1rem;
                line-height: 1;
                margin-top: 0.15rem;
            }

            .app-alert-message__title {
                font-size: 0.92rem;
                font-weight: 700;
                line-height: 1.2;
                color: #0f172a;
                margin-bottom: 0.2rem;
            }

            .app-alert-message__text {
                font-size: 0.9rem;
                line-height: 1.45;
                color: #334155;
                word-break: break-word;
            }

            .app-alert-message__close {
                border: 0;
                background: transparent;
                color: #64748b;
                padding: 0.15rem;
                line-height: 1;
                cursor: pointer;
                border-radius: 999px;
            }

            .app-alert-message__close:hover {
                background: rgba(148, 163, 184, 0.16);
                color: #0f172a;
            }

            .app-alert-message.is-success {
                color: #15803d;
            }

            .app-alert-message.is-info {
                color: #0369a1;
            }

            .app-alert-message.is-warning {
                color: #b45309;
            }

            .app-alert-message.is-error {
                color: #b91c1c;
            }

            @media (max-width: 576px) {
                .app-alert-message-stack {
                    top: 0.75rem;
                    right: 0.75rem;
                    left: 0.75rem;
                    width: auto;
                }
            }
        `;

        document.head.appendChild(style);
    }
}

const alertMessage = new AlertMessageManager();

window.AlertMessage = alertMessage;

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        alertMessage.initialize();
    }, { once: true });
} else {
    alertMessage.initialize();
}

export {
    AlertMessageManager,
    alertMessage,
    normalizeType
};
