"use client";

import { FormEvent, useMemo, useState } from "react";

type LineItem = {
  line_no: string | null;
  sku: string | null;
  description: string | null;
  quantity: string | null;
  unit: string | null;
  unit_price: string | null;
  line_total: string | null;
};

type ExtractedDocument = {
  document_type: string | null;
  vendor_name: string | null;
  document_number: string | null;
  document_date: string | null;
  currency: string | null;
  subtotal: string | null;
  tax: string | null;
  total: string | null;
  line_items: LineItem[];
  warnings: string[];
};

const emptyItem: LineItem = {
  line_no: null,
  sku: null,
  description: null,
  quantity: null,
  unit: null,
  unit_price: null,
  line_total: null,
};

const headerFields: Array<keyof Omit<ExtractedDocument, "line_items" | "warnings">> = [
  "document_type",
  "vendor_name",
  "document_number",
  "document_date",
  "currency",
  "subtotal",
  "tax",
  "total",
];

const lineFields: Array<keyof LineItem> = [
  "line_no",
  "sku",
  "description",
  "quantity",
  "unit",
  "unit_price",
  "line_total",
];

function label(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function csvCell(value: unknown) {
  let text = value == null ? "" : String(value);
  if (/^[=+\-@]/.test(text)) {
    text = "'" + text;
  }
  return '"' + text.replaceAll('"', '""') + '"';
}

function saveFile(name: string, type: string, content: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [licenseKey, setLicenseKey] = useState("");
  const [document, setDocument] = useState<ExtractedDocument | null>(null);
  const [access, setAccess] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const canExport = useMemo(
    () => Boolean(document && document.line_items.length >= 0),
    [document]
  );

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;

    setBusy(true);
    setError("");
    setDocument(null);

    const form = new FormData();
    form.append("file", file);
    form.append("licenseKey", licenseKey.trim());

    try {
      const response = await fetch("/api/extract", {
        method: "POST",
        body: form,
      });
      const payload = (await response.json()) as {
        document?: ExtractedDocument;
        access?: string;
        error?: string;
      };

      if (!response.ok || !payload.document) {
        throw new Error(payload.error || "Extraction failed.");
      }
      setDocument(payload.document);
      setAccess(payload.access || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed.");
    } finally {
      setBusy(false);
    }
  }

  function updateHeader(field: typeof headerFields[number], value: string) {
    setDocument((current) =>
      current ? { ...current, [field]: value || null } : current
    );
  }

  function updateLine(index: number, field: keyof LineItem, value: string) {
    setDocument((current) => {
      if (!current) return current;
      const lines = current.line_items.map((item, i) =>
        i === index ? { ...item, [field]: value || null } : item
      );
      return { ...current, line_items: lines };
    });
  }

  function addLine() {
    setDocument((current) =>
      current
        ? { ...current, line_items: [...current.line_items, { ...emptyItem }] }
        : current
    );
  }

  function removeLine(index: number) {
    setDocument((current) =>
      current
        ? {
            ...current,
            line_items: current.line_items.filter((_, i) => i !== index),
          }
        : current
    );
  }

  function downloadJson() {
    if (!document) return;
    saveFile(
      "supplyextract-reviewed.json",
      "application/json",
      JSON.stringify(document, null, 2)
    );
  }

  function downloadCsv() {
    if (!document) return;

    const columns = [
      "document_type",
      "vendor_name",
      "document_number",
      "document_date",
      "currency",
      "subtotal",
      "tax",
      "total",
      ...lineFields,
    ];

    const rows =
      document.line_items.length > 0
        ? document.line_items
        : [{ ...emptyItem }];

    const csv = [
      columns.map(csvCell).join(","),
      ...rows.map((item) =>
        [
          document.document_type,
          document.vendor_name,
          document.document_number,
          document.document_date,
          document.currency,
          document.subtotal,
          document.tax,
          document.total,
          ...lineFields.map((field) => item[field]),
        ]
          .map(csvCell)
          .join(",")
      ),
    ].join("\n");

    saveFile("supplyextract-reviewed.csv", "text/csv;charset=utf-8", csv);
  }

  return (
    <main className="shell">
      <span className="eyebrow">SupplyExtract MVP</span>
      <h1>Supplier PDF → reviewable rows</h1>
      <p>
        Upload one supplier invoice or purchase order PDF. SupplyExtract uses AI
        to propose structured fields; you review and correct them before export.
      </p>

      <section className="panel">
        <h2>1. Upload</h2>
        <form onSubmit={submit}>
          <label>
            PDF file
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              required
            />
          </label>
          <label>
            Subscription license key (optional when the public demo is enabled)
            <input
              type="password"
              autoComplete="off"
              value={licenseKey}
              onChange={(event) => setLicenseKey(event.target.value)}
              placeholder="Enter your Lemon Squeezy license key"
            />
          </label>
          <p className="muted">
            Paid access supports PDFs up to 10 MB. A public review/demo build may
            use a smaller unlicensed limit. Do not upload documents you are not
            authorized to process.
          </p>
          <button className="button" type="submit" disabled={busy || !file}>
            {busy ? "Extracting…" : "Extract fields"}
          </button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>

      {document ? (
        <>
          <section className="panel">
            <h2>2. Review document fields</h2>
            <p className="warning">
              AI extraction can be incomplete or wrong. Check every value
              against the original PDF before accounting, procurement or payment
              decisions.
            </p>
            {access ? <p className="muted">Access mode: {access}</p> : null}
            <div className="fieldGrid">
              {headerFields.map((field) => (
                <label key={field}>
                  {label(field)}
                  <input
                    value={String(document[field] ?? "")}
                    onChange={(event) => updateHeader(field, event.target.value)}
                  />
                </label>
              ))}
            </div>
            {document.warnings.length ? (
              <div className="warningBox">
                <strong>Extraction warnings</strong>
                <ul>
                  {document.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </section>

          <section className="panel">
            <div className="sectionRow">
              <h2>3. Review line items</h2>
              <button type="button" onClick={addLine}>
                Add line
              </button>
            </div>
            <div className="tableWrap">
              <table>
                <thead>
                  <tr>
                    {lineFields.map((field) => (
                      <th key={field}>{label(field)}</th>
                    ))}
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {document.line_items.map((item, index) => (
                    <tr key={index}>
                      {lineFields.map((field) => (
                        <td key={field}>
                          <input
                            value={item[field] ?? ""}
                            onChange={(event) =>
                              updateLine(index, field, event.target.value)
                            }
                          />
                        </td>
                      ))}
                      <td>
                        <button type="button" onClick={() => removeLine(index)}>
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel">
            <h2>4. Export reviewed data</h2>
            <div className="actions">
              <button
                className="button"
                type="button"
                disabled={!canExport}
                onClick={downloadCsv}
              >
                Download CSV
              </button>
              <button type="button" disabled={!canExport} onClick={downloadJson}>
                Download JSON
              </button>
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
