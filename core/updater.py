# core/updater.py
"""
Sistema de atualização e instalação dos programas da Receita Federal.
Gerencia downloads, execução de instaladores e criação de atalhos.
"""

import os
import json
import subprocess
from typing import Dict, Optional, Tuple

from core.paths import (
    PROGRAMS_DIR,
    SHORTCUTS_DIR,
    VERSIONS_FILE,
    ensure_directories,
)
from core.logger import log_info, log_error, log_warning
from core.programs_registry import (
    get_program_info,
    get_installer_path,
    get_shortcut_path,
    is_program_installed,
    get_program_list,
)

ensure_directories()


class Updater:
    """Classe principal para gerenciamento de atualizações e instalações."""

    def __init__(self) -> None:
        self.current_download: Optional[str] = None
        self.download_progress: int = 0
        self.is_downloading: bool = False

    def load_versions_file(self) -> Dict:
        """Carrega o arquivo versions.json."""
        if os.path.exists(VERSIONS_FILE):
            try:
                with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log_error(f"[UPDATER] Erro ao ler versions.json: {e}")
        return {}

    def get_local_version(self, program_id: str) -> str:
        """Obtém a versão local do programa."""
        installer_path = get_installer_path(program_id)
        if not os.path.exists(installer_path):
            return "N/D"

        try:
            info = get_program_info(program_id)
            if info:
                return info.get("versao_disponivel", "N/D")
            return "N/D"
        except Exception:
            return "N/D"

    def compare_versions(self, v1: str, v2: str) -> int:
        """Compara duas versões."""
        try:
            from packaging import version

            if version.parse(v1) < version.parse(v2):
                return -1
            if version.parse(v1) > version.parse(v2):
                return 1
            return 0
        except ImportError:
            if v1 == "N/D":
                return -1
            if v2 == "N/D":
                return 1
            if v1 == v2:
                return 0
            return -1 if v1 < v2 else 1

    def check_for_updates(self) -> Dict[str, bool]:
        """Verifica se há atualizações disponíveis."""
        updates_available: Dict[str, bool] = {}
        versions = self.load_versions_file()

        for program_id, info in versions.items():
            versao_disponivel = info.get("versao_disponivel", "0.0")
            versao_local = self.get_local_version(program_id)

            if versao_local == "N/D" or self.compare_versions(versao_local, versao_disponivel) < 0:
                updates_available[program_id] = True
            else:
                updates_available[program_id] = False

        log_info(f"[UPDATE] {sum(updates_available.values())} atualizações disponíveis")
        return updates_available

    def download_program(self, program_id: str, callback=None) -> bool:
        """Baixa o instalador de um programa."""
        info = get_program_info(program_id)
        if not info:
            log_error(f"[DOWNLOAD] Programa {program_id} não encontrado")
            return False

        url = info.get("url_download", "")
        if not url:
            log_error(f"[DOWNLOAD] URL não encontrada para {program_id}")
            return False

        exe_name = info.get("executavel_nome", f"{program_id}.exe")
        download_path = os.path.join(PROGRAMS_DIR, exe_name)

        try:
            import requests

            log_info(f"[DOWNLOAD] Iniciando download de {program_id}")
            self.is_downloading = True
            self.current_download = program_id
            self.download_progress = 0

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(download_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            self.download_progress = int((downloaded_size / total_size) * 100)
                            if callback:
                                callback(self.download_progress)

            self.download_progress = 100
            self.is_downloading = False
            self.current_download = None

            if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
                log_info(f"[DOWNLOAD] {program_id} baixado com sucesso")
                return True

            log_error(f"[DOWNLOAD] Arquivo vazio: {download_path}")
            return False

        except ImportError:
            log_error("[DOWNLOAD] 'requests' não instalado. Execute: pip install requests")
            self.is_downloading = False
            self.current_download = None
            return False
        except Exception as e:
            log_error(f"[DOWNLOAD] Erro ao baixar {program_id}: {e}")
            self.is_downloading = False
            self.current_download = None
            return False

    def install_program(self, program_id: str) -> bool:
        """Executa o instalador do programa."""
        installer_path = get_installer_path(program_id)

        if not os.path.exists(installer_path):
            log_error(f"[INSTALL] Instalador não encontrado: {installer_path}")
            return False

        try:
            log_info(f"[INSTALL] Executando instalador: {installer_path}")
            result = subprocess.Popen([installer_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

            if result:
                log_info(f"[INSTALL] Instalador de {program_id} iniciado (PID {result.pid})")
                return True

            log_error(f"[INSTALL] Falha ao iniciar instalador de {program_id}")
            return False

        except Exception as e:
            log_error(f"[INSTALL] Erro ao executar instalador: {e}")
            return False

    def create_shortcut(self, program_id: str, target_path: str, shortcut_name: Optional[str] = None) -> bool:
        """Cria um atalho (.lnk) para o programa."""
        try:
            from win32com.client import Dispatch
        except ImportError:
            log_warning("[SHORTCUT] pywin32 não instalado. Execute: pip install pywin32")
            return False

        try:
            info = get_program_info(program_id)
            if not shortcut_name:
                if info:
                    shortcut_name = info.get("atalho_nome", f"{program_id}.lnk")
                else:
                    shortcut_name = f"{program_id}.lnk"

            shortcut_path = get_shortcut_path(program_id)

            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.WindowStyle = 1
            shortcut.IconLocation = target_path
            shortcut.save()

            log_info(f"[SHORTCUT] Atalho criado: {shortcut_path}")
            return True

        except Exception as e:
            log_error(f"[SHORTCUT] Erro ao criar atalho: {e}")
            return False

    def update_all_programs(self, callback=None) -> Dict[str, str]:
        """Atualiza todos os programas que precisam."""
        results: Dict[str, str] = {}
        updates = self.check_for_updates()
        total = len(updates)
        current = 0

        for program_id, needs_update in updates.items():
            if not needs_update:
                results[program_id] = "pular"
                continue

            current += 1
            log_info(f"[UPDATE] Processando {program_id} ({current}/{total})")

            if self.download_program(program_id, callback):
                results[program_id] = "download_ok"
            else:
                results[program_id] = "erro_download"

            if callback and total > 0:
                callback(int((current / total) * 100))

        return results

    def get_download_status(self) -> Dict:
        """Retorna o status atual do download."""
        return {
            "is_downloading": self.is_downloading,
            "current_program": self.current_download,
            "progress": self.download_progress,
        }


updater = Updater()


def download_and_install(program_id: str, progress_callback=None) -> Tuple[bool, str]:
    """Função de conveniência: baixa e instala um programa."""
    try:
        if is_program_installed(program_id):
            return True, f"{program_id} já está instalado"

        if updater.download_program(program_id, progress_callback):
            if updater.install_program(program_id):
                return True, f"{program_id} baixado e instalação iniciada"
            return False, f"{program_id} baixado, mas falha na instalação"

        return False, f"Falha no download de {program_id}"

    except Exception as e:
        log_error(f"[UPDATE] Erro geral: {e}")
        return False, f"Erro inesperado: {str(e)}"


def create_all_shortcuts() -> int:
    """Cria atalhos para todos os programas instalados."""
    count = 0
    programs = get_program_list()

    for program in programs:
        if program["status"] == "Instalado":
            program_id = program["id"]
            installer_path = get_installer_path(program_id)

            if os.path.exists(installer_path):
                if updater.create_shortcut(program_id, installer_path):
                    count += 1
                else:
                    log_warning(f"[SHORTCUT] Falha ao criar atalho para {program_id}")

    log_info(f"[SHORTCUT] Criados {count} atalhos")
    return count


if __name__ == "__main__":
    print("=== TESTE UPDATER ===")
    updates = updater.check_for_updates()
    print(f"Atualizações disponíveis: {sum(updates.values())}")
    for program_id, needs_update in updates.items():
        if needs_update:
            print(f"  - {program_id}")
    print("=====================")