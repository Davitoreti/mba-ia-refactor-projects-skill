const { hashPassword } = require('./password-service');
const { NotFoundError, PaymentDeniedError } = require('../errors');

class CheckoutService {
    constructor({ repository, paymentService, cache, logger }) {
        this.repository = repository;
        this.paymentService = paymentService;
        this.cache = cache;
        this.logger = logger;
    }

    execute(input) {
        const course = this.repository.findActiveCourse(input.courseId);
        if (!course) {
            throw new NotFoundError('Curso não encontrado');
        }

        if (!this.paymentService.authorize(input.card)) {
            throw new PaymentDeniedError('Pagamento recusado');
        }

        const result = this.repository.completeCheckout({
            name: input.name,
            email: input.email,
            passwordHash: hashPassword(input.password),
            course,
        });

        this.cache.set(`last_checkout_${result.userId}`, course.title);
        this.logger.info(`Checkout concluído para o curso ${course.id}`);

        return { msg: 'Sucesso', enrollment_id: result.enrollmentId };
    }
}

module.exports = { CheckoutService };
