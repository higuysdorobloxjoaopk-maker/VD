import os

import sys

import subprocess

import secrets

import zipfile

from urllib.parse import urljoin, urlparse

import time

import random

# --- SISTEMA DE CORES GLOBAIS ---

C_PURPLE = "\033[95m"

C_CYAN   = "\033[96m"

C_GREEN  = "\033[92m"

C_RED    = "\033[91m"

C_YELLOW = "\033[93m"

C_WHITE  = "\033[97m"

C_BOLD   = "\033[1m"

C_END    = "\033[0m"

# --- AUTO-INSTALADOR DE DEPENDÊNCIAS ---

def setup_environment():

    libs = ['requests', 'beautifulsoup4', 'colorama', 'urllib3']

    for lib in libs:

        try:

            __import__(lib if lib != 'beautifulsoup4' else 'bs4')

        except ImportError:

            print(f"{C_YELLOW}[!] Instalando {lib}...{C_END}")

            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

setup_environment()

import requests

from bs4 import BeautifulSoup

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- MELHOR CONFIGURAÇÃO DE CAMINHO (DOWNLOADS) ---

def get_save_path(filename):

    candidates = [

        os.path.expanduser("\~/storage/downloads"),       # Oficial Termux (melhor)

        "/storage/emulated/0/Download",                  # Caminho direto Android moderno

        "/sdcard/Download",                              # Legacy

        os.path.expanduser("\~/storage/shared/Download"),

    ]

    for path in candidates:

        if os.path.exists(path) and os.access(path, os.W_OK):

            full = os.path.join(path, filename)

            print(f"{C_GREEN}[+] Caminho ideal encontrado: {full}{C_END}")

            return full

    # Fallback

    fallback = os.path.join(os.getcwd(), filename)

    print(f"{C_YELLOW}[!] Nenhuma pasta Downloads acessível.{C_END}")

    print(f"{C_YELLOW}[!] Salvando no diretório atual: {fallback}{C_END}")

    print(f"{C_YELLOW}[i] Para mover depois:  mv {filename} \~/storage/downloads/  ou  cp {filename} /storage/emulated/0/Download/{C_END}")

    return fallback

# --- VISUAL ---

ASCII_ART = f"""

{C_PURPLE}{C_BOLD}

 ██▒   █▓▓█████▄  ███▄ ▄███▓ ██▓ ██▀███   ██▀███   ▒█████   ██▀███  

▓██░   █▒▒██▀ ██▌▓██▒▀█▀ ██▒▓██▒▓██ ▒ ██▒▓██ ▒ ██▒▒██▒  ██▒▓██ ▒ ██▒

 ▓██  █▒░░██   █▌▓██    ▓██░▒██▒▓██ ░▄█ ▒▓██ ░▄█ ▒▒██░  ██▒▓██ ░▄█ ▒

  ▒██ █░░░▓█▄   ▌▒██    ▒██ ░██░▒██▀▀█▄  ▒██▀▀█▄  ▒██   ██░▒██▀▀█▄  

   ▒▀█░  ░▒████▓ ▒██▒   ░██▒░██░░██▓ ▒██▒░██▓ ▒██▒░ ████▓▒░░██▓ ▒██▒

{C_CYAN}         >> MIRRORING PROTOCOL v3.2 | ETERNAL ENHANCED <<

{C_WHITE}         >> STATUS: RECON ATIVO | ANDROID 14/15 READY <<

"""

