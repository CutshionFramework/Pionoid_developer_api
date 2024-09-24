import stripe

class StripePayment:
    def __init__(self, api_key):
        stripe.api_key = api_key

    def create_payment_source(self, token):
        try:
            source = stripe.Source.create(
                type='card',
                token=token
            )
            return source.id
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return None

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
        
    # Example for Google Pay
    google_pay_token = "tok_visa"  # Replace with actual Google Pay token
    google_pay_source = stripe_payment.create_payment_source(google_pay_token)
    if google_pay_source:
        payment_successful = stripe_payment.process_payment(
            amount=5000,  
            currency="usd",
            source=google_pay_source,
            description="Google Pay Test Charge"
        )
        if payment_successful:
            print("Google Pay payment succeeded")
        else:
            print("Google Pay payment failed")
    else:
        print("Failed to create Google Pay payment source")

    # Example for Apple Pay
    apple_pay_token = "tok_chargeDeclined"  # Replace with actual Apple Pay token
    apple_pay_source = stripe_payment.create_payment_source(apple_pay_token)
    if apple_pay_source:
        payment_successful = stripe_payment.process_payment(
            amount=5000,  
            currency="usd",
            source=apple_pay_source,
            description="Apple Pay Test Charge"
        )
        if payment_successful:
            print("Apple Pay payment succeeded")
        else:
            print("Apple Pay payment failed")
    else:
        print("Failed to create Apple Pay payment source")