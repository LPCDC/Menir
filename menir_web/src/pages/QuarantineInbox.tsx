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

  const handleAction = async (action: 'reinject' | 'reject') => {
    if (!selectedDoc) return;
    try {
      const resp = await fetch(`/api/v3/documents/${selectedDoc.id}/retry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, corrected_fields: correctionData })
      });
      if (resp.ok) {
        alert(action === 'reinject' ? 'Documento reenviado para processamento!' : 'Documento rejeitado e arquivado.');
        setSelectedDoc(null);
        fetchQuarantine();
      }
    } catch (e) {
      console.error(e);
      alert('Erro ao processar ação.');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100%', fontFamily: 'Inter, sans-serif' }}>
      {/* Sidebar List - 20% Width */}
      <div style={{ width: '20%', borderRight: '1px solid #e0e0e0', backgroundColor: '#f9f9fb', overflowY: 'auto', padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: '#333' }}>Quarentena 🔴 {documents.length}</h2>
        {documents.map(doc => (
          <div 
            key={doc.id} 
            onClick={() => { setSelectedDoc(doc); setCorrectionData({}); }}
            style={{ 
              padding: '1rem', 
              borderRadius: '8px',
              border: selectedDoc?.id === doc.id ? '2px solid #0056b3' : '1px solid #ddd', 
              marginBottom: '0.8rem', 
              cursor: 'pointer',
              backgroundColor: selectedDoc?.id === doc.id ? '#ebf4ff' : 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}
          >
            <strong style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.3rem', wordBreak: 'break-all' }}>{doc.name}</strong>
            <p style={{ color: '#d32f2f', fontSize: '0.8rem', margin: '0 0 0.5rem 0', fontWeight: 600 }}>⚠️ {doc.reason.substring(0, 30)}...</p>
            <span style={{ fontSize: '0.7rem', color: '#888' }}>{new Date(doc.date).toLocaleString()}</span>
          </div>
        ))}
        {documents.length === 0 && <p style={{ color: '#888', fontSize: '0.9rem' }}>Nenhum documento na fila.</p>}
      </div>

      {/* Workspace Spilt View - 80% Width (65/35 inside) */}
      {selectedDoc ? (
        <div style={{ width: '80%', display: 'flex', backgroundColor: '#fff' }}>
          
          {/* Left Panel: PDF Viewer (65%) */}
          <div style={{ width: '65%', borderRight: '1px solid #e0e0e0', position: 'relative', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '1rem 1.5rem', backgroundColor: '#f0f0f0', borderBottom: '1px solid #ddd' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#333' }}>Visão de Documento</h3>
              <p style={{ margin: '0.5rem 0 0 0', color: '#d32f2f', fontSize: '0.9rem', fontWeight: 600 }}>Motivo da Quarentena: {selectedDoc.reason}</p>
            </div>
            <div style={{ flexGrow: 1, backgroundColor: '#525659' }}>
               <object 
                  data={`/api/v3/files/${selectedDoc.file_hash}`} 
                  type="application/pdf" 
                  width="100%" 
                  height="100%"
                >
                    <p style={{ color: 'white', padding: '2rem' }}>PDF render não suportado no seu navegador. <a href={`/api/v3/files/${selectedDoc.file_hash}`} style={{ color: '#4da6ff' }}>Baixar PDF</a></p>
                </object>
            </div>
          </div>
          
          {/* Right Panel: Correction Form (35%) */}
          <div style={{ width: '35%', padding: '2rem', display: 'flex', flexDirection: 'column' }}>
             <h3 style={{ borderBottom: '2px solid #0056b3', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Extração e Correção</h3>
             
             <div style={{ flexGrow: 1 }}>
               <label style={{ fontWeight: 600, fontSize: '0.9rem', color: '#555' }}>Dados Extraídos (JSON Editável)</label>
               <textarea 
                  rows={20} 
                  style={{ 
                    width: '100%', 
                    marginTop: '0.5rem', 
                    padding: '1rem', 
                    fontFamily: 'monospace', 
                    fontSize: '0.9rem',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    lineHeight: '1.5',
                    resize: 'none'
                  }} 
                  placeholder='Ex: { "total_amount": 120.00, "currency": "CHF" }'
                  value={Object.keys(correctionData).length > 0 ? JSON.stringify(correctionData, null, 2) : ''}
                  onChange={(e) => {
                    try {
                      if (e.target.value.trim() !== "") {
                        setCorrectionData(JSON.parse(e.target.value));
                      } else {
                        setCorrectionData({});
                      }
                    } catch {}
                  }}
               />
               <p style={{ fontSize: '0.8rem', color: '#888', marginTop: '0.5rem' }}>Edite o JSON acima com os campos corretos para forçar a resubmissão.</p>
             </div>
             
             <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
               <button 
                  onClick={() => handleAction('reinject')}
                  style={{ 
                    padding: '1rem', 
                    backgroundColor: '#0056b3', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px', 
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#004494'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#0056b3'}
               >
                 [ ✔ CORRIGIR E REINJETAR ]
               </button>

               <button 
                  onClick={() => handleAction('reject')}
                  style={{ 
                    padding: '1rem', 
                    backgroundColor: 'transparent', 
                    color: '#d32f2f', 
                    border: '1px solid #d32f2f', 
                    borderRadius: '4px', 
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#ffebee'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
               >
                 [ ✖ REJEITAR DOCUMENTO ]
               </button>
             </div>
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0f2f5' }}>
          <img src="https://via.placeholder.com/150/f0f2f5/a0a0a0?text=+" alt="Select" style={{ opacity: 0.5, marginBottom: '1rem' }} />
          <h3 style={{ color: '#555' }}>Nenhum documento selecionado</h3>
          <p style={{ color: '#888' }}>Selecione um documento na barra lateral para iniciar a revisão.</p>
        </div>
      )}
    </div>
  );
};

export default QuarantineInbox;
