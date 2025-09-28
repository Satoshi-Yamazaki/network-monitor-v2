#!/bin/bash
set -e  # Para em qualquer erro

echo "
  ██████   █████ ██████████ ███████████ █████   ███   █████    ███████    ███████████   █████   ████
▒▒██████ ▒▒███ ▒▒███▒▒▒▒▒█▒█▒▒▒███▒▒▒█▒▒███   ▒███  ▒▒███   ███▒▒▒▒▒███ ▒▒███▒▒▒▒▒███ ▒▒███   ███▒ 
 ▒███▒███ ▒███  ▒███  █ ▒ ▒   ▒███  ▒  ▒███   ▒███   ▒███  ███     ▒▒███ ▒███    ▒███  ▒███  ███   
 ▒███▒▒███▒███  ▒██████       ▒███     ▒███   ▒███   ▒███ ▒███      ▒███ ▒██████████   ▒███████    
 ▒███ ▒▒██████  ▒███▒▒█       ▒███     ▒▒███  █████  ███  ▒███      ▒███ ▒███▒▒▒▒▒███  ▒███▒▒███   
 ▒███  ▒▒█████  ▒███ ▒   █    ▒███      ▒▒▒█████▒█████▒   ▒▒███     ███  ▒███    ▒███  ▒███ ▒▒███  
 █████  ▒▒█████ ██████████    █████       ▒▒███ ▒▒███      ▒▒▒███████▒   █████   █████ █████ ▒▒████
▒▒▒▒▒    ▒▒▒▒▒ ▒▒▒▒▒▒▒▒▒▒    ▒▒▒▒▒         ▒▒▒   ▒▒▒         ▒▒▒▒▒▒▒    ▒▒▒▒▒   ▒▒▒▒▒ ▒▒▒▒▒   ▒▒▒▒ 
                                                                                                   
                                                                                                   
                                                                                                   
 ██████   ██████    ███████    ██████   █████ █████ ███████████    ███████    ███████████          
▒▒██████ ██████   ███▒▒▒▒▒███ ▒▒██████ ▒▒███ ▒▒███ ▒█▒▒▒███▒▒▒█  ███▒▒▒▒▒███ ▒▒███▒▒▒▒▒███         
 ▒███▒█████▒███  ███     ▒▒███ ▒███▒███ ▒███  ▒███ ▒   ▒███  ▒  ███     ▒▒███ ▒███    ▒███         
 ▒███▒▒███ ▒███ ▒███      ▒███ ▒███▒▒███▒███  ▒███     ▒███    ▒███      ▒███ ▒██████████          
 ▒███ ▒▒▒  ▒███ ▒███      ▒███ ▒███ ▒▒██████  ▒███     ▒███    ▒███      ▒███ ▒███▒▒▒▒▒███         
 ▒███      ▒███ ▒▒███     ███  ▒███  ▒▒█████  ▒███     ▒███    ▒▒███     ███  ▒███    ▒███         
 █████     █████ ▒▒▒███████▒   █████  ▒▒█████ █████    █████    ▒▒▒███████▒   █████   █████        
▒▒▒▒▒     ▒▒▒▒▒    ▒▒▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒ ▒▒▒▒▒    ▒▒▒▒▒       ▒▒▒▒▒▒▒    ▒▒▒▒▒   ▒▒▒▒▒         
                                                                                                   
                                                                                     By Satoshi Yamazaki
                                                                         "

echo "=== Atualizando pacotes ==="
sudo apt update && sudo apt upgrade -y

echo "=== Instalando Python e ferramentas ==="
sudo apt install -y python3 python3-venv python3-pip

echo "=== Instalando Snap ==="
sudo apt install -y snapd
sudo systemctl enable --now snapd

echo "=== Instalando Firefox ==="
sudo apt install -y firefox

echo "=== Instalando AnyDesk ==="
wget -qO anydesk.deb https://download.anydesk.com/linux/anydesk_7.1.0-1_amd64.deb
sudo apt install -y ./anydesk.deb
rm -f anydesk.deb

echo "=== Configurando AnyDesk para acesso não supervisionado ==="
# Substitua pela senha desejada
read -s -p "Senha para AnyDesk (unattended): " UNATTENDED_PWD
echo
TARGET_USER=$(whoami)

sudo systemctl enable --now anydesk.service || true
sleep 1

sudo -u "$TARGET_USER" mkdir -p "/home/$TARGET_USER/.anydesk"
sudo -u "$TARGET_USER" bash -c "cat >> /home/$TARGET_USER/.anydesk/user.conf <<'EOF'
ad.features.unattended=true
ad.security.allow_logon_token=true
EOF
"
echo -n "$UNATTENDED_PWD" | sudo anydesk --set-password
sudo anydesk --get-status || true
sudo anydesk --get-id || true

echo "=== Instalando Featherpad (editor de texto) ==="
sudo apt install -y featherpad

echo "=== Instalando SQLite e DB Browser ==="
sudo apt install -y sqlite3 sqlitebrowser

echo "=== Criando virtualenv e instalando Flask ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask speedtest-cli

echo "=== Preparando pastas de logs ==="
mkdir -p logs

echo "=== Criando serviço systemd para monitor ==="
SERVICE_FILE="/etc/systemd/system/monitor-ping.service"
PROJECT_DIR="$(pwd)"
USER_NAME=$(whoami)

sudo bash -c "cat > $SERVICE_FILE <<EOF
[Unit]
Description=Monitor de Ping
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
"

echo "=== Recarregando systemd ==="
sudo systemctl daemon-reload

echo "=== Ativando serviço para iniciar junto com o sistema ==="
sudo systemctl enable monitor-ping.service

echo "=== Iniciando serviço agora ==="
sudo systemctl start monitor-ping.service

echo "=== Status do serviço ==="
sudo systemctl status monitor-ping.service --no-pager

echo "=== Setup finalizado ==="
echo "Para iniciar a aplicação manualmente (fora do serviço):"
echo "1. source venv/bin/activate"
echo "2. python app.py"
