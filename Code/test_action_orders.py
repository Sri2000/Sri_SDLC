import unittest
from unittest.mock import patch
from action_orders import get_user_order_history, process_payment

class TestActionOrders(unittest.TestCase):

    def test_get_user_order_history_success(self):
        result = get_user_order_history(user_id=1, page=1, page_size=10)
        self.assertEqual(result['user_id'], 1)
        self.assertEqual(len(result['orders']), 3)
        self.assertEqual(result['total_orders'], 3)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 10)

    def test_get_user_order_history_with_status_filter(self):
        result = get_user_order_history(user_id=1, status='shipped')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['status'], 'shipped')

    def test_get_user_order_history_with_date_filter(self):
        from datetime import datetime
        start_date = datetime.strptime("2024-12-10", '%Y-%m-%d')
        end_date = datetime.strptime("2024-12-15", '%Y-%m-%d')
        result = get_user_order_history(user_id=1, start_date=start_date, end_date=end_date)
        self.assertEqual(len(result['orders']), 2)

    def test_get_user_order_history_no_orders(self):
        result = get_user_order_history(user_id=1, page=2, page_size=10)
        self.assertEqual(result['message'], "No orders found.")

    @patch('requests.post')
    def test_process_payment_success_credit_card(self, mock_post):
        mock_post.return_value.status_code = 200
        payment_info = {'method': 'credit_card', 'amount': 100, 'details': {}}
        result = process_payment(order_id=1, payment_info=payment_info)
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['status'], 'paid')
        self.assertEqual(result['message'], 'Payment successful.')

    @patch('requests.post')
    def test_process_payment_success_paypal(self, mock_post):
        mock_post.return_value.status_code = 200
        payment_info = {'method': 'paypal', 'amount': 100, 'details': {}}
        result = process_payment(order_id=1, payment_info=payment_info)
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['status'], 'paid')
        self.assertEqual(result['message'], 'Payment successful.')

    @patch('requests.post')
    def test_process_payment_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        payment_info = {'method': 'credit_card', 'amount': 100, 'details': {}}
        result = process_payment(order_id=1, payment_info=payment_info)
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('Payment failed. Status Code:', result['message'])

    @patch('requests.post')
    def test_process_payment_unsupported_method(self, mock_post):
        payment_info = {'method': 'bitcoin', 'amount': 100, 'details': {}}
        result = process_payment(order_id=1, payment_info=payment_info)
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['message'], 'Unsupported payment method')

    @patch('requests.post')
    def test_process_payment_retries_on_failure(self, mock_post):
        mock_post.side_effect = [Exception("Network error"), Exception("Network error"), 
                                  mock_post.return_value]
        mock_post.return_value.status_code = 200
        payment_info = {'method': 'credit_card', 'amount': 100, 'details': {}}
        result = process_payment(order_id=1, payment_info=payment_info)
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['status'], 'paid')
        self.assertEqual(result['message'], 'Payment successful.')

if __name__ == '__main__':
    unittest.main()