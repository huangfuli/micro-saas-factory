import json
import os
from urllib.parse import quote
from urllib.request import Request, urlopen

from schemas.launch import BillingProvision


class LemonSqueezyProvisioner:
    api = "https://api.lemonsqueezy.com/v1"

    def _headers(self) -> dict[str, str]:
        key = os.getenv("LEMON_SQUEEZY_API_KEY", "").strip()
        if not key:
            raise RuntimeError("LEMON_SQUEEZY_API_KEY is required.")
        return {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {key}",
        }

    def _get(self, path: str):
        request = Request(self.api + path, headers=self._headers())
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict):
        request = Request(
            self.api + path,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=self._headers(),
        )
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def verify_plan(self) -> BillingProvision:
        store_id = os.getenv("LEMON_SQUEEZY_STORE_ID", "").strip()
        variant_id = os.getenv("LEMON_SQUEEZY_VARIANT_ID", "").strip()
        if not store_id or not variant_id:
            raise RuntimeError(
                "LEMON_SQUEEZY_STORE_ID and LEMON_SQUEEZY_VARIANT_ID are required. "
                "Create the real SaaS product and subscription variant in Lemon Squeezy "
                "test mode first, then configure their IDs."
            )

        variant = self._get(f"/variants/{quote(variant_id)}")["data"]
        variant_attrs = variant["attributes"]
        product_id = str(variant_attrs["product_id"])

        product = self._get(f"/products/{quote(product_id)}")["data"]
        product_attrs = product["attributes"]

        prices = self._get(
            f"/prices?filter[variant_id]={quote(variant_id)}"
        ).get("data", [])
        if not prices:
            raise RuntimeError("No Lemon Squeezy Price object exists for the configured variant.")

        current_price = prices[0]["attributes"]

        if str(product_attrs["store_id"]) != store_id:
            raise RuntimeError(
                "Configured Lemon Squeezy variant does not belong to the configured store."
            )
        if product_attrs.get("status") != "published":
            raise RuntimeError("Lemon Squeezy product must be published before launch.")
        if variant_attrs.get("status") not in {"published", "pending"}:
            raise RuntimeError("Lemon Squeezy variant is not active/published.")
        if current_price.get("category") != "subscription":
            raise RuntimeError("Configured Lemon Squeezy variant must use subscription pricing.")
        if current_price.get("scheme") != "standard":
            raise RuntimeError(
                "Factory v0.2 currently requires standard flat subscription pricing."
            )
        if (
            current_price.get("renewal_interval_unit") != "month"
            or int(current_price.get("renewal_interval_quantity") or 1) != 1
        ):
            raise RuntimeError("Factory v0.2 expects a monthly subscription variant.")

        description = (product_attrs.get("description") or "").strip()
        if len(description) < 20:
            raise RuntimeError(
                "Lemon Squeezy product description is too thin. "
                "Describe the actual SaaS product clearly before merchant review."
            )

        cents = current_price.get("unit_price")
        if cents is None:
            decimal = current_price.get("unit_price_decimal")
            cents = float(decimal) if decimal is not None else 0

        cents = float(cents or 0)
        if cents <= 0:
            raise RuntimeError(
                "Unable to verify a positive Lemon Squeezy subscription price."
            )

        return BillingProvision(
            provider="lemon_squeezy",
            store_id=store_id,
            product_id=product_id,
            variant_id=variant_id,
            monthly_amount_usd=cents / 100,
            test_mode=bool(variant_attrs.get("test_mode")),
            checkout_url=product_attrs.get("buy_now_url"),
        )

    def ensure_webhook(
        self,
        deployment_url: str,
        test_mode: bool,
    ) -> str:
        store_id = os.getenv("LEMON_SQUEEZY_STORE_ID", "").strip()
        secret = os.getenv("LEMON_SQUEEZY_WEBHOOK_SECRET", "").strip()
        if not secret:
            raise RuntimeError("LEMON_SQUEEZY_WEBHOOK_SECRET is required.")
        if not (6 <= len(secret) <= 40):
            raise RuntimeError("Lemon Squeezy webhook secret must be 6-40 characters.")

        target = deployment_url.rstrip("/") + "/api/billing/webhook"
        existing = self._get(
            f"/webhooks?filter[store_id]={quote(store_id)}"
        ).get("data", [])
        if isinstance(existing, dict):
            existing = [existing]

        for item in existing:
            if (item.get("attributes") or {}).get("url") == target:
                return str(item.get("id"))

        payload = {
            "data": {
                "type": "webhooks",
                "attributes": {
                    "url": target,
                    "events": [
                        "order_created",
                        "order_refunded",
                        "subscription_created",
                        "subscription_updated",
                        "subscription_cancelled",
                        "subscription_expired",
                        "subscription_payment_failed",
                        "subscription_payment_success",
                    ],
                    "secret": secret,
                    "test_mode": test_mode,
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": store_id,
                        }
                    }
                },
            }
        }
        created = self._post("/webhooks", payload)
        return str(created["data"]["id"])
