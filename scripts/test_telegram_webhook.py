import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from PIL import Image, ImageDraw, ImageFont

# 1. Create a dummy image for the Photo Test
img = Image.new('RGB', (500, 200), color=(255, 255, 255))
d = ImageDraw.Draw(img)
# Using default font
d.text((20,90), "Recibo Odontologico Dr. Rafael - R$ 900", fill=(0,0,0))
img.save('dummy_odontologico.jpg')

from src.v3.skills.menir_capture import MenirCapture
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.menir_intel import MenirIntel
from src.v3.core.schemas.identity import locked_tenant_context

class MockBot:
    async def send_message(self, chat_id, text, reply_to_message_id=None):
        print(f"\n[Telegram Bot -> Chat {chat_id}] {text}")

bot = MockBot()
intel = MenirIntel()
orch = NodePersistenceOrchestrator()

async def simulate_telegram_webhook(text: str, image_path: str = None):
    # Simulate extraction from update
    tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
    chat_id = 12345
    message_id = 999
    
    print(f"\n{'='*50}\n📱 Recebido no Webhook Telegram (Tenant={tenant_name})")
    print(f"Texto: '{text}' | Imagem anexada: {image_path is not None}")
    
    with locked_tenant_context(tenant_name):
        try:
            capture = MenirCapture(intel, orch)
            success = await capture.ingest(text=text, current_tenant=tenant_name, image_path=image_path)
            
            if success:
                await bot.send_message(chat_id, "✅ Entendido. Memória salva no grafo com sucesso.", message_id)
            else:
                await bot.send_message(chat_id, "❌ Não consegui compreender as informações desta mensagem para extrair uma memória.", message_id)
        except Exception as e:
            print(f"Erro no processamento background Telegram: {e}")
            await bot.send_message(chat_id, "❌ Ocorreu um problema técnico ao processar sua mensagem.", message_id)


async def main():
    # Scenario 1: Simple text
    await simulate_telegram_webhook("Hoje comprei um teclado mecânico novo.")
    await asyncio.sleep(2)
    
    # Scenario 2: Photo of a generic document
    await simulate_telegram_webhook("Salve esse recibo por favor", "dummy_odontologico.jpg")
    await asyncio.sleep(2)
    
    # Scenario 3: Mention entity from BECO cross-tenant (Using Nicole from BECO)
    await simulate_telegram_webhook("Mandei aquele relatório fechado para a Nicole.")
    await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
