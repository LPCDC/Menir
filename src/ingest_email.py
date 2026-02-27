import mailbox
import os
import email.utils
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Carrega ambiente
load_dotenv()

# Configurações
MBOX_DIR = "data/inbox/emails"
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-neo4j:7687") # Ajuste para rodar dentro do container
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

print(f" Iniciando MenirMailParser...")
print(f"Target DB: {NEO4J_URI}")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def clean_text(text):
    if text:
        return text.replace('"', "'").replace('\\', '').strip()[:1000] # Limita tamanho pra não explodir
    return ""

def ingest_mbox(file_path):
    print(f" Lendo arquivo: {file_path}")
    mbox = mailbox.mbox(file_path)
    
    query = """
    MERGE (p:Person {email: $sender_email})
    ON CREATE SET p.name = $sender_name
    
    CREATE (m:Message {
        id: $msg_id,
        subject: $subject,
        date: $date,
        snippet: $snippet,
        source: 'email'
    })
    
    MERGE (p)-[:SENT]->(m)
    
    FOREACH (rec IN $recipients | 
        MERGE (r:Person {email: rec.email})
        ON CREATE SET r.name = rec.name
        MERGE (m)-[:TO]->(r)
    )
    """
    
    count = 0
    batch_data = []
    
    with driver.session() as session:
        for message in mbox:
            try:
                # Extração Segura
                msg_id = message['Message-ID'] or str(datetime.now().timestamp())
                subject = clean_text(message['subject'])
                
                # Data Parser
                date_str = message['date']
                try:
                    parsed_date = email.utils.parsedate_to_datetime(date_str)
                    final_date = parsed_date.isoformat()
                except:
                    final_date = datetime.now().isoformat()

                # Remetente
                from_header = message['from'] or "Unknown <unknown@void>"
                real_name, sender_email = email.utils.parseaddr(from_header)
                
                # Destinatários
                to_header = message['to'] or ""
                recipients = []
                if to_header:
                    for addr in to_header.split(','):
                        r_name, r_email = email.utils.parseaddr(addr)
                        if r_email:
                            recipients.append({'name': r_name, 'email': r_email})

                # Corpo (Simples)
                body_snip = ""
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain":
                            body_snip = clean_text(str(part.get_payload(decode=True)))
                            break
                else:
                    body_snip = clean_text(str(message.get_payload(decode=True)))

                # Executa
                session.run(query, 
                    sender_email=sender_email, 
                    sender_name=real_name,
                    msg_id=msg_id,
                    subject=subject,
                    date=final_date,
                    snippet=body_snip[:500],
                    recipients=recipients
                )
                
                count += 1
                if count % 100 == 0:
                    print(f" Processados: {count} emails...")

            except Exception as e:
                print(f" Erro ao ler email: {e}")
                continue

    print(f" Finalizado! Total de emails importados: {count}")

# Execução
if __name__ == "__main__":
    # Procura arquivos .mbox na pasta
    if not os.path.exists(MBOX_DIR):
        print(f" Pasta {MBOX_DIR} não encontrada.")
    else:
        files = [f for f in os.listdir(MBOX_DIR) if f.endswith('.mbox')]
        if not files:
            print(" Nenhum arquivo .mbox encontrado na Inbox.")
        for f in files:
            ingest_mbox(os.path.join(MBOX_DIR, f))
    
    driver.close()
