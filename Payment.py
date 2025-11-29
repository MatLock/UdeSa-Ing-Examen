from payment_method.PaymentType import *
from payment_state.PaymentState import *


class Payment:
    
    def __init__(self, payment_id: str, amount: float, state: PaymentState, payment_type: PaymentType):
        self.payment_id = payment_id
        self.amount = amount
        self.payment_type = payment_type
        self.status = state
        
    def check_transition_valid(self, new_state):
        if self.status.is_transition_valid(new_state):
            return
        raise ValueError(f'El estado {self.status.description()} no admite cambio al nuevo estado {new_state}')
    
    def pay(self, amount: float):
        self.payment_type.validate(amount)
        if self.status.is_transition_valid(STATUS_PAGADO):
            self.status = PayedPayment()
    
    def revert(self):
        if self.status.is_transition_valid(STATUS_PAGADO):
            self.status = RegisteredPayment()
    
    def update(self, amount: float, payment_method: str):
        if self.status.is_update_valid():
            self.amount = amount
            if payment_method == METHOD_PAYPAL:
                self.payment_type = PaypalPayment()
                return
            self.payment_type = CreditCardPayment()
    
    def to_json(self):
        return {'amount': self.amount, 'status': self.status.description(), 'payment_method': self.payment_type.payment_name()}