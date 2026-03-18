import asyncio
import os
import wave
import struct
from dotenv import load_dotenv
load_dotenv()
from PIL import Image, ImageDraw

def create_dummy_images():
    img = Image.new('RGB', (500, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((20,90), "Recibo Odontologico Dr. Rafael - R$ 900", fill=(0,0,0))
    img.save('dummy_odontologico.jpg')
    print("[Mock] Created dummy_odontologico.jpg")

def create_dummy_audio():
    with wave.open('dummy_voice.wav', 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        # write 1 second of silence
        for i in range(8000):
            f.writeframesraw(struct.pack('<h', 0))
    print("[Mock] Created dummy_voice.wav")

from src.v3.skills.menir_capture import MenirCapture
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.menir_intel import MenirIntel
from src.v3.core.schemas.identity import locked_tenant_context

class MockBot:
    async def send_message(self, chat_id, text, reply_to_message_id=None):
        print(f"\n[Telegram MOCK -> Chat {chat_id}] {text}")

bot = MockBot()
intel = MenirIntel()
orch = NodePersistenceOrchestrator()

async def simulate_scenario(scenario_name: str, text: str, media_path: str = None):
    tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
    chat_id = 999
    
    print(f"\n{'='*60}\n🧪 CENÁRIO: {scenario_name}")
    print(f"📱 Webhook Payload -> Texto: '{text}' | Media: {media_path}")
    
    with locked_tenant_context(tenant_name):
        try:
            capture = MenirCapture(intel, orch)
            res = await capture.ingest(text=text, current_tenant=tenant_name, media_path=media_path)
            
            if res and res.get("success"):
                if res.get("hitl"):
                    target = res['hitl']['target_name']
                    print(f"⚠️  HITL Detectado! Telegram renderizaria InlineKeyboardMarkup para desambiguar '{target}'.")
                else:
                    await bot.send_message(chat_id, "✅ Entendido. Memória salva no grafo com sucesso.")
            else:
                await bot.send_message(chat_id, "❌ Não compreendi as informações (possível bloqueio cognitivo/LGPD).")
        except Exception as e:
            print(f"❌ Erro fatal no pipeline: {e}")

async def main():
    create_dummy_images()
    create_dummy_audio()
    
    print("\n🚀 INICIANDO BATERIA DE REGRESSÃO (S2/S3)")
    await asyncio.sleep(1)
    
    # 1. TEXT PLAIN
    await simulate_scenario("Texto Simples", "Hoje comprei um teclado mecânico novo modelo Keychron K2 por 500 reais.")
    
    # 2. IMAGE UPLOAD
    await simulate_scenario("Foto de Documento", "Guarda esse recibo do dentista por favor", "dummy_odontologico.jpg")
    
    # 3. AUDIO RECORDING (VOICE NOTE)
    await simulate_scenario("Voice Note (audio/wav simulando ogg)", "Extraia as notas desta reunião.", "dummy_voice.wav")
    
    # 4. CROSS-TENANT RESOLUTION
    await simulate_scenario("Cross-Tenant Reference", "Fala que a Nicole do trabalho precisa revisar os dados de S3.")
    
    print("\n✅ Bateria de simulação concluída.")

if __name__ == "__main__":
    asyncio.run(main())
