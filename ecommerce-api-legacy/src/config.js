function requireSecret(env, name) {
    const value = env[name];

    if (typeof value !== 'string' || value.trim() === '') {
        throw new Error(`${name} is required`);
    }

    return value;
}

function loadConfig(env = process.env) {
    const port = Number(env.PORT || 3000);

    if (!Number.isInteger(port) || port < 0 || port > 65535) {
        throw new Error('PORT must be an integer between 0 and 65535');
    }

    return {
        port,
        adminApiToken: requireSecret(env, 'ADMIN_API_TOKEN'),
    };
}

module.exports = { loadConfig };
