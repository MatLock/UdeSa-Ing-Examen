from abc import abstractmethod

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"


class PaymentState:
    
    def __init__(self, state: str):
        self.state = state
    
    def description(self):
        return self.state
    
    @abstractmethod
    def is_transition_valid(self, state_name):
        pass
    
    @abstractmethod
    def is_update_valid(self):
        pass


class RegisteredPayment(PaymentState):
    
    def __init__(self):
        super().__init__(STATUS_REGISTRADO)
    
    def is_transition_valid(self, state_name):
        return state_name == STATUS_PAGADO or state_name == STATUS_FALLIDO
    
    def is_update_valid(self):
        return True


class PayedPayment(PaymentState):
    def __init__(self):
        super().__init__(STATUS_PAGADO)
    
    def is_transition_valid(self, state_name):
        return True
    
    def is_update_valid(self):
        return False


class FailedPayment(PaymentState):
    def __init__(self):
        super().__init__(STATUS_FALLIDO)
    
    def is_transition_valid(self, state_name):
        return False
    
    def is_update_valid(self):
        return False
