const express = require('express');
const { MemoryCache } = require('./infrastructure/memory-cache');
const { createDatabase } = require('./models/database');
const { CommerceRepository } = require('./repositories/commerce-repository');
const { CheckoutService } = require('./services/checkout-service');
const { FinancialReportService } = require('./services/financial-report-service');
const { PaymentService } = require('./services/payment-service');
const { CheckoutController } = require('./controllers/checkout-controller');
const { AdminController } = require('./controllers/admin-controller');
const { createApiRouter } = require('./routes/api-routes');
const { errorHandler } = require('./middleware/error-handler');

function createApplication({ config, logger = console } = {}) {
    if (!config || !config.adminApiToken) {
        throw new Error('Application config with adminApiToken is required');
    }

    const database = createDatabase();
    const repository = new CommerceRepository(database);
    repository.initialize();

    const cache = new MemoryCache({ maxEntries: 1000 });
    const checkoutService = new CheckoutService({
        repository,
        paymentService: new PaymentService(),
        cache,
        logger,
    });
    const reportService = new FinancialReportService({ repository });

    const app = express();
    app.use(express.json());
    app.use('/api', createApiRouter({
        adminApiToken: config.adminApiToken,
        checkoutController: new CheckoutController({ checkoutService }),
        adminController: new AdminController({ repository, reportService }),
    }));
    app.use(errorHandler({ logger }));

    return { app, database };
}

module.exports = { createApplication };
