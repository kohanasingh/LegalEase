export default function WhatsAppDemoPage() {
  return (
    <main className="mx-auto max-w-xl flex-1 px-4 py-16 text-center">
      <h1 className="text-3xl font-bold text-slate-900">LegalEase on WhatsApp</h1>
      <p className="mt-4 text-slate-700">
        The same upload-and-ask pipeline as the web app, available through a Twilio
        WhatsApp Sandbox number — send a document as a PDF or Word (.docx) file, get the
        same plain-language analysis, and ask follow-up questions right in the chat.
      </p>

      <div className="mt-8 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-8 text-slate-500">
        <p className="font-medium">Coming soon</p>
        <p className="mt-1 text-sm">
          The WhatsApp integration is being built next. Once live, this page will show
          the sandbox number and a QR code to start a chat directly.
        </p>
      </div>
    </main>
  );
}
