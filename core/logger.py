# core/logger.py
"""
Sistema de logging do Integrador Receita.
Registra eventos, erros e informações em arquivo e console.
"""

import logging
from datetime import datetime
import os

from core.paths import get_logs_dir, get_base_dir


def get_logger(name: str = "IntegradorReceita") -> logging.Logger:
    """
    Retorna um logger configurado para o sistema.

    Args:
        name (str): Nome do logger (padrão: "IntegradorReceita")

    Returns:
        logging.Logger: Logger configurado com handlers de arquivo e console
    """
    logger = logging.getLogger(name)

    # Evita adicionar handlers duplicados
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Formato das mensagens
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Arquivo de log em logs/app.log
    logs_dir = get_logs_dir()
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "app.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Saída no console (útil em desenvolvimento)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def log_startup():
    """
    Registra a inicialização do sistema com informações básicas.
    """
    logger = get_logger()
    base_dir = get_base_dir()
    logs_dir = get_logs_dir()

    logger.info("=== INICIALIZAÇÃO DO INTEGRADOR RECEITA ===")
    logger.info(f"Sistema iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Diretório base: {base_dir}")
    logger.info(f"Pasta de logs: {logs_dir}")
    logger.info("==========================================")


def log_info(message: str):
    """
    Registra uma mensagem de informação.

    Args:
        message (str): Mensagem a ser registrada
    """
    logger = get_logger()
    logger.info(message)


def log_error(message: str):
    """
    Registra uma mensagem de erro.

    Args:
        message (str): Mensagem de erro a ser registrada
    """
    logger = get_logger()
    logger.error(message)


def log_warning(message: str):
    """
    Registra uma mensagem de aviso.

    Args:
        message (str): Mensagem de aviso a ser registrada
    """
    logger = get_logger()
    logger.warning(message)


def log_debug(message: str):
    """
    Registra uma mensagem de debug (nível INFO com prefixo [DEBUG]).

    Args:
        message (str): Mensagem de debug a ser registrada
    """
    logger = get_logger()
    logger.info(f"[DEBUG] {message}")


def log(msg: str, level: str = "INFO"):
    """
    Função rápida para registrar mensagens em diferentes níveis.

    Args:
        msg (str): Mensagem a ser registrada
        level (str): "INFO", "ERROR", "WARNING" ou "DEBUG"
    """
    logger = get_logger()
    level = level.upper()

    if level == "ERROR":
        logger.error(msg)
    elif level == "WARNING":
        logger.warning(msg)
    elif level == "DEBUG":
        logger.info(f"[DEBUG] {msg}")
    else:
        logger.info(msg)


if __name__ == "__main__":
    # Teste rápido do logger
    log_startup()
    log_info("Teste de log funcionando!")
    log_warning("Teste de aviso")
    log_error("Teste de erro simulado")
    log_debug("Mensagem de debug")