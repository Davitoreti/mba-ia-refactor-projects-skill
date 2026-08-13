class CheckoutController {
    constructor({ checkoutService }) {
        this.checkoutService = checkoutService;
    }

    create = (req, res, next) => {
        try {
            return res.status(200).json(this.checkoutService.execute(req.validatedBody));
        } catch (error) {
            return next(error);
        }
    };
}

module.exports = { CheckoutController };