class VDMirror:

    def __init__(self, url, mode):

        self.url = url if url.startswith(('http://', 'https://')) else 'https://' + url

        self.mode = mode.lower()

        self.domain = f"{urlparse(self.url).scheme}://{urlparse(self.url).netloc}"

        self.token = secrets.token_hex(4).upper()

        self.site_name = urlparse(self.url).netloc.replace('.', '_').replace('-', '_')

        

        self.raw_filename = f"{self.site_name}_{self.token}.zip"

        self.final_path = get_save_path(self.raw_filename)

        

        self.session = requests.Session()

        user_agents = [

            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

            'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',

            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'

        ]

        self.session.headers.update({'User-Agent': random.choice(user_agents)})

    def show_progress(self, current, total, success_count):

        width = 40

        percent = int((current / total) * 100) if total > 0 else 0

        filled = int(width * current / total) if total > 0 else 0

        bar = f"{C_PURPLE}█{C_END}" * filled + f"{C_CYAN}░{C_END}" * (width - filled)

        sys.stdout.write(f"\r{C_BOLD}[{bar}] {C_WHITE}{percent}%  ({success_count} ok / {current} tentados){C_END}")

        sys.stdout.flush()

    def run(self):

        print(f"\n{C_CYAN}[#] ALVO → {C_WHITE}{self.url}")

        try:

            response = self.session.get(self.url, timeout=12, verify=False)

            response.raise_for_status()

        except Exception as e:

            print(f"{C_RED}[!] FALHA NA CONEXÃO: {e}{C_END}")

            return

        soup = BeautifulSoup(response.text, 'html.parser')

        

        tags = {

            'link': 'href',

            'script': 'src',

        }

        if self.mode == 'n':

            tags.update({

                'img': 'src',

                'source': 'src',

                'video': 'src',

                'audio': 'src',

                'iframe': 'src',

            })

        assets_urls = set()

        for tag, attr in tags.items():

            for item in soup.find_all(tag):

                path = item.get(attr)

                if path and not path.startswith(('data:', '#', 'about:', 'javascript:')):

                    full_url = urljoin(self.url, path)

                    if urlparse(full_url).netloc == urlparse(self.url).netloc:  # mesmo domínio

                        assets_urls.add(full_url)

        total_assets = len(assets_urls)

        print(f"{C_GREEN}[+] {total_assets} assets detectados. Iniciando espelhamento...{C_END}")

        print(f"{C_CYAN}[i] Salvando ZIP em → {C_YELLOW}{self.final_path}{C_END}\n")

        success_count = 0

        try:

            with zipfile.ZipFile(self.final_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:

                zipf.writestr("index.html", response.text)

                

                for i, asset_url in enumerate(assets_urls, 1):

                    try:

                        asset_resp = self.session.get(asset_url, timeout=10, verify=False)

                        asset_resp.raise_for_status()

                        data = asset_resp.content

                        parsed = urlparse(asset_url)

                        filename = os.path.basename(parsed.path)

                        if not filename:

                            filename = f"asset_{i:03d}"

                        ext = os.path.splitext(filename)[1].lower()

                        folder = "assets"

                        if ext in ('.css',): folder = "css"

                        elif ext in ('.js',): folder = "js"

                        elif ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'): folder = "img"

                        elif ext in ('.woff', '.woff2', '.ttf', '.eot'): folder = "fonts"

                        elif ext in ('.mp4', '.webm', '.ogg'): folder = "media"

                        zip_path = f"{folder}/{filename}"

                        zipf.writestr(zip_path, data)

                        success_count += 1

                    except Exception:

                        pass  # ignora falhas silenciosamente (muitos assets quebrados)

                    self.show_progress(i, total_assets, success_count)

                    time.sleep(0.08)  # evita flood

            print(f"\n\n{C_GREEN}{C_BOLD}[✓] ESPELHAMENTO FINALIZADO!{C_END}")

            print(f"   → Arquivo: {C_WHITE}{self.raw_filename}{C_END}")

            print(f"   → Local:   {C_YELLOW}{self.final_path}{C_END}")

            print(f"   → Assets baixados: {C_GREEN}{success_count}/{total_assets}{C_END}")

            if success_count < total_assets:

                print(f"{C_YELLOW}[i] Alguns assets falharam (normal em sites modernos).{C_END}")

        except PermissionError:

            print(f"\n{C_RED}[!] PERMISSÃO NEGADA em {self.final_path}{C_END}")

            print(f"{C_YELLOW}Execute no Termux:{C_END}")

            print(f"   termux-setup-storage   → permita tudo no pop-up")

            print(f"   Depois rode o script novamente.")

        except Exception as e:

            print(f"{C_RED}[!] ERRO AO CRIAR ZIP: {e}{C_END}")

def main():

    os.system('clear' if os.name == 'posix' else 'cls')

    print(ASCII_ART)

    

    print(f"{C_YELLOW}[i] Dica: Rode 'termux-setup-storage' antes se Downloads não aparecer!{C_END}\n")

    

    target = input(f"{C_CYAN}ALVO (URL): {C_WHITE}").strip()

    if not target:

        print(f"{C_RED}[!] URL vazia. Abortando.{C_END}")

        return

    print(f"\n{C_PURPLE}MODOS:{C_END}")

    print(f"  {C_CYAN}F {C_WHITE}- Flash (só HTML + CSS/JS)")

    print(f"  {C_CYAN}N {C_WHITE}- Completo (tudo, incluindo imagens/vídeos)")

    mode = input(f"{C_CYAN}Modo [f/n]: {C_WHITE}").lower().strip()

    print(f"\n{C_RED}{C_BOLD}CONFIRMA QUE CONCORDA COM OS TERMOS?{C_END}")

    confirm = input(f"{C_CYAN} [s/n]: {C_WHITE}").lower().strip()

    if confirm in ('s', 'y', 'sim', 'yes'):

        VDMirror(target, mode).run()

    else:

        print(f"{C_RED}[!] Operação cancelada.{C_END}")

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(f"\n{C_RED}[!] Interrompido pelo usuário.{C_END}")

    except Exception as e:

        print(f"{C_RED}[ERRO FATAL] {e}{C_END}")