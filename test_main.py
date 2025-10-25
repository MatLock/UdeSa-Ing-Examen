import unittest

from main import save_payment, load_payment, STATUS_REGISTRADO, STATUS_FALLIDO, STATUS_PAGADO

PAYMENT_ID = 1
PAYMENT_METHOD = 'Paypal'
PAYMENT_AMOUNT = 10000


class PaymentTest(unittest.TestCase):

  async def test_payment_creation(self):
    await save_payment(PAYMENT_ID, PAYMENT_AMOUNT, PAYMENT_METHOD, STATUS_REGISTRADO)
    payment = load_payment(PAYMENT_ID)
    self.assertIsNotNone(payment)
    self.assertEqual(payment.payment_id, PAYMENT_ID)
    self.assertEqual(payment.amount, PAYMENT_AMOUNT)
    self.assertEqual(payment.method, PAYMENT_METHOD)
    self.assertEqual(payment.status, STATUS_REGISTRADO)
  