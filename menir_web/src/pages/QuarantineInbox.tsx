import React, { useEffect, useState } from 'react';

interface QuarantineDocument {
  id: string;
  name: string;
  file_hash: string;
  reason: string;
  date: string;
}

const QuarantineInbox: React.FC = () => {
  const [documents, setDocuments] = useState<QuarantineDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<QuarantineDocument | null>(null);
  const [correctionData, setCorrectionData] = useState<any>({});
  
  const fetchQuarantine = async () => {
    try {
      const resp = await fetch('/api/v3/documents/quarantine');
      if (resp.ok) {
        const data = await resp.json();
        setDocuments(data.documents || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchQuarantine();
  }, []);

  const handleRetry = async () => {
    if (!selectedDoc) return;
    try {
      const resp = await fetch(`/api/v3/documents/${selectedDoc.id}/retry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(correctionData)
      });
      if (resp.ok) {
        alert('Documento reenviado para processamento!');
        setSelectedDoc(null);
        fetchQuarantine();
      }
    } catch (e) {
      console.error(e);
      alert('Erro ao reenviar.');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100%' }}>
      {/* Sidebar List */}
      <div style={{ width: '30%', borderRight: '1px solid #ccc', overflowY: 'auto', padding: '1rem' }}>
        <h2>Quarantine Inbox</h2>
        {documents.map(doc => (
          <div 
            key={doc.id} 
            onClick={() => { setSelectedDoc(doc); setCorrectionData({}); }}
            style={{ 
              padding: '1rem', 
              border: '1px solid #eee', 
              marginBottom: '0.5rem', 
              cursor: 'pointer',
              backgroundColor: selectedDoc?.id === doc.id ? '#f0f0ff' : 'white'
            }}
          >
            <strong>{doc.name}</strong>
            <p style={{ color: 'red', fontSize: '0.8rem' }}>{doc.reason}</p>
            <span style={{ fontSize: '0.7rem', color: '#888' }}>{doc.date}</span>
          </div>
        ))}
      </div>

      {/* Workspace Spilt View */}
      {selectedDoc ? (
        <div style={{ width: '70%', display: 'flex' }}>
          {/* PDF Viewer */}
          <div style={{ width: '50%', backgroundColor: '#555', padding: '1rem' }}>
             <object 
                data={`/api/v3/files/${selectedDoc.file_hash}`} 
                type="application/pdf" 
                width="100%" 
                height="100%"
              >
                  <p>PDF render não suportado. <a href={`/api/v3/files/${selectedDoc.file_hash}`}>Baixar PDF</a></p>
              </object>
          </div>
          {/* Correction Form */}
          <div style={{ width: '50%', padding: '2rem' }}>
             <h3>Correção Manual</h3>
             <p>Documento retido por: <strong>{selectedDoc.reason}</strong></p>
             
             <div style={{ marginTop: '2rem' }}>
               <label>Dados corrigidos (JSON):</label><br/>
               <textarea 
                  rows={10} 
                  style={{ width: '100%', marginTop: '0.5rem' }} 
                  value={JSON.stringify(correctionData, null, 2)}
                  onChange={(e) => {
                    try {
                      setCorrectionData(JSON.parse(e.target.value));
                    } catch {}
                  }}
               />
             </div>
             
             <button 
                onClick={handleRetry}
                style={{ marginTop: '2rem', padding: '0.8rem 1.5rem', backgroundColor: '#0070f3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
             >
               Corrigir e Re-submeter
             </button>
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <p>Selecione um documento na quarentena para iniciar a correção.</p>
        </div>
      )}
    </div>
  );
};

export default QuarantineInbox;
