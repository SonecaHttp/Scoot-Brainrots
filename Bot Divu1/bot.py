import os
import aiohttp
import asyncio
from random import shuffle, choice
import time

# CONFIGURAÇÕES:
MENSAGEM_FIXA = """🌟 Troco Passo **Primeiro** Posso Ir No Seu **Servidor** Se Precisar 🌟"""
IMAGEM_LOCAL = "C:/Users/kalin/Downloads/Bot Divu1/scoot.png"
INTERVALO_SEGUNDOS = 76
PROXY_LIST = [
    "http://38.156.73.154:80",  
    "http://39.102.213.3:3129",
    # Adicione mais proxies aqui
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print("\033[92m[✓] Soneca Spammer Automático (multi-canais com upload de imagens)\033[0m\n")

async def check_proxy(proxy):
    """Verifica se o proxy está funcionando."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org", proxy=proxy, timeout=5) as response:
                if response.status == 200:
                    return True
                return False
    except Exception:
        return False

async def send_message(session, url, token, proxy=None):
    try:
        headers = {
            "authorization": token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
        }

        if not os.path.exists(IMAGEM_LOCAL):
            print(f"\033[91m[ERRO] Arquivo de imagem '{IMAGEM_LOCAL}' não encontrado.\033[0m")
            return

        with open(IMAGEM_LOCAL, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("content", MENSAGEM_FIXA)
            form.add_field("files[0]", f,
                           filename=os.path.basename(IMAGEM_LOCAL),
                           content_type="image/png")

            async with session.post(url, data=form, headers=headers, proxy=proxy) as response:
                if response.status in (200, 204):
                    print(f"\033[92m[✔] Mensagem + imagem enviada: {token[:25]}... (Proxy: {proxy})\033[0m")
                else:
                    text = await response.text()
                    print(f"\033[91m[✖] Erro: {token[:25]}... | Status: {response.status} | {text} (Proxy: {proxy})\033[0m")

    except Exception as e:
        print(f"\033[91m[!] Falha com token {token[:25]}... | Erro: {e} (Proxy: {proxy})\033[0m")

async def spam_loop():
    try:
        with open('tokens.txt', 'r') as file:
            tokens = [t.strip() for t in file if t.strip()]
    except FileNotFoundError:
        print("\033[91m[ERRO] Arquivo 'tokens.txt' não encontrado.\033[0m")
        return
    if not tokens:
        print("\033[91m[ERRO] Nenhum token encontrado no arquivo.\033[0m")
        return

    try:
        with open('canais.txt', 'r') as file:
            canais = [c.strip() for c in file if c.strip()]
    except FileNotFoundError:
        print("\033[91m[ERRO] Arquivo 'canais.txt' não encontrado.\033[0m")
        return
    if not canais:
        print("\033[91m[ERRO] Nenhum ID de canal encontrado no arquivo.\033[0m")
        return

    # Verificar proxies válidos
    valid_proxies = []
    for proxy in PROXY_LIST:
        if await check_proxy(proxy):
            valid_proxies.append(proxy)
            print(f"\033[92m[✔] Proxy válido: {proxy}\033[0m")
        else:
            print(f"\033[91m[✖] Proxy inválido: {proxy}\033[0m")

    if not valid_proxies:
        print("\033[91m[ERRO] Nenhum proxy válido encontrado. Continuando sem proxy...\033[0m")
        valid_proxies = [None]  # Fallback para sem proxy

    async with aiohttp.ClientSession() as session:
        while True:
            for canal_id in canais:
                print(f"\n\033[94m[>] Enviando mensagem para o canal {canal_id}...\033[0m")
                url = f"https://discord.com/api/v9/channels/{canal_id}/messages"
                shuffle(tokens)
                tasks = [send_message(session, url, token, proxy=choice(valid_proxies)) for token in tokens]
                await asyncio.gather(*tasks)
            print(f"\n\033[93m[*] Aguardando {INTERVALO_SEGUNDOS} segundos...\033[0m")
            await asyncio.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    try:
        print_banner()
        asyncio.run(spam_loop())
    except KeyboardInterrupt:

        print("\n\033[91m[!] Interrompido pelo usuário.\033[0m")
