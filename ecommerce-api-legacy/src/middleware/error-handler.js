function errorHandler({ logger }) {
    return (error, req, res, next) => {
        if (res.headersSent) {
            return next(error);
        }

        const statusCode = error.statusCode || error.status;
        if (statusCode >= 400 && statusCode < 500) {
            return res.status(statusCode).send(error.publicMessage || 'Bad Request');
        }

        logger.error('Erro interno', error);
        return res.status(500).send('Erro DB');
    };
}

module.exports = { errorHandler };
