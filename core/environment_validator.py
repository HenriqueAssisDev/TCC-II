# core/environment_validator.py
# Valida se o ambiente está pronto para rodar os programas da Receita

import os
import sys
import subprocess
import platform
import shutil
from typing import Dict, List, Tuple
from datetime import datetime  # <-- ADICIONE ESTA LINHA
from core.logger import log_info, log_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_windows_version() -> Tuple[bool, str]:
    """
    Verifica se o Windows é compatível (Windows 10 ou superior).

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        win_version = platform.win32_ver()
        major_version = int(win_version[0])

        if major_version >= 10:
            return True, f"Windows {major_version} detectado - Compatível"
        else:
            return False, f"Windows {major_version} detectado - Recomendado Windows 10 ou superior"
    except Exception as e:
        log_error(f"Erro ao verificar versão do Windows: {e}")
        return False, f"Erro ao verificar versão do Windows: {e}"


def check_java_runtime() -> Tuple[bool, str]:
    """
    Verifica se o Java Runtime Environment está instalado (necessário para SPED).

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        # Tenta executar 'java -version'
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Java está instalado, extrai a versão
            output = result.stderr  # java -version escreve na stderr
            if "version" in output.lower():
                # Extrai versão (ex: "1.8.0_281" ou "11.0.12")
                lines = output.split('\n')
                version_line = lines[0] if lines else ""
                return True, f"Java detectado: {version_line.strip()}"

        return False, "Java Runtime Environment não encontrado - Necessário para programas SPED"
    except FileNotFoundError:
        return False, "Java Runtime Environment não encontrado - Necessário para programas SPED"
    except Exception as e:
        log_error(f"Erro ao verificar Java: {e}")
        return False, f"Erro ao verificar Java: {e}"


def check_dotnet_framework() -> Tuple[bool, str]:
    """
    Verifica se o .NET Framework 4.5+ está instalado.

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        # Verifica registro do Windows para .NET Framework
        # Chave: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\Release
        cmd = [
            "reg", "query", 
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full",
            "/v", "Release"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # .NET Framework 4.5+ está instalado (Release >= 378389)
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if 'Release' in line:
                    try:
                        release_value = int(line.split()[-1])
                        if release_value >= 378389:
                            return True, f".NET Framework 4.5+ detectado (Release: {release_value})"
                        else:
                            return False, f".NET Framework {release_value} detectado - Versão 4.5+ recomendada"
                    except (ValueError, IndexError):
                        pass

        return False, ".NET Framework 4.5+ não detectado - Necessário para alguns programas"
    except Exception as e:
        log_error(f"Erro ao verificar .NET Framework: {e}")
        return True, ".NET Framework - Verificação não realizada (assumindo compatível)"


def check_admin_privileges() -> Tuple[bool, str]:
    """
    Verifica se o usuário tem privilégios de administrador.

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        # Tenta executar um comando que requer privilégios de admin
        cmd = ["net", "session"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return True, "Privilégios de administrador confirmados"
        else:
            return False, "Executando sem privilégios de administrador - Atualizações podem falhar"
    except Exception as e:
        log_error(f"Erro ao verificar privilégios de admin: {e}")
        return False, f"Erro ao verificar privilégios: {e}"


def check_disk_space(min_mb: int = 500) -> Tuple[bool, str]:
    """
    Verifica se há espaço em disco suficiente.

    Args:
        min_mb: Espaço mínimo em MB

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        total, used, free = shutil.disk_usage(BASE_DIR)
        free_mb = free // (2**20)  # Converte bytes para MB

        if free_mb >= min_mb:
            return True, f"Espaço em disco: {free_mb} MB livres - Suficiente"
        else:
            return False, f"Espaço em disco: {free_mb} MB livres - Recomendado mínimo {min_mb} MB"
    except Exception as e:
        log_error(f"Erro ao verificar espaço em disco: {e}")
        return True, f"Espaço em disco - Verificação não realizada"


def check_internet_connection() -> Tuple[bool, str]:
    """
    Verifica se há conexão com internet (ping para google.com).

    Returns:
        (bool, str): (sucesso, mensagem)
    """
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "google.com"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return True, "Conexão com internet confirmada"
        else:
            return False, "Sem conexão com internet detectada - Verificação de atualizações pode falhar"
    except subprocess.TimeoutExpired:
        return False, "Timeout na verificação de internet - Conexão lenta ou instável"
    except Exception as e:
        log_error(f"Erro ao verificar conexão: {e}")
        return True, "Conexão com internet - Verificação não realizada"


def validate_environment() -> Dict[str, Dict[str, str]]:
    """
    Executa todas as validações de ambiente.

    Returns:
        Dict: {nome_teste: {"status": bool, "mensagem": str}}
    """
    log_info("[VALIDAÇÃO] Iniciando validação de ambiente")

    tests = {
        "Windows": check_windows_version(),
        "Java": check_java_runtime(),
        "NET Framework": check_dotnet_framework(),
        "Administrador": check_admin_privileges(),
        "Disco": check_disk_space(),
        "Internet": check_internet_connection(),
    }

    # Resume o status geral
    passed = sum(1 for status, _ in tests.values() if status)
    total = len(tests)

    log_info(f"[VALIDAÇÃO] {passed}/{total} testes passaram")

    # Adiciona resumo
    tests["Resumo"] = {
        "status": passed == total,
        "mensagem": f"{passed}/{total} pré-requisitos atendidos"
    }

    return tests


def get_environment_report() -> str:
    """
    Gera um relatório textual do ambiente.

    Returns:
        str: Relatório formatado
    """
    tests = validate_environment()
    report_lines = []

    report_lines.append("=== RELATÓRIO DE AMBIENTE ===")
    report_lines.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Diretório: {BASE_DIR}")
    report_lines.append("")

    for test_name, result in tests.items():
        if test_name != "Resumo":
            status_emoji = "✅" if result[0] else "⚠️"
            report_lines.append(f"{status_emoji} {test_name}: {result[1]}")

    report_lines.append("")
    summary_status = tests["Resumo"]["status"]
    summary_emoji = "✅" if summary_status else "⚠️"
    report_lines.append(f"{summary_emoji} {tests['Resumo']['mensagem']}")

    if not summary_status:
        report_lines.append("\nRecomendações:")
        if not tests["Java"][0]:
            report_lines.append("  - Instalar Java Runtime Environment (para programas SPED)")
        if not tests["Administrador"][0]:
            report_lines.append("  - Executar como administrador para atualizações")
        if not tests["Internet"][0]:
            report_lines.append("  - Verificar conexão com internet")

    report_lines.append("=" * 40)

    report = "\n".join(report_lines)
    log_info(f"[RELATÓRIO] Validação de ambiente concluída")

    return report
