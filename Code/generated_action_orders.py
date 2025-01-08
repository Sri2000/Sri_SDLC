# Import required libraries
import requests
from datetime import datetime
####################################

# Function 1: Get User Order History with Pagination and Filtering
def get_user_order_history(user_id, page=1, page_size=10, status=None, start_date=None, end_date=None):
    """
    This function retrieves the order history for a user, with support for pagination and filtering.
    """
    from datetime import datetime

    # Simulate database query (In a real-world scenario, this would query a DB)
    orders_db = [
        {"order_id": 1, "user_id": user_id, "status": "shipped", "order_date": "2024-12-15", "total": 100},
        {"order_id": 2, "user_id": user_id, "status": "processing", "order_date": "2024-12-14", "total": 50},
        {"order_id": 3, "user_id": user_id, "status": "delivered", "order_date": "2024-12-10", "total": 150},
        # Additional orders...
    ]
    
    # Filter orders based on status, date range, and paginate
    filtered_orders = orders_db
    if status:
        filtered_orders = [order for order in filtered_orders if order['status'] == status]
    if start_date and end_date:
        filtered_orders = [
            order for order in filtered_orders if start_date <= datetime.strptime(order['order_date'], '%Y-%m-%d') <= end_date
        ]
    
    # Pagination logic
    start = (page - 1) * page_size
    end = page * page_size
    paginated_orders = filtered_orders[start:end]
    
    if not paginated_orders:
        return {"message": "No orders found."}
    
    return {
        "user_id": user_id,
        "orders": paginated_orders,
        "total_orders": len(filtered_orders),
        "page": page,
        "page_size": page_size
    }
# Function 2: Process Payment with Retry Logic and Multiple Payment Methods
def process_payment(order_id, payment_info):
    """
    This function processes a payment for an order, handling different payment methods, retries, and failure details.
    """
    payment_gateway_url = "https://payment-gateway.com/api/process"
    
    retries = 3
    for attempt in range(retries):
        try:
            # Assuming payment_info contains 'method', 'amount', and 'details'
            payment_status = None
            if payment_info['method'] == 'credit_card':
                payment_status = requests.post(payment_gateway_url, json=payment_info)
            elif payment_info['method'] == 'paypal':
                payment_status = requests.post(payment_gateway_url, json=payment_info)
            else:
                return {"order_id": order_id, "status": "failed", "message": "Unsupported payment method"}
            
            if payment_status.status_code == 200:
                return {"order_id": order_id, "status": "paid", "message": "Payment successful."}
            else:
                return {"order_id": order_id, "status": "failed", "message": f"Payment failed. Status Code: {payment_status.status_code}"}
        
        except requests.RequestException as e:
            if attempt < retries - 1:
                continue
            else:
                return {"order_id": order_id, "status": "failed", "message": f"Payment failed after {retries} attempts: {str(e)}"}
        except Exception as e:
            return {"order_id": order_id, "status": "failed", "message": str(e)}