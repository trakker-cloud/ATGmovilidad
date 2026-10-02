# =====================================================================
# Etiqueta: APP_CHANGO_MAKEFILE_02102026
# Proyecto: app chango
# Arquitectura: Automation & Build Lifecycle Manager
# =====================================================================

.PHONY: help build up down restart logs test clean prune

help:
	@echo "========================================================="
	@echo " COMANDOS DISPONIBLES PARA APP CHANGO RUNTIME:"
	@echo "========================================================="
	@echo "  make build   - Compila la imagen Docker del microkernel"
	@echo "  make up      - Enciende el contenedor en segundo plano"
	@echo "  make down    - Detiene los servicios de contenedores"
	@echo "  make restart - Reinicia el runtime del microkernel"
	@echo "  make logs    - Muestra los logs en tiempo real"
	@echo "  make test    - Ejecuta el orquestador maestro y health check"
	@echo "  make clean   - Limpia volúmenes de datos y contenedores"
	@echo "========================================================="

build:
	sudo docker compose build

up:
	sudo docker compose up -d
	@echo "[OK] Contenedor chango_runtime_node en marcha."

down:
	sudo docker compose down
	@echo "[INFO] Contenedor detenido."

restart: down up

logs:
	sudo docker logs -f chango_runtime_node

test:
	@echo "--- Ejecutando pruebas locales del microkernel ---"
	python3 run_chango.py
	@echo "--- Probando API Gateway endpoint principal ---"
	curl -s http://localhost:8000/ && echo ""

clean:
	sudo docker compose down -v
	rm -rf data/*.db
	@echo "[WARN] Entorno purgado y datos locales eliminados."
