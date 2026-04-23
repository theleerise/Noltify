/**
 * @module rich-editor
 * @description Editor enriquecido ligero basado en `contenteditable`.
 * Sincroniza el contenido visual con un `textarea` auxiliar para facilitar
 * la integración con formularios HTML tradicionales.
 */

(function () {
    /**
     * Editor enriquecido ligero para formularios HTML.
     */
    class RichEditor {

        /**
         * @param {HTMLElement} container - Contenedor raíz del editor.
         */
        constructor(container) {
            this.container = container;
            this.editor = container.querySelector("[data-rich-editor]");
            this.toolbar = container.querySelector("[data-rich-editor-toolbar]");

            if (!this.editor) {
                return;
            }

            this.textareaId = this.editor.dataset.textareaId;
            this.textarea = document.getElementById(this.textareaId);

            if (!this.textarea) {
                console.warn("RichEditor: no se encontró el textarea asociado.");
                return;
            }

            this.placeholder = this.editor.dataset.placeholder || "";
            this.isReadonly = this.editor.dataset.readonly === "true";
            this.isDisabled = this.editor.dataset.disabled === "true";

            this._initialize();
        }

        /**
         * Inicializa el editor, sincroniza el valor inicial y enlaza eventos.
         *
         * @returns {void}
         */
        _initialize() {
            this._normalizeInitialValue();
            this._bindEditorEvents();
            this._bindToolbarEvents();
            this._refreshPlaceholder();
        }

        /**
         * Sincroniza el HTML inicial visible con el `textarea` asociado.
         *
         * @returns {void}
         */
        _normalizeInitialValue() {
            const textareaValue = (this.textarea.value || "").trim();
            const editorHtml = (this.editor.innerHTML || "").trim();

            if (!editorHtml && textareaValue) {
                this.editor.innerHTML = textareaValue;
            }

            this._syncTextarea();
        }

        /**
         * Enlaza los eventos de edición directa sobre el área editable.
         *
         * @returns {void}
         */
        _bindEditorEvents() {
            if (this.isReadonly || this.isDisabled) {
                return;
            }

            this.editor.addEventListener("input", () => {
                this._syncTextarea();
                this._refreshPlaceholder();
            });

            this.editor.addEventListener("blur", () => {
                this._syncTextarea();
                this._refreshPlaceholder();
            });

            this.editor.addEventListener("paste", (event) => {
                event.preventDefault();

                const clipboardData = event.clipboardData || window.clipboardData;
                const plainText = clipboardData.getData("text/plain");

                document.execCommand("insertText", false, plainText);
                this._syncTextarea();
                this._refreshPlaceholder();
            });
        }

        /**
         * Enlaza los botones de la barra de herramientas con sus comandos.
         *
         * @returns {void}
         */
        _bindToolbarEvents() {
            if (!this.toolbar || this.isReadonly || this.isDisabled) {
                return;
            }

            this.toolbar.addEventListener("click", (event) => {
                const button = event.target.closest("button");

                if (!button) {
                    return;
                }

                event.preventDefault();
                this.editor.focus();

                const customAction = button.dataset.customAction;
                const command = button.dataset.command;
                const value = button.dataset.value || null;

                if (customAction) {
                    this._runCustomAction(customAction);
                } else if (command) {
                    document.execCommand(command, false, value);
                }

                this._syncTextarea();
                this._refreshPlaceholder();
            });
        }

        /**
         * Ejecuta acciones personalizadas no cubiertas por `execCommand`.
         *
         * @param {string} action - Acción personalizada solicitada.
         * @returns {void}
         */
        _runCustomAction(action) {
            if (action === "link") {
                const url = window.prompt("Introduzca la URL del enlace:");
                if (!url) {
                    return;
                }

                document.execCommand("createLink", false, url);
                return;
            }

            if (action === "blockquote") {
                document.execCommand("formatBlock", false, "BLOCKQUOTE");
                return;
            }

            if (action === "image") {
                const url = window.prompt("Introduzca la URL de la imagen:");
                if (!url) {
                    return;
                }

                document.execCommand("insertImage", false, url);
            }
        }

        /**
         * Propaga el contenido actual del editor al `textarea` oculto.
         *
         * @returns {void}
         */
        _syncTextarea() {
            this.textarea.value = this.editor.innerHTML.trim();
        }

        /**
         * Actualiza el estado visual del placeholder según el contenido.
         *
         * @returns {void}
         */
        _refreshPlaceholder() {
            const textContent = (this.editor.textContent || "").trim();
            const hasVisualContent = textContent.length > 0 || this.editor.querySelector("img, video, iframe, table, ul, ol, blockquote");

            if (hasVisualContent) {
                this.editor.classList.remove("is-empty");
            } else {
                this.editor.classList.add("is-empty");
            }
        }

        /**
         * Inicializa todos los editores presentes en el documento.
         *
         * @returns {void}
         */
        static initAll() {
            document.querySelectorAll("[data-rich-editor-container]").forEach((container) => {
                if (!container.__richEditorInitialized) {
                    container.__richEditorInitialized = true;
                    new RichEditor(container);
                }
            });
        }
    }

    window.RichEditor = RichEditor;

    document.addEventListener("DOMContentLoaded", function () {
        RichEditor.initAll();
    });
})();
