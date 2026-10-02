import Link from "next/link";

export default function Home() {
  return (
    <main className="shell">
      <nav>
        <strong>SupplyExtract</strong>
        <div className="navLinks">
          <Link href="/pricing">Pricing</Link>
          <Link href="/dashboard">Open extractor</Link>
        </div>
      </nav>

      <section className="hero">
        <span className="eyebrow">Supplier PDF extraction</span>
        <h1>Stop retyping supplier PDFs into spreadsheets.</h1>
        <p>
          Upload a supplier invoice or purchase order, review the extracted
          header and line items, then export the values you approved as CSV or
          JSON.
        </p>
        <div className="actions">
          <Link className="button" href="/dashboard">
            Try the extractor
          </Link>
          <Link href="/pricing">View subscription pricing</Link>
        </div>
      </section>

      <section className="grid">
        <article>
          <h2>What it extracts</h2>
          <ul>
            <li>Vendor and document identifiers</li>
            <li>Document date, currency and totals</li>
            <li>SKU, description, quantity, unit price and line totals</li>
          </ul>
        </article>
        <article>
          <h2>Review before export</h2>
          <ul>
            <li>Edit extracted document fields</li>
            <li>Edit, add or remove line items</li>
            <li>Download the reviewed result as CSV or JSON</li>
          </ul>
        </article>
      </section>

      <section className="panel">
        <h2>Important: extraction is not guaranteed to be correct</h2>
        <p>
          Supplier documents vary in layout and scan quality. SupplyExtract uses
          AI to propose structured values, and those values can be incomplete or
          incorrect. Review the result against the original PDF before using it
          for accounting, procurement or payment decisions.
        </p>
      </section>

      <section className="panel">
        <h2>Current MVP scope</h2>
        <p>
          SupplyExtract currently handles one PDF at a time and focuses on
          supplier invoices and purchase orders. It is not an accounting system,
          invoice-approval engine, ERP posting service, or bank-statement
          processor.
        </p>
      </section>
    </main>
  );
}
