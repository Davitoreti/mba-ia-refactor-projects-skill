const { BadRequestError } = require('../errors');

class AdminController {
    constructor({ repository, reportService }) {
        this.repository = repository;
        this.reportService = reportService;
    }

    financialReport = (req, res, next) => {
        try {
            const limit = parseNonNegativeInteger(req.query.limit, 100, { minimum: 1, maximum: 100 });
            const offset = parseNonNegativeInteger(req.query.offset, 0);
            return res.status(200).json(this.reportService.execute({ limit, offset }));
        } catch (error) {
            return next(error);
        }
    };

    deleteUser = (req, res, next) => {
        try {
            this.repository.deleteUser(req.params.id);
            return res.status(200).send('Usuário deletado com seus dados relacionados.');
        } catch (error) {
            return next(error);
        }
    };
}

function parseNonNegativeInteger(value, defaultValue, { minimum = 0, maximum = Infinity } = {}) {
    if (value === undefined) {
        return defaultValue;
    }

    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed < minimum || parsed > maximum) {
        throw new BadRequestError('Bad Request');
    }

    return parsed;
}

module.exports = { AdminController };
