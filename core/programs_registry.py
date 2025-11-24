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
    SHORTCUTS_DIR,
    VERSIONS_FILE,
    ensure_directories,
)
from core.logger import log_info, log_error, log_warning


# Garante que as pastas principais existam
ensure_directories()


def create_default_versions_file() -> None:
    """
    Cria um arquivo versions.json padrão se ele não existir.
    Este arquivo define os programas gerenciados pelo Integrador.
    """
    default_versions: Dict[str, Dict] = {
        "IRPF2025": {
            "nome": "IRPF 2025",
            "versao_disponivel": "1.0",
            "url_download": "https://downloadirpf.receita.fazenda.gov.br/irpf/2025/irpf/arquivos/IRPF2025-1.0.zip",
            "executavel_nome": "IRPF2025.exe",
            "atalho_nome": "IRPF 2025.lnk",
            "descricao": "Declaração do Imposto de Renda Pessoa Física 2025",
        },
        "IRPF2024": {
            "nome": "IRPF 2024",
            "versao_disponivel": "1.0",
            "url_download": "https://downloadirpf.receita.fazenda.gov.br/irpf/2024/irpf/arquivos/IRPF2024-1.0.zip",
            "executavel_nome": "IRPF2024.exe",
            "atalho_nome": "IRPF 2024.lnk",
            "descricao": "Declaração do Imposto de Renda Pessoa Física 2024",
        },
        "DIRF": {
            "nome": "DIRF 2025",
            "versao_disponivel": "1.0",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/dirf/dirf-2025",
            "executavel_nome": "DIRF2025.exe",
            "atalho_nome": "DIRF 2025.lnk",
            "descricao": "Declaração do Imposto de Renda Retido na Fonte 2025",
        },
        "DCTF": {
            "nome": "DCTF 2025",
            "versao_disponivel": "1.0",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/dctf/dctf-2025",
            "executavel_nome": "DCTF2025.exe",
            "atalho_nome": "DCTF 2025.lnk",
            "descricao": "Declaração de Débitos e Créditos Tributários Federais",
        },
        "ReceitaNet": {
            "nome": "Receitanet",
            "versao_disponivel": "3.9.7",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/receitanet",
            "executavel_nome": "Receitanet.exe",
            "atalho_nome": "Receitanet.lnk",
            "descricao": "Programa para transmissão de declarações pela internet",
        },
        "ReceitaNetBX": {
            "nome": "Receitanet BX",
            "versao_disponivel": "1.0.5",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/receitanet-bx",
            "executavel_nome": "ReceitanetBX.exe",
            "atalho_nome": "Receitanet BX.lnk",
            "descricao": "Receitanet para download de declarações",
        },
        "SPEDContrib": {
            "nome": "SPED Contribuições",
            "versao_disponivel": "1.0",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/sped-contribuicoes",
            "executavel_nome": "SPEDContrib.exe",
            "atalho_nome": "SPED Contribuições.lnk",
            "descricao": "Sistema Público de Escrituração Digital das Contribuições",
        },
        "SPEDEFD": {
            "nome": "SPED EFD",
            "versao_disponivel": "4.0.5",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/sped-efd",
            "executavel_nome": "SPEDEFD.exe",
            "atalho_nome": "SPED EFD.lnk",
            "descricao": "Escrituração Fiscal Digital",
        },
        "SPEDFiscal": {
            "nome": "SPED Fiscal",
            "versao_disponivel": "4.0.5",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/sped-fiscal",
            "executavel_nome": "SPEDFiscal.exe",
            "atalho_nome": "SPED Fiscal.lnk",
            "descricao": "SPED Fiscal - ICMS/IPI",
        },
        "SPEDICMSIPI": {
            "nome": "SPED ICMS/IPI",
            "versao_disponivel": "4.0.5",
            "url_download": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download/sped-icms-ipi",
            "executavel_nome": "SPEDICMSIPI.exe",
            "atalho_nome": "SPED ICMS IPI.lnk",
            "descricao": "SPED ICMS/IPI",
        },
    }

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_versions, f, indent=4, ensure_ascii=False)
        log_info(f"[VERSIONS] Arquivo padrão criado em {VERSIONS_FILE}")
    except Exception as e:
        log_error(f"[VERSIONS] Erro ao criar versions.json: {e}")


def load_versions_file() -> Dict[str, Dict]:
    """
    Carrega o arquivo versions.json. Cria um padrão se não existir.

    Returns:
        Dict[str, Dict]: Dicionário com os programas e suas informações.
    """
    if not os.path.exists(VERSIONS_FILE):
        log_warning(f"[VERSIONS] {VERSIONS_FILE} não encontrado. Criando padrão.")
        create_default_versions_file()

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

    Regra atual:
    - Se existir um atalho correspondente em Atalhos/ -> Instalado
    - Senão, se existir o executável em Programas/   -> Instalado
    - Caso contrário                                -> Não Instalado
    """
    versions = load_versions_file()
    info = versions.get(program_id, {})

    # 1) Checa atalho
    atalho_nome = info.get("atalho_nome", f"{program_id}.lnk")
    shortcut_path = os.path.join(SHORTCUTS_DIR, atalho_nome)
    if os.path.exists(shortcut_path):
        log_info(f"[STATUS] {program_id}: Instalado (atalho encontrado)")
        return "Instalado"

    # 2) Checa executável
    exe_nome = info.get("executavel_nome", "")
    if exe_nome:
        exe_path = os.path.join(PROGRAMS_DIR, exe_nome)
        if os.path.exists(exe_path):
            log_info(f"[STATUS] {program_id}: Instalado (executável encontrado)")
            return "Instalado"

    log_info(f"[STATUS] {program_id}: Não Instalado")
    return "Não Instalado"


def get_local_version(program_id: str) -> str:
    """
    Obtém a versão local do programa.

    Implementação simples:
    - Se estiver instalado, retornamos a mesma versao_disponivel do versions.json.

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
    Retorna o caminho completo do executável/instalador do programa em Programas/.

    Args:
        program_id (str): ID do programa

    Returns:
        str: Caminho completo do arquivo em Programas/, ou "" se não for encontrado
    """
    versions = load_versions_file()
    info = versions.get(program_id)
    if not info:
        return ""

    exe_nome = info.get("executavel_nome", "")
    if not exe_nome:
        return ""

    return os.path.join(PROGRAMS_DIR, exe_nome)


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
            - executavel_nome
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
            "executavel_nome": info.get("executavel_nome", ""),
            "atalho_nome": info.get("atalho_nome", ""),
            "descricao": info.get("descricao", ""),
        }
        programs.append(program_data)

    return programs


def get_all_programs_status() -> Dict[str, str]:
    """
    Retorna um dicionário com o status de todos os programas.
    Função usada pela interface para atualizar a tabela.

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
        # 2) Tenta executável
        exe_path = get_installer_path(program_id)
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
    # Teste rápido do módulo em modo desenvolvimento
    print("=== TESTE PROGRAMS_REGISTRY ===")
    ensure_directories()

    programas = get_program_list()
    for p in programas:
        print(
            f"{p['nome']}: {p['status']} "
            f"(local: {p['versao_local']} / disponível: {p['versao_disponivel']})"
        )

    print(f"\nTotal de programas: {len(programas)}")

    print("\n=== STATUS DE TODOS OS PROGRAMAS ===")
    status_all = get_all_programs_status()
    for prog_id, status in status_all.items():
        print(f"{prog_id}: {status}")

    print("================================")