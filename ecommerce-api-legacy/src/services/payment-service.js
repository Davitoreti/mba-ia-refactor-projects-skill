const AUTHORIZED_CARD_PREFIX = '4';

class PaymentService {
    authorize(cardNumber) {
        return cardNumber.startsWith(AUTHORIZED_CARD_PREFIX);
    }
}

module.exports = { PaymentService };
