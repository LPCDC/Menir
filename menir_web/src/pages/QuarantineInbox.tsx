import React, { useEffect, useState } from 'react';

interface QuarantineDocument {
  uid: string;
  name: string;
  file_hash: string;
  document_type: string;
  suggested_client: string;
  confidence: number;
  language: string;
  quarantined_at: string;
  reason: string;
}

const QuarantineInbox: React.FC = () => {
  const [documents, setDocuments] = useState<QuarantineDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<QuarantineDocument | null>(null);
  const [loading, setLoading] = useState(false);
  const [correctedClient, setCorrectedClient] = useState("");
  const [isCorrecting, setIsCorrecting] = useState(false);

  const fetchQuarantine = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("menir_session_token");
      const resp = await fetch('/api/v3/quarantine/documents', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (resp.ok) {
        const data = await resp.json();
        setDocuments(data || []);
      }
    } catch (e) {
      console.error("Failed to fetch quarantine:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuarantine();
  }, []);

  const handleAccept = async () => {
    if (!selectedDoc) return;
    try {
      const token = localStorage.getItem("menir_session_token");
      const resp = await fetch(`/api/v3/quarantine/documents/${selectedDoc.uid}/accept`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (resp.ok) {
        alert("Documento aceito com sucesso!");
        setSelectedDoc(null);
        fetchQuarantine();
      }
    } catch (e) {
      console.error(e);
      alert("Erro ao aceitar documento.");
    }
  };

  const handleCorrect = async () => {
    if (!selectedDoc || !correctedClient) return;
    try {
      const token = localStorage.getItem("menir_session_token");
      const resp = await fetch(`/api/v3/quarantine/documents/${selectedDoc.uid}/correct`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ client_name: correctedClient })
      });
      if (resp.ok) {
        alert("Documento corrigido e aceito!");
        setSelectedDoc(null);
        setIsCorrecting(false);
        fetchQuarantine();
      }
    } catch (e) {
      console.error(e);
      alert("Erro ao corrigir documento.");
    }
  };

  return (
    <div className="quarantine-container" style={{
      display: 'flex',
      height: 'calc(100vh - 64px)',
      width: '100%',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      color: '#e2e2e2',
      fontFamily: "'Inter', sans-serif",
      overflow: 'hidden'
    }}>
      {/* Sidebar - Glassmorphism */}
      <div className="sidebar" style={{
        width: '300px',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px'
      }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: '#ff4d4d' }}>●</span> Quarentena
          <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '10px' }}>{documents.length}</span>
        </h2>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {documents.map(doc => (
            <div 
              key={doc.uid}
              onClick={() => {
                setSelectedDoc(doc);
                setCorrectedClient(doc.suggested_client);
                setIsCorrecting(false);
              }}
              style={{
                padding: '15px',
                borderRadius: '12px',
                background: selectedDoc?.uid === doc.uid ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: selectedDoc?.uid === doc.uid ? '1px solid rgba(255, 255, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                transform: selectedDoc?.uid === doc.uid ? 'scale(1.02)' : 'scale(1)'
              }}
            >
              <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '5px', color: '#fff' }}>{doc.name}</div>
              <div style={{ fontSize: '0.75rem', color: '#aaa', display: 'flex', justifyContent: 'space-between' }}>
                <span>{doc.document_type}</span>
                <span style={{ color: doc.confidence < 0.5 ? '#ff4d4d' : '#ffaa00' }}>{(doc.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
          {!loading && documents.length === 0 && <div style={{ textAlign: 'center', color: '#888', marginTop: '40px' }}>Nenhum item pendente</div>}
          {loading && <div style={{ textAlign: 'center', color: '#888', marginTop: '40px' }}>Carregando...</div>}
        </div>
      </div>

      {/* Main Content */}
      <div className="content" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        {selectedDoc ? (
          <div style={{ display: 'flex', height: '100%' }}>
            {/* PDF View */}
            <div style={{ flex: 1, background: '#2e2e2e', borderRight: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <object 
                data={`/api/v3/files/${selectedDoc.file_hash}`} 
                type="application/pdf" 
                width="100%" 
                height="100%"
              >
                <div style={{ padding: '40px', textAlign: 'center' }}>
                  <p>Visualização indisponível.</p>
                  <a href={`/api/v3/files/${selectedDoc.file_hash}`} target="_blank" style={{ color: '#4da6ff' }}>Abrir em nova aba</a>
                </div>
              </object>
            </div>

            {/* Actions Panel */}
            <div style={{ width: '350px', padding: '30px', background: 'rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '10px', color: '#fff' }}>Detalhes da Captura</h3>
              
              <div className="detail-item">
                <label style={{ fontSize: '0.8rem', color: '#888' }}>Cliente Sugerido</label>
                <div style={{ fontSize: '1.2rem', fontWeight: 500, color: '#4da6ff' }}>{selectedDoc.suggested_client}</div>
              </div>

              <div className="detail-item">
                <label style={{ fontSize: '0.8rem', color: '#888' }}>Tipo de Documento</label>
                <div>{selectedDoc.document_type}</div>
              </div>

              <div className="detail-item">
                <label style={{ fontSize: '0.8rem', color: '#888' }}>Idioma Detectado</label>
                <div style={{ textTransform: 'uppercase' }}>{selectedDoc.language}</div>
              </div>

              <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {!isCorrecting ? (
                  <>
                    <button 
                      onClick={handleAccept}
                      style={{
                        padding: '14px',
                        background: 'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '8px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        transition: 'opacity 0.2s'
                      }}
                    >
                      ACEITAR E PROSSEGUIR
                    </button>
                    <button 
                      onClick={() => setIsCorrecting(true)}
                      style={{
                        padding: '14px',
                        background: 'rgba(255,255,255,0.05)',
                        color: '#fff',
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '8px',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      CORRIGIR CLIENTE...
                    </button>
                  </>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', background: 'rgba(255,255,255,0.05)', padding: '20px', borderRadius: '12px' }}>
                    <label style={{ fontSize: '0.85rem' }}>Nome Correto do Cliente:</label>
                    <input 
                      autoFocus
                      type="text" 
                      value={correctedClient} 
                      onChange={(e) => setCorrectedClient(e.target.value)}
                      style={{
                        padding: '10px',
                        background: '#1a1a2e',
                        border: '1px solid #4facfe',
                        borderRadius: '4px',
                        color: '#fff',
                        outline: 'none'
                      }}
                    />
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button 
                         onClick={handleCorrect}
                         style={{ flex: 1, padding: '10px', background: '#4facfe', border: 'none', borderRadius: '4px', color: '#fff', fontWeight: 600, cursor: 'pointer' }}
                      >
                        SALVAR
                      </button>
                      <button 
                         onClick={() => setIsCorrecting(false)}
                         style={{ flex: 1, padding: '10px', background: 'transparent', border: '1px solid #888', borderRadius: '4px', color: '#888', cursor: 'pointer' }}
                      >
                        CANCELAR
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ fontSize: '4rem', opacity: 0.2 }}>📁</div>
            <div style={{ color: '#888', marginTop: '20px' }}>Selecione um documento para revisar</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuarantineInbox;
