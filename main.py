# main.py
"""
Ponto de entrada principal do Integrador Receita.
Inicializa o sistema e abre a interface gráfica.
"""

import sys
import os

# Adiciona o diretório raiz ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import log_startup, log_info, log_error
from core.paths import ensure_directories
from ui.main_window import create_main_window


def main():
    """
    Função principal do aplicativo.
    Inicializa o sistema e abre a interface gráfica.
    """
    try:
        # Registra inicialização do sistema
        log_startup()

        # Garante que todas as pastas necessárias existem
        log_info("[MAIN] Garantindo estrutura de pastas...")
        ensure_directories()

        # Cria e exibe a janela principal
        log_info("[MAIN] Criando interface gráfica...")
        root = create_main_window()

        # Inicia o loop da interface
        log_info("[MAIN] Iniciando aplicação...")
        root.mainloop()

        log_info("[MAIN] Aplicação encerrada normalmente")

    except Exception as e:
        log_error(f"[MAIN] Erro crítico ao iniciar aplicação: {e}")
        import traceback
        log_error(f"[MAIN] Traceback completo:\n{traceback.format_exc()}")

        # Tenta mostrar erro na interface (se possível)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Erro Crítico",
                f"Erro ao iniciar o Integrador Receita:\n\n{str(e)}\n\n"
                f"Verifique o arquivo de log em logs/app.log para mais detalhes."
            )
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()