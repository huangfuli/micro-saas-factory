import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from schemas.launch import BillingProvision


class StripeProvisioner:
    api = "https://api.stripe.com/v1"

    def _post(self, path: str, payload: dict[str, str], idempotency_key: str):
        secret = os.getenv("STRIPE_SECRET_KEY", "").strip()
        if not secret:
            raise RuntimeError("STRIPE_SECRET_KEY is required for Stripe provisioning.")

        body = urlencode(payload).encode("utf-8")
        request = Request(
            self.api + path,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {secret}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idempotency_key,
            },
        )
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def provision(
        self,
        slug: str,
        product_name: str,
        monthly_amount_usd: float,
    ) -> BillingProvision:
        cents = max(100, int(round(monthly_amount_usd * 100)))
        product = self._post(
            "/products",
            {
                "name": product_name,
                "metadata[factory_slug]": slug,
            },
            f"{slug}-product-v1",
        )
        price = self._post(
            "/prices",
            {
                "product": product["id"],
                "currency": "usd",
                "unit_amount": str(cents),
                "recurring[interval]": "month",
                "metadata[factory_slug]": slug,
            },
            f"{slug}-price-v1-{cents}",
        )
        return BillingProvision(
            product_id=product["id"],
            price_id=price["id"],
            monthly_amount_usd=cents / 100,
        )
