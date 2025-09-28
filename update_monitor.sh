#!/bin/bash

SERVICE_NAME="monitor-ping"
PROJECT_DIR="$(pwd)"  # usa a pasta atual

echo "=== Parando o serviço $SERVICE_NAME ==="
sudo systemctl stop $SERVICE_NAME

echo "=== Atualizando código via Git na pasta $PROJECT_DIR ==="
git pull origin main

echo "=== Reiniciando o serviço $SERVICE_NAME ==="
sudo systemctl start $SERVICE_NAME

echo "=== Status do serviço ==="
sudo systemctl status $SERVICE_NAME --no-pager

