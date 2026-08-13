class HttpError extends Error {
    constructor(statusCode, message) {
        super(message);
        this.statusCode = statusCode;
        this.publicMessage = message;
    }
}

class BadRequestError extends HttpError {
    constructor(message) {
        super(400, message);
    }
}

class NotFoundError extends HttpError {
    constructor(message) {
        super(404, message);
    }
}

class PaymentDeniedError extends HttpError {
    constructor(message) {
        super(400, message);
    }
}

module.exports = { BadRequestError, NotFoundError, PaymentDeniedError };
