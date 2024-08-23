import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.robot.custom_robots.jaka_robot import JakaRobot
from integrations.stripe_online_payment import StripePayment


def handle_payment_and_robot_movement(api_key, amount, currency, source, description):
    stripe_payment = StripePayment(api_key)
    payment_successful = stripe_payment.process_payment(amount, currency, source, description)
    
    if payment_successful:
        print("Payment succeeded, moving the robot.")
        robot = JakaRobot("192.168.0.127")
        robot.login()
        robot.power_on()
        robot.enable_robot()
        robot.joint_move(joint_pos=[1, 0, 0, 0, 0, 0], move_mode=0, is_block=False, speed=1)
        robot.logout()
    else:
        print("Payment failed, robot will not move.")

# Example usage
if __name__ == "__main__":
    handle_payment_and_robot_movement(
        api_key="sk_test_4eC39HqLyjWDarjtT1zdp7dc",  # Stripe's test API key
        amount=5000,  # Amount in cents
        currency="usd",
        source="tok_visa",  # Stripe's test card token for SUC
        #source="tok_chargeDeclined",  # Stripe's test card token for a declined charge
        description="Test Charge"
    )