export class DateFormatter {

    static ISO_REGEX =
        /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,6})?)?$/;

    static parse(value) {
        if (!value)
            return null;
        if (value instanceof Date)
            return value;
        if (typeof value === "string" && this.ISO_REGEX.test(value))
            return new Date(value);
        return null;
    }

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