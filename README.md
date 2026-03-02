# VD
no terminal use 2 ou 3 vezes o comando abaixo
```py
pkg update -y && pkg upgrade -y && pkg install python -y

# Instala dependências uma por uma
python3 - <<'EOF'
import subprocess
import sys
libs = ['requests','bs4','colorama','urllib3']
for lib in libs:
    try:
        __import__(lib)
        print(f"[✓] {lib} já instalado")
    except ImportError:
        print(f"[!] Instalando {lib}...")
        subprocess.check_call([sys.executable,'-m','pip','install',lib])
        print(f"[✓] {lib} instalado")
EOF

# Baixa e executa o script do GitHub
curl -L -o VDmirror.py3 https://raw.githubusercontent.com/higuysdorobloxjoaopk-maker/VD/refs/heads/main/VD.py
python3 VDmirror.py
```
bem use para aprender essa ferramenta serve e é para fins educacionais 
