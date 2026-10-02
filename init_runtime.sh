#!/bin/bash
# Archivo: init_runtime.sh
# Propósito: Bootloader para el runtime operativo del microkernel y motor de eventos

set -e

echo "[+] Inicializando pipeline de ejecución del microkernel..."

# 1. Verificación del módulo de aislamiento de memoria (Virtual Environment)
if [ ! -d "venv" ]; then
    echo "[!] Entorno virtual no detectado. Creando capa de aislamiento (venv)..."
    python3 -m venv venv
fi

# 2. Activación del contexto de ejecución local
source venv/bin/activate

# 3. Construcción del entorno (Equivalente a fase de "compilación")
echo "[+] Inyectando dependencias base del sistema..."
pip install --upgrade pip > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    echo "[+] Verificando manifiesto de requerimientos..."
    pip install -r requirements.txt
else
    echo "[!] Advertencia crítica: requirements.txt no encontrado. Riesgo de fallo en módulos centrales."
fi

# 4. Arranque del Event Bus y Orquestador Principal
echo "[+] Levantando orquestador, conectando base SQLite WAL y arrancando Event Bus..."
if [ -f "run_chango.py" ]; then
    python3 run_chango.py
else
    echo "[-] Error crítico: Archivo de entrada (run_chango.py) no localizado en el directorio raíz."
    exit 1
fi
