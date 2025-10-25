import unittest
import json
import os
from main import save_payment, load_payment,  load_all_payments, get_payments, PaymentRequest, pay_payment, update_payment,  revert_payment, save_all_payments
from main import STATUS_REGISTRADO, STATUS_FALLIDO, STATUS_PAGADO, DATA_PATH, AMOUNT, METHOD_CREDIT_CARD, METHOD_PAYPAL
from fastapi import HTTPException

# datos de prueba para test payment payment test
PAYMENT_ID = 1
PAYMENT_METHOD = 'Paypal'
PAYMENT_AMOUNT = 10000

# datos de prueba para test payment endpoints
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

# datos de prueba para test pay_payment
PAYMENT_TO_BE_PAID = {
    "1": {
        "amount": 1500,
        "payment_method": "Debit Card",
        "status": STATUS_REGISTRADO
    }
}
PAYMENT_ID_TO_PAY = 1
NON_EXISTENT_PAYMENT_ID = 999

STATUS = "status"

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

class PayPaymentEndpointTest(unittest.TestCase):

    def setUp(self):
        """
        Prepara el entorno antes de cada test: crea un archivo data.json
        con un pago en estado 'REGISTRADO'.
        """
        with open(DATA_PATH, "w") as f:
            json.dump(PAYMENT_TO_BE_PAID, f, indent=4)

    def tearDown(self):
        """
        Limpia el entorno después de cada test: elimina el archivo data.json.
        """
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    async def test_pay_payment_successfully(self):
        """
        Prueba que un pago existente se marque correctamente como 'PAGADO'.
        """
        response = await pay_payment(PAYMENT_ID_TO_PAY)

        self.assertIsNotNone(response)
        self.assertEqual(response['status'], STATUS_PAGADO)

        updated_payment_in_db = load_payment(str(PAYMENT_ID_TO_PAY))
        self.assertEqual(updated_payment_in_db['status'], STATUS_PAGADO)

    async def test_pay_payment_not_found(self):
        """
        Prueba que se devuelva un error HTTPException 404
        cuando se intenta pagar un payment_id que no existe.
        """
        with self.assertRaises(HTTPException) as cm:
            await pay_payment(NON_EXISTENT_PAYMENT_ID)

        self.assertEqual(cm.exception.status_code, 404)

class UpdatePaymentEndpointTest(unittest.TestCase):

    def setUp(self):
        self.initial_data = PAYMENT_TO_BE_PAID
        with open(DATA_PATH, "w") as f:
            json.dump(self.initial_data, f, indent=4)

    def tearDown(self):
        """
        Limpia el entorno eliminando el archivo data.json.
        """
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    async def test_update_payment_successfully(self):
        """
        Prueba que un pago existente se actualiza correctamente
        con los nuevos valores de amount y payment_method.
        """
        payment_id_to_update = 1
        new_amount = 9999.99
        new_method = "Credit Card"

        # 1. Ejecución (Act)
        response = await update_payment(payment_id_to_update, new_amount, new_method)

        # 2. Verificación (Assert)
        self.assertEqual(response[AMOUNT], new_amount)
        self.assertEqual(response[PAYMENT_METHOD], new_method)
        self.assertEqual(response['status'], self.initial_data[str(payment_id_to_update)]['status'])

        updated_payment_in_db = load_payment(str(payment_id_to_update))
        self.assertEqual(updated_payment_in_db[AMOUNT], new_amount)

    async def test_update_payment_not_found(self):
        """
        Prueba que se devuelve un HTTPException 404 al intentar
        actualizar un payment_id que no existe.
        """
        non_existent_id = 404
        
        with self.assertRaises(HTTPException) as cm:
            await update_payment(non_existent_id, 100, "Cash")

        self.assertEqual(cm.exception.status_code, 404)

