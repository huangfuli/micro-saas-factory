import { legalBusinessName, supportEmail } from "@/lib/legal";

export default function PrivacyPage() {
  return (
    <main className="shell legal">
      <h1>Privacy Policy</h1>
      <p>
        This policy explains how {legalBusinessName} handles information when
        you use SupplyExtract, a SaaS web tool that converts supplier invoice
        and purchase-order PDFs into reviewable structured data.
      </p>

      <h2>Documents you upload</h2>
      <p>
        When you request an extraction, the PDF you choose is sent from the
        application server to OpenAI&apos;s API so that document fields and line
        items can be extracted. The SupplyExtract MVP does not intentionally
        write uploaded PDF bytes to its own database or persistent application
        filesystem.
      </p>
      <p>
        Processing by OpenAI is subject to the provider&apos;s applicable API
        terms, privacy commitments, and data-handling settings. SupplyExtract
        does not claim that third-party processors have zero retention in every
        circumstance.
      </p>

      <h2>Extracted data</h2>
      <p>
        Extracted values are returned to your browser for review and export.
        The MVP is designed around review-before-export and does not use the
        extracted result as an automatic accounting approval or payment
        instruction.
      </p>

      <h2>Account and billing information</h2>
      <p>
        Subscription checkout, billing and license-key issuance are handled by
        Lemon Squeezy. Lemon Squeezy processes billing information under its own
        terms and privacy practices. This application does not need to store
        full payment-card details.
      </p>

      <h2>Operational information</h2>
      <p>
        We may process limited technical information needed to operate,
        troubleshoot, secure and prevent abuse of the service. Application logs
        should not intentionally contain uploaded PDF contents or extracted
        supplier-document fields.
      </p>

      <h2>Your responsibility</h2>
      <p>
        Upload documents only when you have the right to process them. Do not
        rely on AI-extracted values without checking them against the original
        document.
      </p>

      <h2>Contact</h2>
      <p>
        Privacy or deletion questions can be sent to {supportEmail}.
      </p>
    </main>
  );
}
