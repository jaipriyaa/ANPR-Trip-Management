#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Docker Stack Manager (Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ACTION="${1:-up}"

cd "${PROJECT_ROOT}"

echo "======================================================================"
echo "  ANPR & TRIP MANAGEMENT PLATFORM - DOCKER ORCHESTRATION"
echo "  Action: ${ACTION}"
echo "======================================================================"

case "${ACTION}" in
    up|start)
        echo "Launching containers in foreground..."
        docker compose up --build
        ;;
    up-d|daemon)
        echo "Launching containers in detached mode..."
        docker compose up --build -d
        echo "✓ Stack launched in background. View logs with: bash scripts/docker_run.sh logs"
        ;;
    down|stop)
        echo "Stopping and removing containers..."
        docker compose down
        echo "✓ Docker containers stopped."
        ;;
    build)
        echo "Building container images..."
        docker compose build
        echo "✓ Docker images built."
        ;;
    logs)
        echo "Tailing container logs..."
        docker compose logs -f
        ;;
    ps|status)
        docker compose ps
        ;;
    restart)
        echo "Restarting stack..."
        docker compose restart
        ;;
    *)
        echo "Usage: bash scripts/docker_run.sh [up|daemon|down|build|logs|status|restart]"
        exit 1
        ;;
esac
