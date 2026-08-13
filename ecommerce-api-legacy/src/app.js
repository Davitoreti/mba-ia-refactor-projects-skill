const { createApplication } = require('./create-application');
const { loadConfig } = require('./config');

function start() {
    const config = loadConfig();
    const { app } = createApplication({ config });

    return app.listen(config.port, () => {
        console.log(`LMS rodando na porta ${config.port}...`);
    });
}

if (require.main === module) {
    start();
}

module.exports = { start };
