from decimal import Decimal

import stripe

from django.conf import settings
from django.urls import reverse

from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, request):
    total_price = borrowing.calculate_total_price()

    unit_amount = int(total_price.quantize(Decimal("1.00")) * 100)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=(
                request.build_absolute_uri(
                    reverse("payment:payment-success")) + "?session_id={CHECKOUT_SESSION_ID}"
        ),

        cancel_url=request.build_absolute_uri(reverse("payment:payment-cancel")),
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )

    return payment
