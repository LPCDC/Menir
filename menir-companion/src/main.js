let statusEl;
let countEl;

function connectSSE() {
  const token = "BECO_ENTERPRISE_JWT"; // Mock token for MVP proof of life
  const url = "http://localhost:8080/api/v3/events/companion";
  
  // Note: EventSource doesn't support headers natively. 
  // For MVP, we pass token via query param or rely on a simpler auth for dev.
  // Or we use a polyfill/fetch. For "prova de vida apenas", let's use a simpler connection.
  
  const eventSource = new EventSource(`${url}?token=${token}`);

  eventSource.onopen = () => {
    statusEl.textContent = "Conectado ao Menir (BECO)";
  };

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === "quarantine_update") {
      countEl.textContent = `${data.pending_count} itens aguardam revisão`;
    }
  };

  eventSource.onerror = (err) => {
    statusEl.textContent = "Erro na conexão SSE. Tentando reconectar...";
    console.error("SSE Error:", err);
  };
}

window.addEventListener("DOMContentLoaded", () => {
  statusEl = document.querySelector("#status-display");
  countEl = document.querySelector("#quarantine-count");
  connectSSE();
});
