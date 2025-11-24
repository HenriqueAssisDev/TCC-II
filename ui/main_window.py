# ui/main_window.py
"""
Interface gráfica principal do Integrador Receita.
Exibe lista de programas, status e botões de ação.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from core.programs_registry import (
    get_program_list,
    get_all_programs_status,
    is_program_installed,
    run_program,
)
from core.updater import download_and_install, updater
from core.logger import log_info, log_error


def create_main_window():
    """
    Cria e retorna a janela principal do aplicativo.

    Returns:
        tk.Tk: Janela principal configurada
    """
    root = tk.Tk()
    root.title("Integrador Receita - Gerenciador de Programas da Receita Federal")
    root.geometry("1200x700")
    root.resizable(True, True)

    # Configuração de estilo
    style = ttk.Style()
    style.theme_use("clam")

    # Cores personalizadas
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=30,
        fieldbackground="white",
        font=("Segoe UI", 11),
    )
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 12, "bold"),
        background="#0066cc",
        foreground="white",
    )
    style.map("Treeview", background=[("selected", "#0066cc")])

    # Frame principal
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    title_label = tk.Label(
        main_frame,
        text="Gerenciador de Programas da Receita Federal",
        font=("Segoe UI", 18, "bold"),
        fg="#0066cc",
    )
    title_label.pack(pady=(0, 15))

    # Frame da tabela
    table_frame = ttk.Frame(main_frame)
    table_frame.pack(fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Treeview (tabela)
    columns = ("Programa", "Status", "Versão Local", "Versão Disponível", "Ações")
    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        yscrollcommand=scrollbar.set,
        height=15,
    )
    scrollbar.config(command=tree.yview)
    tree.pack(fill=tk.BOTH, expand=True)

    # Configuração das colunas
    tree.heading("Programa", text="Programa")
    tree.heading("Status", text="Status")
    tree.heading("Versão Local", text="Versão Local")
    tree.heading("Versão Disponível", text="Versão Disponível")
    tree.heading("Ações", text="Ações")

    tree.column("Programa", width=300, anchor=tk.W)
    tree.column("Status", width=150, anchor=tk.CENTER)
    tree.column("Versão Local", width=150, anchor=tk.CENTER)
    tree.column("Versão Disponível", width=150, anchor=tk.CENTER)
    tree.column("Ações", width=200, anchor=tk.CENTER)

    # Preencher tabela com dados
    def refresh_table():
        """Atualiza a tabela com os dados mais recentes."""
        tree.delete(*tree.get_children())
        programs = get_program_list()

        for program in programs:
            tree.insert(
                "",
                tk.END,
                values=(
                    program["nome"],
                    program["status"],
                    program["versao_local"],
                    program["versao_disponivel"],
                    "Clique para ações",
                ),
                tags=(program["id"],),
            )

        log_info(f"[UI] Tabela atualizada com {len(programs)} programas")

    # Função de atualização de um programa
    def update_program(program_id: str):
        """
        Baixa e instala um programa específico.

        Args:
            program_id (str): ID do programa a ser atualizado
        """
        def download_thread():
            try:
                log_info(f"[UI] Iniciando download de {program_id}")
                messagebox.showinfo(
                    "Download Iniciado",
                    f"Download de {program_id} iniciado.\nAguarde...",
                )

                success, message = download_and_install(program_id)

                if success:
                    messagebox.showinfo("Sucesso", message)
                    log_info(f"[UI] {program_id} atualizado com sucesso")
                else:
                    messagebox.showerror("Erro", message)
                    log_error(f"[UI] Erro ao atualizar {program_id}: {message}")

                # Atualiza a tabela após download
                root.after(0, refresh_table)

            except Exception as e:
                log_error(f"[UI] Erro inesperado ao atualizar {program_id}: {e}")
                messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

        # Executa download em thread separada para não travar a interface
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    # Função de verificação de atualizações
    def check_updates():
        """Verifica atualizações disponíveis para todos os programas."""
        try:
            log_info("[UI] Verificando atualizações...")
            updates = updater.check_for_updates()

            available = sum(updates.values())

            if available > 0:
                programs_list = "\n".join(
                    [f"• {pid}" for pid, needs in updates.items() if needs]
                )
                messagebox.showinfo(
                    "Atualizações Disponíveis",
                    f"{available} programa(s) com atualizações disponíveis:\n\n{programs_list}",
                )
            else:
                messagebox.showinfo(
                    "Sem Atualizações",
                    "Todos os programas estão atualizados!",
                )

            refresh_table()

        except Exception as e:
            log_error(f"[UI] Erro ao verificar atualizações: {e}")
            messagebox.showerror("Erro", f"Erro ao verificar atualizações: {str(e)}")

    # Evento de clique duplo na tabela
    def on_double_click(event):
        """Ação ao clicar duas vezes em um programa."""
        selection = tree.selection()
        if not selection:
            return

        item = tree.item(selection[0])
        program_id = item["tags"][0] if item["tags"] else None
        if not program_id:
            return

        nome = item["values"][0]
        status = item["values"][1]

        # Se instalado, executa direto
        if status == "Instalado":
            ok = run_program(program_id)
            if not ok:
                messagebox.showerror(
                    "Erro ao executar",
                    f"Não foi possível abrir {nome}.\nVerifique se o atalho ou executável existe.",
                )
            return

        # Se não instalado, pergunta se quer baixar
        resposta = messagebox.askyesno(
            "Baixar/Atualizar",
            f"{nome} não está instalado.\n\nDeseja baixar/instalar agora?",
        )
        if resposta:
            update_program(program_id)

    tree.bind("<Double-1>", on_double_click)

    # Frame de botões inferiores
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(15, 0))

    # Botões
    btn_refresh = tk.Button(
        button_frame,
        text="🔄 Atualizar Lista",
        command=refresh_table,
        font=("Segoe UI", 12, "bold"),
        bg="#0066cc",
        fg="white",
        padx=20,
        pady=10,
        relief=tk.RAISED,
        cursor="hand2",
    )
    btn_refresh.pack(side=tk.LEFT, padx=5)

    btn_check_updates = tk.Button(
        button_frame,
        text="🔍 Verificar Atualizações",
        command=check_updates,
        font=("Segoe UI", 12, "bold"),
        bg="#28a745",
        fg="white",
        padx=20,
        pady=10,
        relief=tk.RAISED,
        cursor="hand2",
    )
    btn_check_updates.pack(side=tk.LEFT, padx=5)

    btn_exit = tk.Button(
        button_frame,
        text="❌ Sair",
        command=root.quit,
        font=("Segoe UI", 12, "bold"),
        bg="#dc3545",
        fg="white",
        padx=20,
        pady=10,
        relief=tk.RAISED,
        cursor="hand2",
    )
    btn_exit.pack(side=tk.RIGHT, padx=5)

    # Preenche a tabela na inicialização
    refresh_table()

    log_info("[UI] Interface gráfica criada com sucesso")

    return root


if __name__ == "__main__":
    # Teste da interface
    root = create_main_window()
    root.mainloop()