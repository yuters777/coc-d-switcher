export default function TemplatePreview() {
  return (
    <div className="flex-1 p-4 bg-white">
      <div className="border rounded p-8" style={{ minHeight: '800px' }}>
        <h2 className="text-center font-bold text-lg mb-4">
          Certificate of Conformity - Part I
        </h2>
        <div className="space-y-4 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-semibold">1. Supplier Serial No:</label>
              <p>COC_SV_Del165_20.03.2025.docx</p>
            </div>
            <div>
              <label className="font-semibold">3. Contract Number:</label>
              <p>697.12.5011.01</p>
            </div>
          </div>
          <div>
            <label className="font-semibold">2. Supplier:</label>
            <p>Elbit Systems C4I and Cyber Ltd</p>
            <p>2 Hamachshev, Netanya, Israel</p>
          </div>
          <div>
            <label className="font-semibold">6. Acquirer:</label>
            <p>NETHERLANDS MINISTRY OF DEFENCE</p>
          </div>
        </div>
      </div>
    </div>
  );
}