const { timingSafeEqual } = require('node:crypto');

function tokensMatch(received, expected) {
    const receivedBuffer = Buffer.from(received);
    const expectedBuffer = Buffer.from(expected);
    return receivedBuffer.length === expectedBuffer.length
        && timingSafeEqual(receivedBuffer, expectedBuffer);
}

function requireAdminToken(expectedToken) {
    return (req, res, next) => {
        const authorization = req.get('authorization') || '';
        const [scheme, token = ''] = authorization.split(' ');

        if (scheme !== 'Bearer' || !tokensMatch(token, expectedToken)) {
            return res.status(401).send('Unauthorized');
        }

        return next();
    };
}

module.exports = { requireAdminToken };
