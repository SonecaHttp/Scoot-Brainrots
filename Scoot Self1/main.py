import discord
import aiohttp
import asyncio
from datetime import datetime
import json

# CONFIGURAÇÕES
RESPOSTA_DM = """> - ```Slow Corporation ©```

> Opa Mano Então Você Tem Interesse Em Nossos *Brainrots*?
> ⚠️  Sim Isso Mesmo Que Você Viu Passamos **Primeiro** e Ainda No Seu **Sevidor ** ⚠️ 

🎉 Para Nois Começar a Troca Somente Entrar No Nosso Sevidor Do Discord e ir Em **Troca-Aqui** Estamos Espernado Você 🎉

🔗 :https://discord.gg/pxRcSFN9"""
WEBHOOK_URL = "https://discord.com/api/webhooks/1409012528188751913/6Vt4qVWBsSs-2mqIOysHbM8Xgo3YfpJUGD5HNQKgD79khrz2uoZAWRwtDEkjtPRyqzkD"
DM_RESPONSE_DELAY = 60 

def load_responded_users():
    try:
        with open('responded_users.json', 'r') as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_responded_users(responded_users):
    with open('responded_users.json', 'w') as file:
        json.dump(list(responded_users), file)

responded_users = load_responded_users()

class MySelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

    async def on_ready(self):
        print(f"\033[92m[✓] Self-bot conectado como {self.user.name}#{self.user.discriminator}\033[0m")

    async def send_webhook_embed(self, sender_name, sender_id, message_content, response_sent=False):
        embed = {
            "title": "Nova Mensagem no DM" if not response_sent else "Resposta Enviada no DM",
            "color": 0xFF0000 if not response_sent else 0x00FF00,  
            "fields": [
                {"name": "Usuário", "value": sender_name, "inline": True},
                {"name": "ID do Usuário", "value": str(sender_id), "inline": True},
                {"name": "Mensagem", "value": message_content[:1024], "inline": False}, 
                {"name": "Conta", "value": f"{self.user.name}#{self.user.discriminator}", "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Log de DMs"}
        }
        payload = {"embeds": [embed]}
        try:
            async with self.session.post(WEBHOOK_URL, json=payload) as response:
                if response.status in (200, 204):
                    print(f"\033[92m[✔] Webhook enviado para {'DM de' if not response_sent else 'resposta enviada para'} {sender_name}\033[0m")
                else:
                    print(f"\033[91m[✖] Erro ao enviar webhook: Status {response.status}\033[0m")
        except Exception as e:
            print(f"\033[91m[!] Falha ao enviar webhook: {e}\033[0m")

    async def send_dm_response(self, channel, sender_name, sender_id):
        try:
            await asyncio.sleep(DM_RESPONSE_DELAY)
            await channel.send(RESPOSTA_DM)
            print(f"\033[92m[✔] Resposta automática enviada para {sender_name} após {DM_RESPONSE_DELAY} segundos\033[0m")
            await self.send_webhook_embed(sender_name, sender_id, RESPOSTA_DM, response_sent=True)
        except Exception as e:
            print(f"\033[91m[!] Falha ao enviar resposta automática para {sender_name}: {e}\033[0m")

    async def on_message(self, message):
        if message.author == self.user or not isinstance(message.channel, discord.DMChannel):
            return

        sender_name = f"{message.author.name}#{message.author.discriminator}"
        sender_id = message.author.id
        content = message.content or "Mensagem sem texto (pode conter anexos)"

        await self.send_webhook_embed(sender_name, sender_id, content)

        if sender_id not in responded_users:
            responded_users.add(sender_id)
            save_responded_users(responded_users)
            asyncio.create_task(self.send_dm_response(message.channel, sender_name, sender_id))

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()

async def validate_token(token):
    """Valida o token antes de iniciar o self-bot."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}) as response:
            if response.status == 200:
                return True
            return False

async def main():
    try:
        with open('token.txt', 'r') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("\033[91m[ERRO] Arquivo 'token.txt' não encontrado. Crie um arquivo 'token.txt' com o token da conta.\033[0m")
        return
    if not token:
        print("\033[91m[ERRO] Nenhum token encontrado no arquivo 'token.txt'.\033[0m")
        return

    if not await validate_token(token):
        print(f"\033[91m[!] Token inválido: {token[:25]}... Verifique o token em 'token.txt' e certifique-se de que é um token de conta válido.\033[0m")
        return

    client = MySelfBot()
    try:
        await client.start(token)
    except discord.errors.LoginFailure:
        print(f"\033[91m[!] Token inválido: {token[:25]}... Verifique o token em 'token.txt' e certifique-se de que é um token de conta válido.\033[0m")
    except Exception as e:
        print(f"\033[91m[!] Erro ao iniciar o self-bot: {e}\033[0m")
    finally:
        if client.session and not client.session.closed:
            await client.session.close()

if __name__ == "__main__":
    try:
        print("\033[92m[✓] Iniciando Self-Bot de Resposta a DMs\033[0m\n")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[91m[!] Interrompido pelo usuário.\033[0m")
    except Exception as e:
        print(f"\033[91m[!] Erro inesperado: {e}\033[0m")