import json
from pathlib import Path

from schemas.product import ProductPackage


class NextJsScaffolder:
    """Writes a review-ready Next.js App Router SaaS scaffold."""

    def create(self, workspace: Path, package: ProductPackage) -> list[str]:
        workspace.mkdir(parents=True, exist_ok=True)
        slug = package.builder_manifest.product_slug
        name = package.positioning.product_name

        files = {
            "package.json": json.dumps({
                "name": slug,
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "eslint ."
                },
                "dependencies": {
                    "next": "^16.3.0",
                    "react": "^19.0.0",
                    "react-dom": "^19.0.0"
                },
                "devDependencies": {
                    "@types/node": "^22.0.0",
                    "@types/react": "^19.0.0",
                    "@types/react-dom": "^19.0.0",
                    "eslint": "^9.0.0",
                    "eslint-config-next": "^16.3.0",
                    "typescript": "^5.7.0"
                }
            }, indent=2),
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2017",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": False,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {"@/*": ["./src/*"]}
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"]
            }, indent=2),
            "next-env.d.ts": '/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n',
            "next.config.ts": "import type { NextConfig } from 'next';\n\nconst nextConfig: NextConfig = {};\nexport default nextConfig;\n",
            "eslint.config.mjs": "import { defineConfig, globalIgnores } from 'eslint/config';\nimport nextVitals from 'eslint-config-next/core-web-vitals';\n\nexport default defineConfig([nextVitals, globalIgnores(['.next/**','out/**','build/**'])]);\n",
            ".gitignore": "node_modules\n.next\n.env\n.env.local\n.vercel\ncoverage\n",
            ".vercelignore": ".factory\ndocs\n*.zip\n",
            ".env.example": "\n".join(f"{x}=" for x in package.builder_manifest.required_env) + "\n",
            "src/app/layout.tsx": self._layout(name),
            "src/app/page.tsx": self._landing(package),
            "src/app/globals.css": self._css(),
            "src/app/dashboard/page.tsx": self._dashboard(package),
            "src/app/pricing/page.tsx": self._pricing(package),
            "src/app/privacy/page.tsx": self._privacy(package),
            "src/app/terms/page.tsx": self._terms(package),
            "src/app/refund-policy/page.tsx": self._refund(package),
            "src/app/contact/page.tsx": self._contact(package),
            "src/app/api/health/route.ts": "export async function GET() { return Response.json({ ok: true }); }\n",
            "src/app/api/jobs/route.ts": self._jobs_route(package),
            "src/app/api/billing/checkout/route.ts": self._checkout_route(),
            "src/app/api/billing/webhook/route.ts": self._webhook_route(),
            "src/lib/product.ts": self._product_config(package),
            "src/lib/legal.ts": self._legal_config(),
            "README.md": self._readme(package),
        }

        created = []
        for relative, content in files.items():
            path = workspace / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(relative)
        return created

    @staticmethod
    def _layout(name: str) -> str:
        return f"""import Link from 'next/link';
import './globals.css';

export const metadata = {{
  title: '{name}',
  description: 'Focused SaaS web application',
}};

export default function RootLayout({{ children }}: Readonly<{{ children: React.ReactNode }}>) {{
  return (
    <html lang="en">
      <body>
        {{children}}
        <footer className="footer shell">
          <span>© {{new Date().getFullYear()}} {name}</span>
          <div className="footerLinks">
            <Link href="/pricing">Pricing</Link>
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
            <Link href="/refund-policy">Refunds</Link>
            <Link href="/contact">Contact</Link>
          </div>
        </footer>
      </body>
    </html>
  );
}}
"""

    @staticmethod
    def _landing(package: ProductPackage) -> str:
        l = package.landing_page
        problems = "".join(f"<li>{x}</li>" for x in l.problem_bullets)
        solutions = "".join(f"<li>{x}</li>" for x in l.solution_bullets)
        return f"""import Link from 'next/link';

export default function Home() {{
  return (
    <main className="shell">
      <nav>
        <strong>{package.positioning.product_name}</strong>
        <div className="navLinks">
          <Link href="/pricing">Pricing</Link>
          <Link href="/dashboard">Open app</Link>
        </div>
      </nav>
      <section className="hero">
        <span className="eyebrow">Focused SaaS web tool</span>
        <h1>{l.headline}</h1>
        <p>{l.subheadline}</p>
        <div className="actions">
          <Link className="button" href="/dashboard">{l.primary_cta}</Link>
          <Link href="/pricing">View pricing</Link>
        </div>
      </section>
      <section className="grid">
        <article>
          <h2>The workflow problem</h2>
          <ul>{problems}</ul>
        </article>
        <article>
          <h2>What this product does</h2>
          <ul>{solutions}</ul>
        </article>
      </section>
      <section className="panel">
        <h2>Product scope</h2>
        <p>
          {package.positioning.product_name} is a web-based SaaS tool for
          {package.positioning.target_user}. Its current purpose is:
          {package.positioning.painful_job}
        </p>
        <p>
          The service is intentionally narrow. The website describes the current
          MVP only; it does not claim customers, partnerships, usage volume,
          awards, or functionality that has not been implemented.
        </p>
      </section>
    </main>
  );
}}
"""

    @staticmethod
    def _dashboard(package: ProductPackage) -> str:
        features = "".join(f"<li>{x}</li>" for x in package.prd.in_scope)
        return f"""export default function Dashboard() {{
  return (
    <main className="shell">
      <span className="eyebrow">MVP workspace</span>
      <h1>{package.positioning.product_name}</h1>
      <p>{package.positioning.one_liner}</p>
      <section className="panel">
        <h2>Core workflow</h2>
        <ul>{features}</ul>
        <form action="/api/jobs" method="post">
          <button className="button" type="submit">Run workflow</button>
        </form>
      </section>
      <section className="panel">
        <h2>Subscription</h2>
        <p>
          The paid plan and billing interval are shown on the Pricing page.
          Checkout is handled by Lemon Squeezy.
        </p>
        <form action="/api/billing/checkout" method="post">
          <button className="button" type="submit">Subscribe with Lemon Squeezy</button>
        </form>
      </section>
    </main>
  );
}}
"""

    @staticmethod
    def _pricing(package: ProductPackage) -> str:
        return f"""import {{ planPrice }} from '@/lib/legal';

export default function PricingPage() {{
  return (
    <main className="shell legal">
      <span className="eyebrow">Pricing</span>
      <h1>Simple subscription pricing</h1>
      <section className="panel">
        <h2>{package.positioning.product_name}</h2>
        <p className="price">{{planPrice}}</p>
        <p>{package.positioning.one_liner}</p>
        <p>
          The subscription covers access to the current SaaS workflow described
          on this website. Features outside the published product scope are not
          included unless this page is updated to say otherwise.
        </p>
        <form action="/api/billing/checkout" method="post">
          <button className="button" type="submit">Subscribe</button>
        </form>
      </section>
      <p>
        Payments and subscription billing are processed by Lemon Squeezy as our
        payment provider and Merchant of Record.
      </p>
    </main>
  );
}}
"""

    @staticmethod
    def _privacy(package: ProductPackage) -> str:
        return f"""import {{ legalBusinessName, supportEmail }} from '@/lib/legal';

export default function PrivacyPage() {{
  return (
    <main className="shell legal">
      <h1>Privacy Policy</h1>
      <p>
        This policy explains how {{legalBusinessName}} handles information when
        you use {package.positioning.product_name}, a SaaS web tool for
        {package.positioning.target_user}.
      </p>
      <h2>Information we process</h2>
      <p>
        We may process account information, data you intentionally submit to the
        product, generated results, basic usage events, and technical information
        needed to operate, secure, and improve the service.
      </p>
      <h2>Payments</h2>
      <p>
        Subscription checkout and payment processing are handled by Lemon
        Squeezy. We do not need to store full payment-card details in this
        application. Lemon Squeezy may process billing information under its own
        terms and privacy practices.
      </p>
      <h2>Use and retention</h2>
      <p>
        We use information to provide the product, troubleshoot failures,
        prevent abuse, provide support, and meet legal obligations. We retain
        data only for as long as reasonably needed for those purposes and the
        operation of your account.
      </p>
      <h2>Your choices</h2>
      <p>
        You may contact us to ask about access, correction, or deletion of
        information associated with your account, subject to applicable legal
        and operational requirements.
      </p>
      <h2>Contact</h2>
      <p>Email: {{supportEmail}}</p>
    </main>
  );
}}
"""

    @staticmethod
    def _terms(package: ProductPackage) -> str:
        return f"""import {{ legalBusinessName, supportEmail }} from '@/lib/legal';

export default function TermsPage() {{
  return (
    <main className="shell legal">
      <h1>Terms of Service</h1>
      <p>
        These terms apply to use of {package.positioning.product_name}, provided
        by {{legalBusinessName}}.
      </p>
      <h2>Service</h2>
      <p>
        The service provides the web-based workflow described on the product and
        pricing pages. We may improve or change the service while keeping public
        descriptions reasonably accurate.
      </p>
      <h2>Accounts and acceptable use</h2>
      <p>
        You are responsible for lawful use of the service and for data you submit.
        You may not use the service to violate law, interfere with other users,
        probe or abuse infrastructure, or submit material you do not have the
        right to process.
      </p>
      <h2>Billing</h2>
      <p>
        Paid subscriptions are purchased through Lemon Squeezy. The price and
        billing interval shown on the Pricing page should match the selected
        Lemon Squeezy subscription variant.
      </p>
      <h2>Availability</h2>
      <p>
        We aim to operate the service reliably, but do not promise uninterrupted
        availability or results beyond the functionality explicitly described
        on this website.
      </p>
      <h2>Contact</h2>
      <p>Questions about these terms can be sent to {{supportEmail}}.</p>
    </main>
  );
}}
"""

    @staticmethod
    def _refund(package: ProductPackage) -> str:
        return f"""import {{
  refundPolicyText,
  supportEmail,
}} from '@/lib/legal';

export default function RefundPolicyPage() {{
  return (
    <main className="shell legal">
      <h1>Refund Policy</h1>
      <p>{{refundPolicyText}}</p>
      <p>
        Refund requests and billing questions should identify the email used for
        the purchase and the relevant transaction. Payments are processed by
        Lemon Squeezy, which may also be involved in handling payment and refund
        operations as Merchant of Record.
      </p>
      <p>
        This policy does not limit rights that cannot be waived under applicable
        consumer law.
      </p>
      <h2>Contact</h2>
      <p>Email: {{supportEmail}}</p>
    </main>
  );
}}
"""

    @staticmethod
    def _contact(package: ProductPackage) -> str:
        return f"""import {{
  legalBusinessName,
  supportEmail,
}} from '@/lib/legal';

export default function ContactPage() {{
  return (
    <main className="shell legal">
      <h1>Contact</h1>
      <p>
        {package.positioning.product_name} is operated by {{legalBusinessName}}.
        For product support, account questions, billing questions, privacy
        requests, or refund requests, contact us using the email below.
      </p>
      <section className="panel">
        <h2>Support email</h2>
        <p>{{supportEmail}}</p>
      </section>
      <p>
        Please do not send passwords, full payment-card numbers, or other
        sensitive authentication credentials by email.
      </p>
    </main>
  );
}}
"""

    @staticmethod
    def _jobs_route(package: ProductPackage) -> str:
        slug_json = json.dumps(package.builder_manifest.product_slug)
        return f"""export async function POST() {{
  return Response.json({{
    id: crypto.randomUUID(),
    status: 'queued',
    product: {slug_json},
    message: 'Core workflow request accepted.'
  }}, {{ status: 202 }});
}}
"""

    @staticmethod
    def _checkout_route() -> str:
        return """export async function POST(request: Request) {
  const apiKey = process.env.LEMON_SQUEEZY_API_KEY;
  const storeId = process.env.LEMON_SQUEEZY_STORE_ID;
  const variantId = process.env.LEMON_SQUEEZY_VARIANT_ID;

  if (!apiKey || !storeId || !variantId) {
    return Response.json(
      { error: 'Billing is not configured.' },
      { status: 503 }
    );
  }

  const origin = new URL(request.url).origin;
  const response = await fetch('https://api.lemonsqueezy.com/v1/checkouts', {
    method: 'POST',
    headers: {
      Accept: 'application/vnd.api+json',
      'Content-Type': 'application/vnd.api+json',
      Authorization: 'Bearer ' + apiKey,
    },
    body: JSON.stringify({
      data: {
        type: 'checkouts',
        attributes: {
          product_options: {
            redirect_url: origin + '/dashboard?checkout=success',
          },
          checkout_options: {
            embed: false,
          },
        },
        relationships: {
          store: {
            data: { type: 'stores', id: storeId },
          },
          variant: {
            data: { type: 'variants', id: variantId },
          },
        },
      },
    }),
    cache: 'no-store',
  });

  const payload = await response.json() as {
    data?: { attributes?: { url?: string } };
    errors?: Array<{ detail?: string }>;
  };
  const checkoutUrl = payload.data?.attributes?.url;

  if (!response.ok || !checkoutUrl) {
    return Response.json(
      { error: payload.errors?.[0]?.detail || 'Unable to start checkout.' },
      { status: 502 }
    );
  }

  return Response.redirect(checkoutUrl, 303);
}
"""

    @staticmethod
    def _webhook_route() -> str:
        return """import { createHmac, timingSafeEqual } from 'node:crypto';

export async function POST(request: Request) {
  const secret = process.env.LEMON_SQUEEZY_WEBHOOK_SECRET;
  const signature = request.headers.get('x-signature');
  if (!secret || !signature) {
    return Response.json({ error: 'Missing signature.' }, { status: 401 });
  }

  const rawBody = await request.text();
  const digest = createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');

  const expected = Buffer.from(digest, 'utf8');
  const received = Buffer.from(signature, 'utf8');
  if (expected.length !== received.length || !timingSafeEqual(expected, received)) {
    return Response.json({ error: 'Invalid signature.' }, { status: 401 });
  }

  const event = JSON.parse(rawBody) as {
    meta?: { event_name?: string; custom_data?: Record<string, unknown> };
    data?: { type?: string; id?: string };
  };

  // Builder v0.2 validates the webhook and acknowledges it.
  // Product-specific entitlement persistence belongs in the app's domain layer.
  return Response.json({
    received: true,
    event: event.meta?.event_name || 'unknown',
    resource: event.data?.type || 'unknown',
  });
}
"""

    @staticmethod
    def _product_config(package: ProductPackage) -> str:
        payload = {
            "name": package.positioning.product_name,
            "targetUser": package.positioning.target_user,
            "value": package.positioning.unique_value,
            "pricing": package.pricing_plan,
            "features": package.prd.in_scope,
        }
        return "export const product = " + json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ) + " as const;\n"

    @staticmethod
    def _legal_config() -> str:
        return """function required(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    return 'Configuration required before public launch';
  }
  return value;
}

export const legalBusinessName = required('NEXT_PUBLIC_LEGAL_BUSINESS_NAME');
export const supportEmail = required('NEXT_PUBLIC_SUPPORT_EMAIL');
export const planPrice = required('NEXT_PUBLIC_PLAN_PRICE');
export const refundPolicyText = required('NEXT_PUBLIC_REFUND_POLICY_TEXT');
"""

    @staticmethod
    def _readme(package: ProductPackage) -> str:
        return f"""# {package.positioning.product_name}

Generated by MicroSaaS Factory Builder v0.2.

Goal:
{package.builder_manifest.build_goal}

Local run requires Node.js 20.9+.

Commands:
npm install
npm run dev

QA:
npm run lint
npm run build

Lemon Squeezy:
1. Create the real SaaS subscription product/variant in Lemon Squeezy test mode.
2. Set LEMON_SQUEEZY_API_KEY, LEMON_SQUEEZY_STORE_ID,
   LEMON_SQUEEZY_VARIANT_ID and LEMON_SQUEEZY_WEBHOOK_SECRET.
3. Keep the product description, pricing and website copy truthful and aligned.
4. Use live-mode IDs/keys only after the Lemon Squeezy store is activated.

Merchant-review website:
Set NEXT_PUBLIC_LEGAL_BUSINESS_NAME, NEXT_PUBLIC_SUPPORT_EMAIL,
NEXT_PUBLIC_PLAN_PRICE and NEXT_PUBLIC_REFUND_POLICY_TEXT before public launch.
The factory intentionally does not generate fake customers, testimonials,
usage counts, partnerships, awards or revenue claims.

See docs/ for PRD, technical specification and Builder tasks.
"""

    @staticmethod
    def _css() -> str:
        return """*{box-sizing:border-box}body{margin:0;background:#0a0a0a;color:#f5f5f5;font-family:Arial,sans-serif}.shell{max-width:1040px;margin:auto;padding:32px 24px}nav{display:flex;justify-content:space-between;align-items:center;gap:24px}.navLinks,.footerLinks{display:flex;gap:18px;flex-wrap:wrap}a{color:inherit}.hero{padding:96px 0 64px}.hero h1{font-size:clamp(42px,7vw,82px);line-height:.95;max-width:900px}.hero p,.legal p{font-size:18px;line-height:1.65;max-width:800px;color:#c8c8c8}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.2em;color:#9dffb0}.actions{display:flex;gap:20px;align-items:center;margin-top:28px}.button{display:inline-block;border:0;border-radius:10px;background:#f5f5f5;color:#0a0a0a;padding:13px 18px;text-decoration:none;font-weight:700;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}.grid article,.panel{border:1px solid #292929;border-radius:18px;padding:28px;background:#111;margin-top:20px}li{margin:10px 0;color:#d2d2d2}.legal{max-width:820px}.legal h1{font-size:48px}.legal h2{margin-top:34px}.price{font-size:34px!important;color:#fff!important;font-weight:700}.footer{border-top:1px solid #242424;margin-top:72px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;color:#a8a8a8}
"""
