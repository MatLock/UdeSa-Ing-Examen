import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

STATUS = "status"
AMOUNT = "amount"
PAYMENT_METHOD = "payment_method"

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

DATA_PATH = "data.json"

METHOD_CREDIT_CARD = "Tarjeta de Crédito"
METHOD_PAYPAL = "PayPal"

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


def save_payment(payment_id, amount, payment_method, status):
    data = {
        AMOUNT: amount,
        PAYMENT_METHOD: payment_method,
        STATUS: status,
    }
    save_payment_data(payment_id, data)

# --- Nueva función de validación ---
def validate_payment_rules(payment_id_to_process: str, payment_data: dict, all_payments: dict):
    """
    Aplica las reglas de negocio para un intento de pago.
    Lanza un ValueError si alguna regla no se cumple.
    """
    amount = payment_data[AMOUNT]
    method = payment_data[PAYMENT_METHOD]

    if method == METHOD_CREDIT_CARD:
        # Regla 1.1: Monto máximo para Tarjeta de Crédito
        if amount >= 10000:
            raise ValueError("El pago con Tarjeta de Crédito no puede ser mayor o igual a $10,000.")

        # Regla 1.2: No más de 1 pago REGISTRADO con este método
        registered_credit_card_payments = 0
        for pid, pdata in all_payments.items():
            if pid != payment_id_to_process and \
               pdata[PAYMENT_METHOD] == METHOD_CREDIT_CARD and \
               pdata[STATUS] == STATUS_REGISTRADO:
                registered_credit_card_payments += 1
        
        if registered_credit_card_payments > 0:
            raise ValueError("Ya existe otro pago con Tarjeta de Crédito pendiente de procesamiento.")

    elif method == METHOD_PAYPAL:
        # Regla 2.1: Monto máximo para PayPal
        if amount >= 5000:
            raise ValueError("El pago con PayPal no puede ser mayor o igual a $5,000.")


"""
# Ejemplo de uso:
# Actualizando el status de un pago:
data = load_payment(payment_id)
data[STATUS] = STATUS_PAGADO
save_payment_data(payment_id, data)
"""



# Endpoints a implementar:
# * GET en el path /payments que retorne todos los pagos.
# * POST en el path /payments/{payment_id} que registre un nuevo pago.
# * POST en el path /payments/{payment_id}/update que cambie los parametros de una pago (amount, payment_method)
# * POST en el path /payments/{payment_id}/pay que intente.
# * POST en el path /payments/{payment_id}/revert que revertir el pago.

class Payment(BaseModel):
    payment_id: int
    payment_amount: float
    payment_method: str

class PaymentRequest(BaseModel):
    amount: float
    method: str


@app.get("/payments")
async def get_payments():
    """Devuelve todos los pagos del sistema"""
    return load_all_payments()

@app.post('/payments/{payment_id}')
async def create_payment(payment_id: int, request: PaymentRequest):
    save_payment(payment_id, request.amount, request.method, STATUS_REGISTRADO)

@app.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: int):
    """
    Intenta marcar un pago como PAGADO, aplicando las reglas de negocio.
    """
    try:
        all_payments = load_all_payments()
        payment_data = all_payments[str(payment_id)]

        # 1. Validar las reglas de negocio ANTES de procesar.
        validate_payment_rules(str(payment_id), payment_data, all_payments)

        # 2. Si la validación es exitosa, se actualiza el estado.
        payment_data[STATUS] = STATUS_PAGADO
        save_payment_data(str(payment_id), payment_data)

        return payment_data
    
    except ValueError as e:
        payment_data = load_payment(str(payment_id))
        payment_data[STATUS] = STATUS_FALLIDO
        save_payment_data(str(payment_id), payment_data)
        raise HTTPException(status_code=409, detail=str(e))

    except KeyError:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")

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
    
@app.post("/payments/{payment_id}/revert")
async def revert_payment(payment_id: int):
    """
    Revierte el estado de un pago a 'REGISTRADO'.
    Si el pago no se encuentra, devuelve un error 404.
    """
    try:
        # 1. Cargar los datos del pago.
        payment_data = load_payment(str(payment_id))

        # 2. Actualizar el estado a 'REGISTRADO', sin importar su estado actual.
        payment_data[STATUS] = STATUS_REGISTRADO

        # 3. Guardar los cambios.
        save_payment_data(str(payment_id), payment_data)

        # 4. Devolver el objeto actualizado como confirmación.
        return payment_data

    except KeyError:
        # 5. Manejar el caso de que el ID no exista.
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")