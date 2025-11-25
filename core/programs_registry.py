# core/programs_registry.py
"""
Registro e gerenciamento de programas da Receita Federal.
Lê versions.json, verifica instalação e retorna dados para a interface.
"""

import os
import json
import subprocess
from typing import Dict, List, Optional

from core.paths import (
    DATA_DIR,
    PROGRAMS_DIR,
    INSTALADORES_DIR,  # ← ADICIONADO
    SHORTCUTS_DIR,
    VERSIONS_FILE,
    ensure_directories,
)
from core.logger import log_info, log_error, log_warning


# Garante que as pastas principais existam
ensure_directories()


def load_versions_file() -> Dict[str, Dict]:
    """
    Carrega o arquivo versions.json.

    Returns:
        Dict[str, Dict]: Dicionário com os programas e suas informações.
    """
    if not os.path.exists(VERSIONS_FILE):
        log_error(f"[VERSIONS] {VERSIONS_FILE} não encontrado!")
        return {}

    try:
        with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
            data: Dict[str, Dict] = json.load(f)
        log_info(f"[VERSIONS] Arquivo versions.json carregado ({len(data)} programas).")
        return data
    except Exception as e:
        log_error(f"[VERSIONS] Erro ao ler {VERSIONS_FILE}: {e}")
        return {}


def get_program_status(program_id: str) -> str:
    """
    Verifica se o programa está instalado.

    Regra:
    - Se existir um atalho correspondente em Atalhos/ -> Instalado
    - Senão, se existir o executável em Programas/   -> Instalado
    - Caso contrário                                  -> Não Instalado
    """
    versions = load_versions_file()
    info = versions.get(program_id, {})

    # 1) Checa atalho
    atalho_nome = info.get("atalho_nome", f"{program_id}.lnk")
    shortcut_path = os.path.join(SHORTCUTS_DIR, atalho_nome)
    if os.path.exists(shortcut_path):
        log_info(f"[STATUS] {program_id}: Instalado (atalho encontrado)")
        return "Instalado"

    # 2) Checa executável em PROGRAMS_DIR
    nome_arquivo = info.get("nome_arquivo", "")
    if nome_arquivo:
        exe_path = os.path.join(PROGRAMS_DIR, nome_arquivo)
        if os.path.exists(exe_path):
            log_info(f"[STATUS] {program_id}: Instalado (executável encontrado)")
            return "Instalado"

    log_info(f"[STATUS] {program_id}: Não Instalado")
    return "Não Instalado"


def get_local_version(program_id: str) -> str:
    """
    Obtém a versão local do programa.

    Se estiver instalado, retorna a versao_disponivel do versions.json.

    Args:
        program_id (str): ID do programa

    Returns:
        str: Versão local ou "N/D"
    """
    status = get_program_status(program_id)
    if status != "Instalado":
        return "N/D"

    versions = load_versions_file()
    info = versions.get(program_id)
    if not info:
        return "N/D"

    return info.get("versao_disponivel", "N/D")


def get_installer_path(program_id: str) -> str:
    """
    Retorna o caminho completo do instalador baixado em Instaladores/.

    Args:
        program_id (str): ID do programa

    Returns:
        str: Caminho completo do arquivo em Instaladores/, ou "" se não encontrado
    """
    versions = load_versions_file()
    info = versions.get(program_id)
    if not info:
        return ""

    # ===== CORREÇÃO: usar nome_arquivo =====
    nome_arquivo = info.get("nome_arquivo", "")
    if not nome_arquivo:
        return ""

    # ===== CORREÇÃO: buscar em INSTALADORES_DIR =====
    return os.path.join(INSTALADORES_DIR, nome_arquivo)


def get_shortcut_path(program_id: str) -> str:
    """
    Retorna o caminho completo do atalho (.lnk) do programa em Atalhos/.

    Args:
        program_id (str): ID do programa

    Returns:
        str: Caminho completo do atalho .lnk
    """
    versions = load_versions_file()
    info = versions.get(program_id, {})

    atalho_nome = info.get("atalho_nome", f"{program_id}.lnk")
    return os.path.join(SHORTCUTS_DIR, atalho_nome)


def is_program_installed(program_id: str) -> bool:
    """
    Retorna True se o programa estiver instalado, False caso contrário.
    """
    return get_program_status(program_id) == "Instalado"


def get_program_info(program_id: str) -> Optional[Dict]:
    """
    Retorna o dicionário de informações de um programa específico
    a partir do versions.json.

    Args:
        program_id (str): ID do programa

    Returns:
        Optional[Dict]: Informações do programa ou None se não existir
    """
    versions = load_versions_file()
    return versions.get(program_id)


def get_program_list() -> List[Dict]:
    """
    Retorna uma lista de programas com informações completas
    para preenchimento da tabela na interface.

    Returns:
        List[Dict]: Lista de programas com campos:
            - id
            - nome
            - status
            - versao_local
            - versao_disponivel
            - url_download
            - nome_arquivo
            - atalho_nome
            - descricao
    """
    versions = load_versions_file()
    programs: List[Dict] = []

    for program_id, info in versions.items():
        program_data = {
            "id": program_id,
            "nome": info.get("nome", program_id),
            "status": get_program_status(program_id),
            "versao_local": get_local_version(program_id),
            "versao_disponivel": info.get("versao_disponivel", "N/D"),
            "url_download": info.get("url_download", ""),
            "nome_arquivo": info.get("nome_arquivo", ""),  # ← CORRIGIDO
            "atalho_nome": info.get("atalho_nome", ""),
            "descricao": info.get("descricao", ""),
        }
        programs.append(program_data)

    return programs


def get_all_programs_status() -> Dict[str, str]:
    """
    Retorna um dicionário com o status de todos os programas.

    Returns:
        Dict[str, str]: {program_id: "Instalado" ou "Não Instalado"}
    """
    versions = load_versions_file()
    status_dict: Dict[str, str] = {}

    for program_id in versions.keys():
        status_dict[program_id] = get_program_status(program_id)

    return status_dict


def run_program(program_id: str) -> bool:
    """
    Executa o programa instalado via atalho ou executável.
    """
    try:
        # 1) Tenta atalho
        shortcut_path = get_shortcut_path(program_id)
        if os.path.exists(shortcut_path):
            subprocess.Popen(['cmd', '/c', 'start', '', shortcut_path], shell=True)
            log_info(f"[RUN] Executando via atalho: {shortcut_path}")
            return True

        # 2) Tenta executável em PROGRAMS_DIR
        versions = load_versions_file()
        info = versions.get(program_id, {})
        nome_arquivo = info.get("nome_arquivo", "")

        if nome_arquivo:
            exe_path = os.path.join(PROGRAMS_DIR, nome_arquivo)
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path], shell=True)
                log_info(f"[RUN] Executando via executável: {exe_path}")
                return True

        log_warning(f"[RUN] Não foi possível localizar {program_id}")
        return False

    except Exception as e:
        log_error(f"[RUN] Erro ao executar {program_id}: {e}")
        return False


if __name__ == "__main__":
    # Teste rápido do módulo
    print("=== TESTE PROGRAMS_REGISTRY ===")
    ensure_directories()

    programas = get_program_list()
    for p in programas:
        print(
            f"{p['nome']}: {p['status']} "
            f"(local: {p['versao_local']} / disponível: {p['versao_disponivel']})"
        )

    print(f"\nTotal de programas: {len(programas)}")
    print("================================")