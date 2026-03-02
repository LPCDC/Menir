"""
Menir Core V5.1 - Administrative CLI (Root Access)
Connects strictly via 127.0.0.1:8081 TCP Socket to the MenirSynapse.
Acts as the Priority 0 Command Origin with "Fat Finger" guardrails
to protect the database from sleepy Admins.
"""
import sys
import asyncio
import argparse

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 8081

# Comandos Sensíveis que exigem Y/N do Admin
DESTRUCTIVE_COMMANDS = ['reload', 'flush', 'apagar', 'recarregar', 'reload_rules', 'flush_quarantine']

async def send_to_socket(intent: str):
    """Abre conexão TCP, envia a String e recebe a Resposta da Synapse."""
    try:
        reader, writer = await asyncio.open_connection(SOCKET_HOST, SOCKET_PORT)
        
        # Ignora o banner inicial de boas vindas "Menir V5.1 Root CLI..."
        await reader.readline()
        
        # Envia a Intenção
        writer.write((intent + '\n').encode('utf-8'))
        await writer.drain()
        
        # Lê todas as linhas de resposta até o final da transmissão de bloco
        response = ""
        while True:
            try:
                # Usa um timeout curto para quando a synapse não fecha 
                # a conexão, mas já enviou o ACK
                line = await asyncio.wait_for(reader.readline(), timeout=1.5)
                if not line:
                    break
                response += line.decode('utf-8')
            except asyncio.TimeoutError:
                break
                
        writer.close()
        await writer.wait_closed()
        
        print(response)
        
    except ConnectionRefusedError:
        print(f"❌ SERVIDOR OFFLINE. Falha de Conexão com a Synapse em {SOCKET_HOST}:{SOCKET_PORT}.")
        print("Certifique-se que o MenirAsyncRunner está online.")
    except Exception as e:
        print(f"❌ ERRO CRÍTICO NO SOCKET: {e}")

def detect_fat_finger(intent: str) -> bool:
    """Retorna True se o usuário deve confirmar."""
    intent_lower = intent.lower()
    return any(cmd in intent_lower for cmd in DESTRUCTIVE_COMMANDS)

def main():
    parser = argparse.ArgumentParser(description="Menir V5.1 Root CLI (Synapse Interface)")
    
    # Comandos Rápidos Mapeados (Shortcuts que evitam processamento NLP ambíguo)
    subparsers = parser.add_subparsers(dest="command", help="Root Commands")
    
    # menir status
    subparsers.add_parser("status", help="Retorna a saúde dos Workers e Concorrência")
    
    # menir pause "motivo"
    pause_parser = subparsers.add_parser("pause", help="Trava a Ingestão Imediatamente")
    pause_parser.add_argument("reason", type=str, nargs='?', default="Emergency Pause CLI", help="Motivo da pausa (salvo na proveniência)")
    
    # menir resume
    subparsers.add_parser("resume", help="Reinicia o Watchdog")
    
    # menir ask "texto livre"
    ask_parser = subparsers.add_parser("ask", help="Envia linguagem natural para o Córtex Logos")
    ask_parser.add_argument("intent", type=str, nargs='+', help="A intenção livre (ex: 'Me mostre o status atual')")

    args = parser.parse_args()

    intent_string = ""

    if args.command == "status":
        intent_string = "Retorne oSTATUS_REPORT do sistema imediatamente."
    elif args.command == "pause":
        intent_string = f"PAUSE_INGESTION. Motivo obrigatório: {args.reason}"
    elif args.command == "resume":
        intent_string = "RESUME_INGESTION"
    elif args.command == "ask":
        intent_string = " ".join(args.intent)
    else:
        parser.print_help()
        sys.exit(1)

    # GUARDRAIL - O Fat Finger Check
    if detect_fat_finger(intent_string):
        print("⚠️  ATENÇÃO: Este comando modificará o estado crítico do Grafo ou da Memória RAM (Neo4j/LRU).")
        print(f"Ordem detetada: '{intent_string}'")
        choice = input("Você tem certeza administrativa que deseja prosseguir? [y/N]: ")
        if choice.lower() not in ['y', 'yes', 'sim', 's']:
            print("🛑 Comando Abortado via Fat Finger Guardrail.")
            sys.exit(0)

    # ENCERRAMENTO
    print(f"🚀 Enviando comando via Socket Seguro para o MenirAsyncRunner (Priority 0)...")
    asyncio.run(send_to_socket(intent_string))


if __name__ == "__main__":
    main()
