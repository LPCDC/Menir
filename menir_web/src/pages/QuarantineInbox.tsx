import React, { useEffect, useState } from 'react';

interface QuarantineDocument {
  uid: string;
  name: string;
  file_hash: string;
  document_type: string;
  suggested_client: string;
  confidence: number;
  trust_score: number;
  routing_decision: string;
  language: string;
  quarantined_at: string;
  reason: string;
}

const QuarantineInbox: React.FC = () => {
  const [documents, setDocuments] = useState<QuarantineDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<QuarantineDocument | null>(null);
  const [filter, setFilter] = useState<string>("ALL"); // ALL, PRODUCTION, QUARANTINE
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

  const getScoreColor = (score: number) => {
    if (score >= 0.85) return '#4dff4d'; // Verde
    if (score >= 0.70) return '#ffaa00'; // Laranja
    return '#ff4d4d'; // Vermelho
  };

  const filteredDocuments = documents.filter(doc => {
    if (filter === "ALL") return true;
    return doc.routing_decision === filter;
  });

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
        width: '320px',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px'
      }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: '#ff4d4d' }}>●</span> Quarentena
          <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '10px' }}>{filteredDocuments.length}</span>
        </h2>

        {/* Filter Selection */}
        <div style={{ display: 'flex', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '4px', marginBottom: '15px' }}>
          {["ALL", "PRODUCTION", "QUARANTINE"].map(f => (
            <button 
              key={f}
              onClick={() => setFilter(f)}
              style={{
                flex: 1,
                padding: '6px',
                fontSize: '0.65rem',
                borderRadius: '6px',
                border: 'none',
                background: filter === f ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: filter === f ? '#fff' : '#888',
                cursor: 'pointer',
                fontWeight: filter === f ? 700 : 400
              }}
            >
              {f === "ALL" ? "TODOS" : f}
            </button>
          ))}
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredDocuments.map(doc => (
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
              <div style={{ fontSize: '0.75rem', color: '#aaa', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.document_type}</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                   <span title="Gemini Confidence" style={{ color: '#aaa' }}>{(doc.confidence * 100).toFixed(0)}%</span>
                   <span title="Menir Trust Score" style={{ color: getScoreColor(doc.trust_score || 0), fontWeight: 700 }}>
                     {( (doc.trust_score || 0) * 100).toFixed(0)}
                   </span>
                </div>
              </div>
            </div>
          ))}
          {!loading && filteredDocuments.length === 0 && <div style={{ textAlign: 'center', color: '#888', marginTop: '40px' }}>Nenhum item pendente</div>}
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
            <div style={{ width: '380px', padding: '30px', background: 'rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '10px', color: '#fff' }}>Detalhes da Captura</h3>
              
              <div className="detail-item">
                <label style={{ fontSize: '0.8rem', color: '#888' }}>Cliente Sugerido</label>
                <div style={{ fontSize: '1.2rem', fontWeight: 500, color: '#4da6ff' }}>{selectedDoc.suggested_client}</div>
              </div>

              <div style={{ display: 'flex', gap: '20px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '0.8rem', color: '#888' }}>Trust Score</label>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: getScoreColor(selectedDoc.trust_score || 0) }}>
                    {((selectedDoc.trust_score || 0) * 100).toFixed(0)}%
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '0.8rem', color: '#888' }}>Roteamento</label>
                  <div style={{ 
                    fontSize: '0.7rem', 
                    fontWeight: 700, 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    background: selectedDoc.routing_decision === 'PRODUCTION' ? 'rgba(77, 255, 77, 0.1)' : 'rgba(255, 77, 77, 0.1)',
                    color: selectedDoc.routing_decision === 'PRODUCTION' ? '#4dff4d' : '#ff4d4d',
                    display: 'inline-block',
                    marginTop: '5px'
                  }}>
                    {selectedDoc.routing_decision}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '20px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '0.8rem', color: '#888' }}>Tipo</label>
                  <div style={{ fontSize: '0.85rem' }}>{selectedDoc.document_type}</div>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '0.8rem', color: '#888' }}>Idioma</label>
                  <div style={{ textTransform: 'uppercase', fontSize: '0.85rem' }}>{selectedDoc.language}</div>
                </div>
              </div>

              <div className="detail-item">
                <label style={{ fontSize: '0.8rem', color: '#888' }}>Motivo da Quarentena</label>
                <div style={{ fontSize: '0.85rem', color: '#ffaa00' }}>{selectedDoc.reason}</div>
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
