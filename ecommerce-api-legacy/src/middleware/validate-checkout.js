const { BadRequestError } = require('../errors');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function validateCheckout(req, res, next) {
    const body = req.body || {};
    const courseId = Number(body.c_id);
    const valid = typeof body.usr === 'string'
        && body.usr.trim().length > 0
        && typeof body.eml === 'string'
        && EMAIL_PATTERN.test(body.eml)
        && typeof body.pwd === 'string'
        && body.pwd.length >= 3
        && Number.isInteger(courseId)
        && courseId > 0
        && typeof body.card === 'string'
        && CARD_PATTERN.test(body.card);

    if (!valid) {
        return next(new BadRequestError('Bad Request'));
    }

    req.validatedBody = {
        name: body.usr.trim(),
        email: body.eml.toLowerCase(),
        password: body.pwd,
        courseId,
        card: body.card,
    };
    return next();
}

module.exports = { validateCheckout };