class RevertPaymentEndpointTest(unittest.TestCase):

    def setUp(self):
        """
        Prepara el entorno creando un data.json con un pago en estado 'PAGADO',
        para que la acción de revertir tenga un efecto visible.
        """
        self.initial_data = PAYMENT_TO_BE_PAID
        with open(DATA_PATH, "w") as f:
            json.dump(self.initial_data, f, indent=4)

    def tearDown(self):
        """
        Limpia el entorno eliminando el archivo data.json.
        """
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    async def test_revert_payment_successfully(self):
        """
        Prueba que un pago en estado 'PAGADO' se revierte
        correctamente al estado 'REGISTRADO'.
        """
        payment_id_to_revert = 1

        # 1. Ejecución (Act)
        response = await revert_payment(payment_id_to_revert)

        # 2. Verificación (Assert)
        self.assertEqual(response['status'], STATUS_REGISTRADO)
        
        reverted_payment_in_db = load_payment(str(payment_id_to_revert))
        self.assertEqual(reverted_payment_in_db['status'], STATUS_REGISTRADO)
        self.assertEqual(reverted_payment_in_db[AMOUNT], self.initial_data["1"][AMOUNT])


    async def test_revert_payment_not_found(self):
        """
        Prueba que se devuelve un HTTPException 404 al intentar
        revertir un payment_id que no existe.
        """
        non_existent_id = 12345
        
        with self.assertRaises(HTTPException) as cm:
            # 1. Ejecución (Act)
            await revert_payment(non_existent_id)

        # 2. Verificación (Assert)
        self.assertEqual(cm.exception.status_code, 404)

class PayPaymentValidationTest(unittest.TestCase):

    def tearDown(self):
        """ Limpia el archivo de datos después de cada test. """
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    # --- Tests para Tarjeta de Crédito ---

    async def test_pay_credit_card_fails_if_amount_is_too_high(self):
        """
        Verifica que el pago FALLE (409) si el monto de Tarjeta de Crédito es >= $10,000.
        """
        test_data = {
            "1": {"amount": 10000, "payment_method": METHOD_CREDIT_CARD, "status": STATUS_REGISTRADO}
        }
        save_all_payments(test_data)

        with self.assertRaises(HTTPException) as cm:
            await pay_payment(1)
        
        self.assertEqual(cm.exception.status_code, 409)
        self.assertEqual(load_payment("1")[STATUS], STATUS_FALLIDO)

    async def test_pay_credit_card_fails_if_another_is_registered(self):
        """
        Verifica que el pago FALLE (409) si ya existe otro pago con
        Tarjeta de Crédito en estado REGISTRADO.
        """
        test_data = {
            "1": {"amount": 500, "payment_method": METHOD_CREDIT_CARD, "status": STATUS_REGISTRADO},
            "2": {"amount": 1000, "payment_method": METHOD_CREDIT_CARD, "status": STATUS_REGISTRADO}
        }
        save_all_payments(test_data)

        # Ejecución y Verificación (Act & Assert)
        with self.assertRaises(HTTPException) as cm:
            await pay_payment(2)  # Intentamos pagar el segundo
        
        self.assertEqual(cm.exception.status_code, 409)
        self.assertEqual(load_payment("2")[STATUS], STATUS_FALLIDO)
        # El primer pago no debe haber sido afectado
        self.assertEqual(load_payment("1")[STATUS], STATUS_REGISTRADO)

    # --- Tests para PayPal ---

    async def test_pay_paypal_fails_if_amount_is_too_high(self):
        """
        Verifica que el pago FALLE (409) si el monto de PayPal es >= $5,000.
        """
        # Preparación (Arrange)
        test_data = {
            "1": {"amount": 5000, "payment_method": METHOD_PAYPAL, "status": STATUS_REGISTRADO}
        }
        save_all_payments(test_data)

        # Ejecución y Verificación (Act & Assert)
        with self.assertRaises(HTTPException) as cm:
            await pay_payment(1)
        
        self.assertEqual(cm.exception.status_code, 409)
        self.assertEqual(load_payment("1")[STATUS], STATUS_FALLIDO)

    # --- Test de Éxito ---

    async def test_pay_payment_succeeds_with_valid_conditions(self):
        """
        Verifica que un pago VÁLIDO (ej. Tarjeta de Crédito < 10000)
        se procesa correctamente a PAGADO.
        """
        # Preparación (Arrange)
        test_data = {
            "1": {"amount": 9999.99, "payment_method": METHOD_CREDIT_CARD, "status": STATUS_REGISTRADO}
        }
        save_all_payments(test_data)

        # Ejecución (Act)
        response = await pay_payment(1)
        
        # Verificación (Assert)
        self.assertEqual(response[STATUS], STATUS_PAGADO)
        self.assertEqual(load_payment("1")[STATUS], STATUS_PAGADO)