const express = require('express');
const { requireAdminToken } = require('../middleware/auth');
const { validateCheckout } = require('../middleware/validate-checkout');

function createApiRouter({ adminApiToken, checkoutController, adminController }) {
    const router = express.Router();
    const authorizeAdmin = requireAdminToken(adminApiToken);

    router.post('/checkout', validateCheckout, checkoutController.create);
    router.get('/admin/financial-report', authorizeAdmin, adminController.financialReport);
    router.delete('/users/:id', authorizeAdmin, adminController.deleteUser);

    return router;
}

module.exports = { createApiRouter };
