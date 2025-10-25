import unittest
import json
import os
from main import save_payment, load_payment, STATUS_REGISTRADO, STATUS_FALLIDO, STATUS_PAGADO, DATA_PATH, load_all_payments, get_payments, PaymentRequest

PAYMENT_ID = 1
PAYMENT_METHOD = 'Paypal'
PAYMENT_AMOUNT = 10000

TEST_DATA = {
    "1": {
        "amount": 10000,
        "payment_method": "Paypal",
        "status": "REGISTRADO"
    },
    "2": {
        "amount": 500,
        "payment_method": "Credit Card",
        "status": "PAGADO"
    }
}

class PaymentTest(unittest.TestCase):

  async def test_payment_creation(self):
    await save_payment(PAYMENT_ID, PAYMENT_AMOUNT, PAYMENT_METHOD, STATUS_REGISTRADO)
    payment = load_payment(PAYMENT_ID)
    self.assertIsNotNone(payment)
    self.assertEqual(payment.payment_id, PAYMENT_ID)
    self.assertEqual(payment.amount, PAYMENT_AMOUNT)
    self.assertEqual(payment.method, PAYMENT_METHOD)
    self.assertEqual(payment.status, STATUS_REGISTRADO)
  
class GetPaymentsEndpointTest(unittest.TestCase):

    def setUp(self):
        with open(DATA_PATH, "w") as f:
            json.dump(TEST_DATA, f, indent=4)

    def tearDown(self):
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    async def test_get_all_payments_successfully(self):
        """
        Prueba que la función get_payments devuelve correctamente
        todos los pagos almacenados en el archivo data.json.
        """
        # 1. Ejecución (Act): Llamamos a la función asíncrona que queremos probar.
        retrieved_payments = await get_payments()

        # 2. Verificación (Assert): Comparamos el resultado obtenido con el esperado.
        self.assertIsNotNone(retrieved_payments)
        
        # Verificamos que los datos devueltos son exactamente los que guardamos
        self.assertEqual(retrieved_payments, TEST_DATA)
        
        self.assertEqual(len(retrieved_payments), 2)