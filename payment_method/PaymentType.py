from abc import abstractmethod

METHOD_CREDIT_CARD = "Tarjeta de Credito"
METHOD_PAYPAL = "Paypal"


class PaymentType:
    @abstractmethod
    def validate(self, payment):
        pass
    
    @abstractmethod
    def payment_name(self):
        pass


class PaypalPayment(PaymentType):
    def validate(self, amount):
        if amount >= 5000:
            raise ValueError("El pago con PayPal no puede ser mayor o igual a $5,000.")
    
    def payment_name(self):
        return METHOD_PAYPAL


class CreditCardPayment(PaymentType):
    def validate(self, amount):
        if amount >= 10000:
            raise ValueError("El pago con Tarjeta de Crédito no puede ser mayor o igual a $10,000.")
    
    def payment_name(self):
        return METHOD_CREDIT_CARD
