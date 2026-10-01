import json
from pathlib import Path
from schemas.product import ProductPackage


class NextJsScaffolder:
    """Writes a dependency-light Next.js App Router project without shelling out."""

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
            "src/app/api/health/route.ts": "export async function GET() { return Response.json({ ok: true }); }\n",
            "src/app/api/jobs/route.ts": self._jobs_route(package),
            "src/app/api/billing/checkout/route.ts": self._checkout_route(),
            "src/lib/product.ts": self._product_config(package),
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
        return f"""import './globals.css';

export const metadata = {{
  title: '{name}',
  description: 'AI-generated MicroSaaS MVP',
}};

export default function RootLayout({{ children }}: Readonly<{{ children: React.ReactNode }}>) {{
  return <html lang="en"><body>{{children}}</body></html>;
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
      <nav><strong>{package.positioning.product_name}</strong><Link href="/dashboard">Open app</Link></nav>
      <section className="hero">
        <span className="eyebrow">Focused MicroSaaS</span>
        <h1>{l.headline}</h1>
        <p>{l.subheadline}</p>
        <div className="actions">
          <Link className="button" href="/dashboard">{l.primary_cta}</Link>
          <span>{l.pricing_anchor}</span>
        </div>
      </section>
      <section className="grid">
        <article><h2>The problem</h2><ul>{problems}</ul></article>
        <article><h2>The MVP</h2><ul>{solutions}</ul></article>
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
        <p>This product-specific workflow is the Builder Agent's T003 implementation target.</p>
        <ul>{features}</ul>
        <form action="/api/jobs" method="post">
          <button className="button" type="submit">Run sample job</button>
        </form>
      </section>
      <section className="panel">
        <h2>Founding plan</h2>
        <p>{package.pricing_plan}</p>
        <form action="/api/billing/checkout" method="post">
          <button className="button" type="submit">Subscribe with Stripe</button>
        </form>
      </section>
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
    message: 'T003 core workflow adapter is ready for implementation.'
  }}, {{ status: 202 }});
}}
"""

    @staticmethod
    def _checkout_route() -> str:
        return """export async function POST(request: Request) {
  const secret = process.env.STRIPE_SECRET_KEY;
  const price = process.env.STRIPE_PRICE_ID;
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin;

  if (!secret || !price) {
    return Response.json(
      { error: 'Stripe is not configured.' },
      { status: 503 }
    );
  }

  const params = new URLSearchParams();
  params.set('mode', 'subscription');
  params.set('line_items[0][price]', price);
  params.set('line_items[0][quantity]', '1');
  params.set('success_url', appUrl + '/dashboard?checkout=success');
  params.set('cancel_url', appUrl + '/dashboard?checkout=cancelled');

  const response = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + secret,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
    cache: 'no-store',
  });

  const payload = await response.json() as { url?: string; error?: { message?: string } };
  if (!response.ok || !payload.url) {
    return Response.json(
      { error: payload.error?.message || 'Unable to start checkout.' },
      { status: 502 }
    );
  }

  return Response.redirect(payload.url, 303);
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
        return "export const product = " + json.dumps(payload, ensure_ascii=False, indent=2) + " as const;\n"

    @staticmethod
    def _readme(package: ProductPackage) -> str:
        return f"""# {package.positioning.product_name}

Generated by MicroSaaS Factory Builder Agent v0.2.

Goal:
{package.builder_manifest.build_goal}

Local run requires Node.js 20.9+.

Commands:
npm install
npm run dev

QA commands:
npm run lint
npm run build

Billing:
Set NEXT_PUBLIC_APP_URL, STRIPE_SECRET_KEY, and STRIPE_PRICE_ID.
The generated checkout route creates a hosted Stripe Checkout Session in subscription mode.

See docs/ for PRD, technical specification and Builder tasks.
"""

    @staticmethod
    def _css() -> str:
        return """*{box-sizing:border-box}body{margin:0;background:#0a0a0a;color:#f5f5f5;font-family:Arial,sans-serif}.shell{max-width:1040px;margin:auto;padding:32px 24px}nav{display:flex;justify-content:space-between;align-items:center}a{color:inherit}.hero{padding:96px 0 64px}.hero h1{font-size:clamp(42px,7vw,82px);line-height:.95;max-width:900px}.hero p{font-size:20px;max-width:720px;color:#b8b8b8}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.2em;color:#9dffb0}.actions{display:flex;gap:20px;align-items:center;margin-top:28px}.button{display:inline-block;border:0;border-radius:10px;background:#f5f5f5;color:#0a0a0a;padding:13px 18px;text-decoration:none;font-weight:700;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}.grid article,.panel{border:1px solid #292929;border-radius:18px;padding:28px;background:#111;margin-top:20px}li{margin:10px 0;color:#d2d2d2}
"""
