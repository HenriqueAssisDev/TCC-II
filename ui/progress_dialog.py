# ui/progress_dialog.py
"""
Janela de progresso para downloads do Integrador Receita.
Design elegante e profissional, compatível com o tema do sistema.
"""

import tkinter as tk
from tkinter import ttk
import math

class ProgressDialog:
    """Janela modal de progresso para downloads com design profissional."""

    def __init__(self, parent, title="Download em andamento", program_name="Programa"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("520x220")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#f8f9fa")

        # Centralizar na tela
        self._center_window()
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes("-topmost", True)

        # Variáveis de estado
        self.progress_var = tk.DoubleVar(value=0)
        self.status_text = tk.StringVar(value="Iniciando download...")
        self.speed_text = tk.StringVar(value="")
        self.time_remaining = tk.StringVar(value="")

        # Configurar estilo
        self._configure_style()

        # Criar interface
        self._create_widgets(program_name)

        # Impedir fechamento manual
        self.dialog.protocol("WM_DELETE_WINDOW", self._prevent_close)

    def _center_window(self):
        """Centraliza a janela na tela."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_style(self):
        """Configura o estilo da janela de progresso."""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo da barra de progresso
        style.configure(
            "Custom.TProgressbar",
            thickness=25,
            troughcolor="#e9ecef",
            background="#0078d4",
            borderwidth=0,
            lightcolor="#005a9e",
            darkcolor="#005a9e"
        )

        # Estilo dos labels
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), foreground="#2c3e50")
        style.configure("Status.TLabel", font=("Segoe UI", 10), foreground="#34495e")
        style.configure("Info.TLabel", font=("Segoe UI", 9), foreground="#7f8c8d")

    def _create_widgets(self, program_name):
        """Cria todos os widgets da interface."""
        # Frame principal com padding
        main_frame = ttk.Frame(self.dialog, padding="25 20 25 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título do programa
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(
            title_frame,
            text=f"Baixando: {program_name}",
            style="Title.TLabel"
        ).pack(anchor=tk.W)

        # Subtítulo
        ttk.Label(
            main_frame,
            text="Aguarde o download ser concluído...",
            style="Status.TLabel",
            foreground="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 15))

        # Barra de progresso
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            style="Custom.TProgressbar",
            length=470
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))

        # Frame de informações
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X)

        # Porcentagem e status
        self.status_label = ttk.Label(
            info_frame,
            textvariable=self.status_text,
            style="Status.TLabel",
            foreground="#495057"
        )
        self.status_label.pack(anchor=tk.W)

        # Velocidade e tempo restante
        info_row = ttk.Frame(info_frame)
        info_row.pack(fill=tk.X, pady=(5, 0))

        self.speed_label = ttk.Label(
            info_row,
            textvariable=self.speed_text,
            style="Info.TLabel"
        )
        self.speed_label.pack(side=tk.LEFT)

        self.time_label = ttk.Label(
            info_row,
            textvariable=self.time_remaining,
            style="Info.TLabel"
        )
        self.time_label.pack(side=tk.RIGHT)

        # Label de status final
        self.final_status = ttk.Label(
            main_frame,
            text="",
            style="Status.TLabel",
            foreground="#28a745"
        )
        self.final_status.pack(anchor=tk.W, pady=(10, 0))

    def _prevent_close(self):
        """Impede o fechamento manual da janela."""
        pass

    def update_progress(self, progress: int, downloaded_mb: float, total_mb: float, 
                       download_speed: float = 0, start_time: float = None):
        """
        Atualiza o progresso do download.

        Args:
            progress: Porcentagem (0-100)
            downloaded_mb: MB baixados
            total_mb: MB totais
            download_speed: Velocidade em MB/s
            start_time: Timestamp do início do download
        """
        self.progress_var.set(progress)
        self.status_text.set(f"{progress}% - {downloaded_mb:.1f} MB de {total_mb:.1f} MB")

        # Calcular velocidade e tempo restante
        if download_speed > 0 and start_time:
            elapsed = time.time() - start_time
            if elapsed > 0:
                actual_speed = downloaded_mb / elapsed
                remaining_mb = total_mb - downloaded_mb
                remaining_seconds = remaining_mb / actual_speed if actual_speed > 0 else 0

                # Atualizar velocidade
                self.speed_text.set(f"Velocidade: {actual_speed:.1f} MB/s")

                # Calcular tempo restante
                if remaining_seconds > 60:
                    minutes = int(remaining_seconds // 60)
                    seconds = int(remaining_seconds % 60)
                    self.time_remaining.set(f"Tempo restante: {minutes:02d}:{seconds:02d}")
                else:
                    self.time_remaining.set(f"Tempo restante: {int(remaining_seconds)}s")

        self.dialog.update_idletasks()

    def set_final_status(self, message: str, success: bool = True):
        """Define o status final após concluir o download."""
        color = "#28a745" if success else "#dc3545"
        self.final_status.config(text=message, foreground=color)
        self.status_text.set("Download concluído!")
        self.progress_var.set(100)
        self.dialog.update_idletasks()

    def close(self):
        """Fecha a janela de progresso."""
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except tk.TclError:
            pass

    def is_visible(self) -> bool:
        """Verifica se a janela está visível."""
        return self.dialog.winfo_exists() == '1'