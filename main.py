import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from payment_method.PaymentType import *
from payment_state.PaymentState import *
from Payment import Payment

STATUS = "status"
AMOUNT = "amount"
PAYMENT_METHOD = "payment_method"
DATA_PATH = "data.json"

app = FastAPI()

def load_all_payments():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data


def save_all_payments(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_payment(payment_id):
    data = load_all_payments()[payment_id]
    return data


def save_payment_data(payment_id, data):
    all_data = load_all_payments()
    all_data[str(payment_id)] = data
    save_all_payments(all_data)


def save_payment(payment_id, amount, payment_method):
    payment_type = PaypalPayment() if METHOD_PAYPAL == payment_method else CreditCardPayment()
    payment_type.validate(amount)
    new_payment = Payment(payment_id, amount,
                          RegisteredPayment(),
                          payment_type)
    save_payment_data(payment_id, new_payment.to_json())
    
def create_payment_state(state):
    if STATUS_REGISTRADO == state:
        return RegisteredPayment()
    if STATUS_REGISTRADO == state:
        return FailedPayment()
    return PayedPayment()


# Endpoints a implementar:
# * GET en el path /payments que retorne todos los pagos.
# * POST en el path /payments/{payment_id} que registre un nuevo pago.
# * POST en el path /payments/{payment_id}/update que cambie los parametros de una pago (amount, payment_method)
# * POST en el path /payments/{payment_id}/pay que intente.
# * POST en el path /payments/{payment_id}/revert que revertir el pago.
class PaymentRequest(BaseModel):
    amount: float
    method: str


@app.get("/payments")
async def get_payments():
    """Devuelve todos los pagos del sistema"""
    return load_all_payments()

@app.post('/payments/{payment_id}')
async def create_payment(payment_id: int, request: PaymentRequest):
    try:
        save_payment(payment_id, request.amount, request.method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: int):
    """
    Intenta marcar un pago como PAGADO, aplicando las reglas de negocio.
    """
    try:
        all_payments = load_all_payments()
        payment_data = all_payments[str(payment_id)]
        # 2. Si la validación es exitosa, se actualiza el estado.
        payment_type = PaypalPayment() if METHOD_PAYPAL == payment_data['payment_method'] else CreditCardPayment()
        payment_state = create_payment_state(payment_data['status'])
        payment = Payment(str(payment_id), payment_data['amount'], payment_state, payment_type)
        payment.check_transition_valid(STATUS_PAGADO)
        
        payment_data[STATUS] = STATUS_PAGADO
        save_payment_data(str(payment_id), payment_data)
        return payment_data
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")
    except Exception as e:
        payment_data = load_payment(str(payment_id))
        payment_data[STATUS] = STATUS_FALLIDO
        save_payment_data(str(payment_id), payment_data)
        raise HTTPException(status_code=409, detail=str(e))

# [Ticket-4] POST /payments/{payment_id}/update    
@app.post("/payments/{payment_id}/update")
async def update_payment(payment_id: int, amount: float, payment_method: str):
    """
    Actualiza el monto y el método de un pago existente.
    Si el pago no se encuentra, devuelve un error 404.
    """
    try:
        # 1. Cargar los datos del pago específico.
        payment_data = load_payment(str(payment_id))
        payment_type = PaypalPayment() if METHOD_PAYPAL == payment_method else CreditCardPayment()
        payment_type.validate(amount)
        # 2. Actualizar los campos con los valores de los parámetros de query.
        payment_data[AMOUNT] = amount
        payment_data[PAYMENT_METHOD] = payment_method

        # 3. Guardar los datos actualizados en el archivo.
        save_payment_data(str(payment_id), payment_data)

        # 4. Devolver el objeto completo y actualizado.
        return payment_data

    except KeyError:
        # 5. Manejar el error si el payment_id no existe.
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
@app.post("/payments/{payment_id}/revert")
async def revert_payment(payment_id: int):
    """
    Revierte el estado de un pago a 'REGISTRADO'.
    Si el pago no se encuentra, devuelve un error 404.
    """
    try:
        # 1. Cargar los datos del pago.
        payment_data = load_payment(str(payment_id))
        payment_type = PaypalPayment() if METHOD_PAYPAL == payment_data['payment_method'] else CreditCardPayment()
        payment_state = create_payment_state(payment_data['status'])
        payment = Payment(str(payment_id), payment_data['amount'], payment_state, payment_type)
        payment.check_transition_valid(STATUS_REGISTRADO)
        
        # 2. Actualizar el estado a 'REGISTRADO', sin importar su estado actual.
        payment_data[STATUS] = STATUS_REGISTRADO

        # 3. Guardar los cambios.
        save_payment_data(str(payment_id), payment_data)

        # 4. Devolver el objeto actualizado como confirmación.
        return payment_data

    except KeyError:
        # 5. Manejar el caso de que el ID no exista.
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))