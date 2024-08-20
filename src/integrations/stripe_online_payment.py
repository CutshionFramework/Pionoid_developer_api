import stripe

class StripePayment:
    def __init__(self, api_key):
        stripe.api_key = api_key

    def process_payment(self, amount, currency, source, description):
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                source=source,
                description=description
            )
            return charge['status'] == 'succeeded'
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return False

# Example usage
if __name__ == "__main__":
    stripe_payment = StripePayment("sk_test_4eC39HqLyjWDarjtT1zdp7dc")  # Stripe's test API key
    payment_successful = stripe_payment.process_payment(
        amount=5000,  # Amount in cents
        currency="usd",
        source="tok_visa",  # Stripe's test card token for a successful transaction
        #source="tok_chargeDeclined",  # Stripe's test card token for a declined charge
        description="Test Charge"
    )
    
    if payment_successful:
        print("Payment succeeded")
    else:
        print("Payment failed")