import os
import aiohttp
import asyncio
from random import shuffle

# CONFIGURAÇÕES:
MENSAGEM_FIXA = """I trade Dragon Caneloni for 250M – I’ll go to your server and go first.
I trade Dragon Caneloni for 250M – I’ll go to your server and go first.
I trade Dragon Caneloni for 250M – I’ll go to your server and go first.
I trade Dragon Caneloni for 250M – I’ll go to your server and go first.
I trade Dragon Caneloni for 250M – I’ll go to your server and go first.
I trade Dragon Caneloni for 250M – I’ll go to your server and go first."""
INTERVALO_SEGUNDOS = 300

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print("\033[92m[✓] Soneca Spammer Automático (multi-canais, só mensagem)\033[0m\n")

async def send_message(session, url, token):
    try:
        headers = {
            "authorization": token,
            "content-type": "application/json"
        }

        payload = {
            "content": MENSAGEM_FIXA
        }

        async with session.post(url, json=payload, headers=headers) as response:
            if response.status in (200, 204):
                print(f"\033[92m[✔] Mensagem enviada: {token[:25]}...\033[0m")
            else:
                text = await response.text()
                print(f"\033[91m[✖] Erro: {token[:25]}... | Status: {response.status} | {text}\033[0m")

    except Exception as e:
        print(f"\033[91m[!] Falha com token {token[:25]}... | Erro: {e}\033[0m")

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

    async with aiohttp.ClientSession() as session:
        while True:
            for canal_id in canais:
                print(f"\n\033[94m[>] Enviando mensagem para o canal {canal_id}...\033[0m")
                url = f"https://discord.com/api/v9/channels/{canal_id}/messages"
                shuffle(tokens)
                tasks = [send_message(session, url, token) for token in tokens]
                await asyncio.gather(*tasks)
            print(f"\n\033[93m[*] Aguardando {INTERVALO_SEGUNDOS} segundos...\033[0m")
            await asyncio.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    try:
        print_banner()
        asyncio.run(spam_loop())
    except KeyboardInterrupt:
        print("\n\033[91m[!] Interrompido pelo usuário.\033[0m")
