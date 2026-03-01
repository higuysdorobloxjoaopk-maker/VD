# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import secrets
import zipfile
import re
from urllib.parse import urljoin, urlparse

# --- SISTEMA DE CORES GLOBAIS ---
C_PURPLE = "\033[95m"
C_CYAN   = "\033[96m"
C_GREEN  = "\033[92m"
C_RED    = "\033[91m"
C_YELLOW = "\033[93m"
C_WHITE  = "\033[97m"
C_BOLD   = "\033[1m"
C_END    = "\033[0m"

# --- CONFIGURAÇÃO UTF-8 E COLORAMA ---
import colorama
colorama.init(autoreset=True)
sys.stdout.reconfigure(encoding='utf-8')

# --- AUTO-INSTALADOR DE DEPENDÊNCIAS ---
def setup_enviroment():
    libs = ['requests', 'bs4', 'colorama', 'urllib3']
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"{C_YELLOW}[!] Instalando módulo crítico: {lib}...{C_END}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

setup_enviroment()

import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAÇÃO DE CAMINHO (DOWNLOADS) ---
def get_save_path(filename):
    termux_download = "/sdcard/Download"
    if os.path.exists(termux_download):
        return os.path.join(termux_download, filename)
    return filename

# --- VISUAL ---
ASCII_ART = f"""
{C_PURPLE}{C_BOLD}
 ██▒   █▓▓█████▄  ███▄ ▄███▓ ██▓ ██▀███   ██▀███   ▒█████   ██▀███  
▓██░   █▒▒██▀ ██▌▓██▒▀█▀ ██▒▓██▒▓██ ▒ ██▒▓██ ▒ ██▒▒██▒  ██▒▓██ ▒ ██▒
 ▓██  █▒░░██   █▌▓██    ▓██░▒██▒▓██ ░▄█ ▒▓██ ░▄█ ▒▒██░  ██▒▓██ ░▄█ ▒
  ▒██ █░░░▓█▄   ▌▒██    ▒██ ░██░▒██▀▀█▄  ▒██▀▀█▄  ▒██   ██░▒██▀▀█▄  
   ▒▀█░  ░▒████▓ ▒██▒   ░██▒░██░░██▓ ▒██▒░██▓ ▒██▒░ ████▓▒░░██▓ ▒██▒
{C_CYAN}         >> MIRRORING PROTOCOL v3.1 | ETERNAL EDITION <<
{C_WHITE}         >> STATUS: TERMINAL RECON ATIVO <<
"""

# --- CLASSE DE ESPELHAMENTO ---
class VDMirror:
    def __init__(self, url, mode):
        self.url = url if url.startswith('http') else 'https://' + url
        self.mode = mode
        self.domain = f"{urlparse(self.url).scheme}://{urlparse(self.url).netloc}"
        self.token = secrets.token_hex(3).upper()
        self.site_name = urlparse(self.url).netloc.replace('.', '_')
        self.raw_filename = f"{self.site_name}-{self.token}.zip"
        self.final_path = get_save_path(self.raw_filename)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def show_progress(self, current, total):
        width = 35
        percent = int((current / total) * 100) if total > 0 else 0
        filled = int(width * current / total) if total > 0 else 0
        bar = f"{C_PURPLE}█{C_END}" * filled + f"{C_CYAN}▒{C_END}" * (width - filled)
        sys.stdout.write(f"\r{C_BOLD}[{bar}] {C_WHITE}{percent}% {C_CYAN}({current}/{total})")
        sys.stdout.flush()

    def run(self):
        print(f"\n{C_CYAN}[#] CONECTANDO EM: {C_WHITE}{self.url}")
        try:
            response = self.session.get(self.url, timeout=15, verify=False)
            response.raise_for_status()
        except Exception as e:
            print(f"{C_RED}[!] ERRO DE CONEXÃO: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        tags = {'link':'href','script':'src'}
        if self.mode == 'n':
            tags.update({'img':'src','source':'src','video':'src'})

        assets_urls = []
        for tag, attr in tags.items():
            for item in soup.find_all(tag):
                path = item.get(attr)
                if path:
                    assets_urls.append(urljoin(self.url, path))

        assets_urls = list(set(assets_urls))
        total_assets = len(assets_urls)
        print(f"{C_GREEN}[+] PROTOCOLO INICIADO. SALVANDO EM DOWNLOADS...")

        try:
            with zipfile.ZipFile(self.final_path,'w',zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("index.html", response.text)
                for i, asset_url in enumerate(assets_urls):
                    try:
                        data = self.session.get(asset_url, timeout=8, verify=False).content
                        filename = os.path.basename(urlparse(asset_url).path) or f"resource_{i}"
                        ext = os.path.splitext(filename)[1].lower()
                        folder = "assets"
                        if ext=='.css': folder='css'
                        elif ext=='.js': folder='js'
                        elif ext in ['.jpg','.png','.svg','.webp','.ico']: folder='img'
                        zipf.writestr(f"{folder}/{filename}", data)
                    except:
                        continue
                    self.show_progress(i+1, total_assets)
            print(f"\n\n{C_GREEN}{C_BOLD}[✓] ESPELHAMENTO CONCLUÍDO!")
            print(f"{C_CYAN}[i] ARQUIVO: {C_WHITE}{self.raw_filename}")
            print(f"{C_CYAN}[i] DESTINO: {C_YELLOW}{self.final_path}{C_END}\n")
        except PermissionError:
            print(f"\n{C_RED}[!] ERRO: Sem permissão para escrever em /sdcard/Download.")
            print(f"{C_YELLOW}[!] Rode 'termux-setup-storage' e aceite a permissão.")

def main():
    os.system('clear')
    print(ASCII_ART)
    target = input(f"{C_CYAN}ALVO (URL): {C_WHITE}").strip()
    if not target: return
    print(f"\n{C_PURPLE}[MODOS DE OPERAÇÃO]{C_END}")
    print(f"{C_CYAN}F - FLASH (Rápido, apenas estrutura)")
    print(f"{C_CYAN}N - COMPLETO (Lento, baixa todas as mídias)")
    mode = input(f"{C_CYAN}ESCOLHA [f/n]: {C_WHITE}").lower().strip()
    print(f"\n{C_RED}{C_BOLD}VOCÊ SEJA ESPELHAR TODA A PARTE VIZUAL DO ALVO{C_END}")
    confirm = input(f"{C_CYAN}[y/n]: {C_WHITE}").lower().strip()
    if confirm=='y':
        VDMirror(target,mode).run()
    else:
        print(f"{C_RED}[!] ABORTADO.")

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C_RED}[!] INTERROMPIDO PELO USUÁRIO.")
