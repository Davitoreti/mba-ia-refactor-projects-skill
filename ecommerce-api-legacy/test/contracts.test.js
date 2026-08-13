const assert = require('node:assert/strict');
const { after, before, test } = require('node:test');
const { createApplication } = require('../src/create-application');

const ADMIN_TOKEN = 'test-admin-token';
const silentLogger = { info() {}, error() {} };
let baseUrl;
let database;
let server;

before(async () => {
    const application = createApplication({
        config: { adminApiToken: ADMIN_TOKEN },
        logger: silentLogger,
    });
    database = application.database;
    server = application.app.listen(0);
    await new Promise((resolve) => server.once('listening', resolve));
    baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
    await new Promise((resolve, reject) => server.close((error) => (
        error ? reject(error) : resolve()
    )));
    database.close();
});

async function request(path, options = {}) {
    return fetch(`${baseUrl}${path}`, options);
}

test('POST /api/checkout preserves the success contract and persists atomically', async () => {
    const response = await request('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            usr: 'Guilherme',
            eml: 'gui@fullcycle.com.br',
            pwd: 'senhaforte',
            c_id: 2,
            card: '4111222233334444',
        }),
    });

    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { msg: 'Sucesso', enrollment_id: 2 });
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM users').get().count, 2);
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM enrollments').get().count, 2);
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM payments').get().count, 2);
    const password = database.prepare('SELECT pass FROM users WHERE email = ?').get(
        'gui@fullcycle.com.br',
    ).pass;
    assert.match(password, /^scrypt:/);
    assert.equal(password.includes('senhaforte'), false);
});

test('POST /api/checkout rejects invalid input without partial persistence', async () => {
    const beforeCount = database.prepare('SELECT COUNT(*) AS count FROM users').get().count;
    const response = await request('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ usr: 'Invalid', eml: 'invalid', c_id: 1, card: 4 }),
    });

    assert.equal(response.status, 400);
    assert.equal(await response.text(), 'Bad Request');
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM users').get().count, beforeCount);
});

test('POST /api/checkout maps malformed JSON to a stable 400 response', async () => {
    const response = await request('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: '{',
    });

    assert.equal(response.status, 400);
    assert.equal(await response.text(), 'Bad Request');
});

test('POST /api/checkout preserves not-found and denied-payment errors', async () => {
    const notFound = await request('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            usr: 'Ana', eml: 'ana@example.com', pwd: 'abc', c_id: 999,
            card: '4111222233334444',
        }),
    });
    assert.equal(notFound.status, 404);
    assert.equal(await notFound.text(), 'Curso não encontrado');

    const denied = await request('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            usr: 'Ana', eml: 'ana@example.com', pwd: 'abc', c_id: 1,
            card: '5111222233334444',
        }),
    });
    assert.equal(denied.status, 400);
    assert.equal(await denied.text(), 'Pagamento recusado');
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM users WHERE email = ?').get(
        'ana@example.com',
    ).count, 0);
});

test('GET /api/admin/financial-report requires auth and preserves its JSON shape', async () => {
    const unauthorized = await request('/api/admin/financial-report');
    assert.equal(unauthorized.status, 401);

    const response = await request('/api/admin/financial-report', {
        headers: { authorization: `Bearer ${ADMIN_TOKEN}` },
    });
    assert.equal(response.status, 200);
    const report = await response.json();
    assert.deepEqual(report.map((item) => Object.keys(item)), [
        ['course', 'revenue', 'students'],
        ['course', 'revenue', 'students'],
    ]);
    assert.equal(report[0].course, 'Clean Architecture');
    assert.equal(report[0].revenue, 997);

    const paged = await request('/api/admin/financial-report?limit=1&offset=1', {
        headers: { authorization: `Bearer ${ADMIN_TOKEN}` },
    });
    assert.equal(paged.status, 200);
    assert.deepEqual((await paged.json()).map((item) => item.course), ['Docker']);
});

test('DELETE /api/users/:id requires auth and cascades related data', async () => {
    const unauthorized = await request('/api/users/1', { method: 'DELETE' });
    assert.equal(unauthorized.status, 401);

    const response = await request('/api/users/1', {
        method: 'DELETE',
        headers: { authorization: `Bearer ${ADMIN_TOKEN}` },
    });
    assert.equal(response.status, 200);
    assert.equal(await response.text(), 'Usuário deletado com seus dados relacionados.');
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM users WHERE id = 1').get().count, 0);
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM enrollments WHERE user_id = 1').get().count, 0);
    assert.equal(database.prepare('SELECT COUNT(*) AS count FROM payments WHERE enrollment_id = 1').get().count, 0);
});
