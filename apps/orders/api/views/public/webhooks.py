import stripe
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from ....services import StripeService

logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        logger.warning("Invalid Stripe signature")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(str(e))
        return HttpResponse(status=400)

    event_type = event["type"]
    payment_intent = event["data"]["object"]

    if event_type == "payment_intent.succeeded":
        StripeService.handle_payment_success(payment_intent)

    elif event_type == "payment_intent.payment_failed":
        StripeService.handle_payment_failed(payment_intent)

    return HttpResponse(status=200)