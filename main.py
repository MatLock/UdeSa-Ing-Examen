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


"""
# Ejemplos:

@app.get("/path/{arg_1}")
async def endpoint_a(arg_1: str, arg_2: float):
    # Este es un endpoint GET que recibe un argumento (arg_1) por path y otro por query (arg_2).
    return {}

@app.post("/path/{arg_1}/some_action")
async def endpoint_b(arg_1: str, arg_2: float, arg_3: str):
    # Este es un endpoint POST que recibe un argumento (arg_1) por path y otros dos por query (arg_2 y arg_3).
    return {}
"""

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

@app.post('payments/{payment_id}')
async def create_payment(payment_id: int, request: PaymentRequest):
    save_payment(payment_id, request.mount, request.method, STATUS_REGISTRADO)

# [Ticket-5] POST /payments/{payment_id}/update    
@app.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: int):
    try:
        # 1. Cargar los datos del pago específico.
        payment_data = load_payment(str(payment_id))

        # 2. Modificar el estado del pago.
        payment_data[STATUS] = STATUS_PAGADO

        # 3. Guardar los datos actualizados en el archivo JSON.
        save_payment_data(str(payment_id), payment_data)

        # 4. Devolver el objeto actualizado como confirmación.
        return payment_data

    except KeyError:
        # 5. Manejo de error: si el payment_id no existe en los datos,
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