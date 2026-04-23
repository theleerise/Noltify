/**
 * @module formater
 * @description Utilidades de formateo de fechas y horas para la interfaz.
 * Este módulo interpreta valores compatibles con fechas ISO y los devuelve
 * en formato localizado para español (`es-ES`).
 */

/**
 * Utilidad estática para parsear y formatear fechas.
 */
export class DateFormatter {

    static ISO_REGEX =
        /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,6})?)?$/;

    /**
     * Convierte un valor compatible a una instancia `Date`.
     *
     * @param {string|Date|null|undefined} value - Valor a interpretar.
     * @returns {Date|null} Fecha parseada o `null` si no se puede interpretar.
     */
    static parse(value) {
        if (!value)
            return null;
        if (value instanceof Date)
            return value;
        if (typeof value === "string" && this.ISO_REGEX.test(value))
            return new Date(value);
        return null;
    }

    /**
     * Formatea un valor como fecha `dd/mm/yyyy`.
     *
     * @param {string|Date|null|undefined} value - Valor a formatear.
     * @returns {*} Fecha formateada o el valor original si no es convertible.
     */
    static toDate(value) {
        const date = this.parse(value);
        if (!date)
            return value;
        return date.toLocaleDateString(
            "es-ES",
            {
                year: "numeric",
                month: "2-digit",
                day: "2-digit"
            }
        );
    }

    /**
     * Formatea un valor como fecha y hora en locale español.
     *
     * @param {string|Date|null|undefined} value - Valor a formatear.
     * @returns {*} Fecha/hora formateada o el valor original.
     */
    static toDateTime(value) {
        const date = this.parse(value);
        if (!date)
            return value;
        return date.toLocaleString(
            "es-ES",
            {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit"
            }
        );
    }

    /**
     * Formatea un valor mostrando únicamente la hora y los minutos.
     *
     * @param {string|Date|null|undefined} value - Valor a formatear.
     * @returns {*} Hora formateada o el valor original.
     */
    static toTime(value) {
        const date = this.parse(value);
        if (!date)
            return value;
        return date.toLocaleTimeString(
            "es-ES",
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );
    }

    /**
     * Aplica el formateo adecuado en función del tipo solicitado.
     *
     * @param {*} value - Valor a formatear.
     * @param {"date"|"datetime"|"time"|string} type - Tipo de representación deseado.
     * @returns {*} Resultado del formateo o el valor original si no aplica.
     */
    static format(value, type) {
        switch (type) {
            case "date":
                return this.toDate(value);
            case "datetime":
                return this.toDateTime(value);
            case "time":
                return this.toTime(value);
            default:
                return value;
        }
    }
}
