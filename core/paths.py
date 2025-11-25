# core/paths.py
"""
Gerenciador de caminhos do Integrador Receita.
Garante funcionamento portátil em qualquer máquina/diretório.
"""
import os
import sys

def get_base_dir() -> str:
    """
    Retorna o diretório base do aplicativo.
    - Modo .exe (PyInstaller): pasta onde está o executável
    - Modo .py (desenvolvimento): raiz do projeto
    Returns:
        str: Caminho absoluto do diretório base
    """
    if getattr(sys, "frozen", False):
        # Executável PyInstaller
        return os.path.dirname(sys.executable)

    # Execução normal (desenvolvimento)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_dir() -> str:
    """
    Retorna o caminho da pasta 'data'.
    Cria a pasta se não existir.

    Returns:
        str: Caminho absoluto da pasta data
    """
    base = get_base_dir()
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_logs_dir() -> str:
    """
    Retorna o caminho da pasta 'logs'.
    Cria a pasta se não existir.

    Returns:
        str: Caminho absoluto da pasta logs
    """
    base = get_base_dir()
    logs_dir = os.path.join(base, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_programs_dir() -> str:
    """
    Retorna o caminho da pasta 'Programas'.
    Cria a pasta se não existir.
    Aqui ficam os programas INSTALADOS (após execução do instalador).

    Returns:
        str: Caminho absoluto da pasta Programas
    """
    base = get_base_dir()
    programs_dir = os.path.join(base, "Programas")
    os.makedirs(programs_dir, exist_ok=True)
    return programs_dir

def get_instaladores_dir() -> str:
    """
    Retorna o caminho da pasta 'Instaladores'.
    Cria a pasta se não existir.
    Aqui ficam os instaladores BAIXADOS (.exe da Receita Federal).

    Returns:
        str: Caminho absoluto da pasta Instaladores
    """
    base = get_base_dir()
    instaladores_dir = os.path.join(base, "Instaladores")
    os.makedirs(instaladores_dir, exist_ok=True)
    return instaladores_dir

def get_shortcuts_dir() -> str:
    """
    Retorna o caminho da pasta 'Atalhos'.
    Cria a pasta se não existir.
    Aqui ficam os atalhos (.lnk) dos programas instalados.

    Returns:
        str: Caminho absoluto da pasta Atalhos
    """
    base = get_base_dir()
    shortcuts_dir = os.path.join(base, "Atalhos")
    os.makedirs(shortcuts_dir, exist_ok=True)
    return shortcuts_dir

def get_versions_file() -> str:
    """
    Retorna o caminho do arquivo versions.json.

    Returns:
        str: Caminho absoluto do versions.json
    """
    return os.path.join(get_data_dir(), "versions.json")

def ensure_directories():
    """
    Garante que todas as pastas necessárias existam.
    Cria automaticamente na primeira execução.

    Esta função é chamada na inicialização do sistema.
    """
    get_data_dir()
    get_logs_dir()
    get_programs_dir()
    get_instaladores_dir()  # ← ADICIONADO
    get_shortcuts_dir()

# Variáveis globais para uso direto
BASE_DIR = get_base_dir()
DATA_DIR = get_data_dir()
LOGS_DIR = get_logs_dir()
PROGRAMS_DIR = get_programs_dir()
INSTALADORES_DIR = get_instaladores_dir()  # ← ADICIONADO
SHORTCUTS_DIR = get_shortcuts_dir()
VERSIONS_FILE = get_versions_file()