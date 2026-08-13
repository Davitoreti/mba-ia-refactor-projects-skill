const { randomBytes, scryptSync } = require('node:crypto');

function hashPassword(password) {
    const salt = randomBytes(16);
    const hash = scryptSync(password, salt, 64);
    return `scrypt:${salt.toString('hex')}:${hash.toString('hex')}`;
}

module.exports = { hashPassword };
