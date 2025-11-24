# core/downloader.py
# Módulo responsável por baixar instaladores da internet

import os
import requests
from typing import Optional, Callable

# Pasta onde os instaladores serão salvos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALADORES_DIR = os.path.join(BASE_DIR, "Instaladores")

# Garante que a pasta Instaladores existe
os.makedirs(INSTALADORES_DIR, exist_ok=True)


def download_file(
    url: str,
    destino: str,
    callback_progresso: Optional[Callable[[int, int], None]] = None
) -> bool:
    """
    Baixa um arquivo da URL especificada para o destino local.

    Args:
        url: URL do arquivo a ser baixado
        destino: Caminho completo onde o arquivo será salvo
        callback_progresso: Função opcional para reportar progresso (bytes_baixados, total_bytes)

    Returns:
        True se o download foi bem-sucedido, False caso contrário
    """
    try:
        print(f"[DOWNLOAD] Iniciando download de: {url}")

        # Faz a requisição HTTP com streaming
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Levanta exceção se status != 200

        # Obtém o tamanho total do arquivo (se disponível)
        total_size = int(response.headers.get('content-length', 0))

        # Abre o arquivo de destino para escrita binária
        with open(destino, 'wb') as file:
            bytes_baixados = 0

            # Baixa em chunks de 8KB
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filtra chunks vazios
                    file.write(chunk)
                    bytes_baixados += len(chunk)

                    # Chama callback de progresso se fornecido
                    if callback_progresso:
                        callback_progresso(bytes_baixados, total_size)

        print(f"[DOWNLOAD] Concluído: {destino}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha no download: {e}")
        # Remove arquivo parcial se existir
        if os.path.exists(destino):
            os.remove(destino)
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        if os.path.exists(destino):
            os.remove(destino)
        return False


def download_installer(program_id: str, url: str, nome_arquivo: str) -> Optional[str]:
    """
    Baixa o instalador de um programa específico.

    Args:
        program_id: ID do programa (ex: "IRPF2025")
        url: URL de download
        nome_arquivo: Nome do arquivo a ser salvo

    Returns:
        Caminho completo do arquivo baixado, ou None se falhou
    """
    destino = os.path.join(INSTALADORES_DIR, nome_arquivo)

    # Se já existe, pergunta se quer sobrescrever (por enquanto, sobrescreve sempre)
    if os.path.exists(destino):
        print(f"[INFO] Arquivo já existe, será sobrescrito: {destino}")
        os.remove(destino)

    sucesso = download_file(url, destino)

    if sucesso:
        return destino
    else:
        return None
