"""Aplicación GUI con Tkinter para simulación bancaria."""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from typing import Optional
import threading
from core.producer import TransactionProducer
from core.consumer import TransactionConsumer
from core.transaction import BankingTransaction
from config import CONFIG, KAFKA_CONFIG


class BankingGUI:
    """
    Interfaz gráfica principal para el simulador de transacciones.
    
    Proporciona una ventana con controles para iniciar/detener
    el productor y consumidor de Kafka, mostrando las transacciones
    en tiempo real.
    
    Attributes:
        root: Ventana principal de Tkinter
        producer: Instancia del productor
        consumer: Instancia del consumidor
    """
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.producer: Optional[TransactionProducer] = None
        self.consumer: Optional[TransactionConsumer] = None
        self._transactions_displayed = 0
        
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()
    
    def _setup_window(self) -> None:
        """Configura las propiedades de la ventana."""
        self.root.title(CONFIG.app_title)
        self.root.geometry(f"{CONFIG.window_width}x{CONFIG.window_height}")
        self.root.minsize(600, 400)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_styles(self) -> None:
        """Configura estilos.ttk para widgets."""
        self.style = ttk.Style()
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 12, "bold")
        )
        self.style.configure(
            "Stats.TLabel",
            font=("Helvetica", 10),
            foreground="#333333"
        )
        self.style.configure(
            "Control.TButton",
            font=("Helvetica", 10, "bold"),
            padding=(20, 10)
        )
    
    def _create_widgets(self) -> None:
        """Crea todos los widgets de la interfaz."""
        self._create_header()
        self._create_control_panel()
        self._create_text_area()
        self._create_status_bar()
        self._create_stats_panel()
    
    def _create_header(self) -> None:
        """Crea el panel de encabezado."""
        self.header_frame = ttk.Frame(self.root)
        
        self.title_label = ttk.Label(
            self.header_frame,
            text="Apache Kafka - Simulador de Transacciones Bancarias",
            style="Header.TLabel"
        )
        
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text=f"Topic: {KAFKA_CONFIG.topic} | "
            f"Broker: {KAFKA_CONFIG.bootstrap_servers}"
        )
    
    def _create_control_panel(self) -> None:
        """Crea el panel de control con botones."""
        self.control_frame = ttk.LabelFrame(
            self.root,
            text="Control de Simulación",
            padding=10
        )
        
        self.btn_iniciar = ttk.Button(
            self.control_frame,
            text="▶ Iniciar Simulación",
            style="Control.TButton",
            command=self._start_simulation
        )
        
        self.btn_detener = ttk.Button(
            self.control_frame,
            text="■ Detener Simulación",
            style="Control.TButton",
            command=self._stop_simulation,
            state="disabled"
        )
        
        self.btn_limpiar = ttk.Button(
            self.control_frame,
            text="🗑 Limpiar",
            command=self._clear_text
        )
    
    def _create_text_area(self) -> None:
        """Crea el área de texto para mostrar transacciones."""
        self.text_frame = ttk.Frame(self.root)
        
        self.text_area = scrolledtext.ScrolledText(
            self.text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=20,
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="white",
            relief=tk.FLAT
        )
        
        self.text_area.tag_configure(
            "deposito",
            foreground="#4CAF50"
        )
        self.text_area.tag_configure(
            "retiro",
            foreground="#FF9800"
        )
        self.text_area.tag_configure(
            "transferencia",
            foreground="#2196F3"
        )
        self.text_area.tag_configure(
            "header",
            foreground="#FFFFFF",
            font=("Consolas", 10, "bold")
        )
        
        self._insert_welcome_message()
    
    def _create_status_bar(self) -> None:
        """Crea la barra de estado."""
        self.status_frame = ttk.Frame(self.root)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Estado: Detenido",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=20,
            height=20,
            bg="red",
            highlightthickness=0
        )
        self.status_circle = self.status_indicator.create_oval(
            2, 2, 18, 18,
            fill="red",
            outline="darkred"
        )
    
    def _create_stats_panel(self) -> None:
        """Crea el panel de estadísticas."""
        self.stats_frame = ttk.Frame(self.root)
        
        self.lbl_producidas = ttk.Label(
            self.stats_frame,
            text="Producidas: 0",
            style="Stats.TLabel"
        )
        
        self.lbl_consumidas = ttk.Label(
            self.stats_frame,
            text="Consumidas: 0",
            style="Stats.TLabel"
        )
        
        self.lbl_depositos = ttk.Label(
            self.stats_frame,
            text="Depósitos: 0",
            style="Stats.TLabel"
        )
        
        self.lbl_retiros = ttk.Label(
            self.stats_frame,
            text="Retiros: 0",
            style="Stats.TLabel"
        )
        
        self.lbl_transferencias = ttk.Label(
            self.stats_frame,
            text="Transferencias: 0",
            style="Stats.TLabel"
        )
        
        self._reset_stats()
    
    def _layout_widgets(self) -> None:
        """Organiza los widgets en la ventana."""
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack()
        self.subtitle_label.pack()
        
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_detener.pack(side=tk.LEFT, padx=5)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        self.stats_frame.pack(fill=tk.X, padx=10, pady=5)
        self.lbl_producidas.pack(side=tk.LEFT, padx=10)
        self.lbl_consumidas.pack(side=tk.LEFT, padx=10)
        self.lbl_depositos.pack(side=tk.LEFT, padx=10)
        self.lbl_retiros.pack(side=tk.LEFT, padx=10)
        self.lbl_transferencias.pack(side=tk.LEFT, padx=10)
        
        self.text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    def _insert_welcome_message(self) -> None:
        """Inserta mensaje de bienvenida en el área de texto."""
        header = (
            "=" * 70 + "\n"
            "  SIMULADOR DE TRANSACCIONES BANCARIAS - APACHE KAFKA\n"
            "=" * 70 + "\n\n"
            "  Esperando inicio de simulación...\n"
            "  Presione 'Iniciar Simulación' para comenzar\n\n"
            "-" * 70 + "\n"
        )
        self.text_area.insert(tk.END, header, "header")
        self.text_area.insert(tk.END, "\n  TX Generadas    Hora          Tipo            Monto        Cuenta           ID\n")
        self.text_area.insert(tk.END, "-" * 70 + "\n")
    
    def _insert_transaction(self, tx: BankingTransaction, counter: int) -> None:
        """
        Inserta una transacción en el área de texto.
        
        Args:
            tx: Transacción a mostrar
            counter: Contador de transacciones
        """
        tag_map = {
            "DEPOSITO": "deposito",
            "RETIRO": "retiro",
            "TRANSFERENCIA": "transferencia"
        }
        tag = tag_map.get(tx.transaction_type, "header")
        
        line = (
            f"  {counter:4}    "
            f"{tx.timestamp.strftime('%H:%M:%S')}    "
            f"{tx.transaction_type:15}    "
            f"${tx.amount:>9.2f}    "
            f"{tx.account_number}    "
            f"{tx.transaction_id}\n"
        )
        
        self.text_area.insert(tk.END, line, tag)
        self.text_area.see(tk.END)
        
        self._transactions_displayed += 1
        
        if self._transactions_displayed > CONFIG.max_display_transactions:
            self._clear_text()
    
    def _update_stats(self, tx: BankingTransaction) -> None:
        """
        Actualiza las estadísticas de la UI.
        
        Args:
            tx: Transacción procesada
        """
        total_text = self.lbl_producidas.cget("text")
        total = int(total_text.split(": ")[1]) + 1
        self.lbl_producidas.config(text=f"Producidas: {total}")
        
        consumed_text = self.lbl_consumidas.cget("text")
        consumed = int(consumed_text.split(": ")[1]) + 1
        self.lbl_consumidas.config(text=f"Consumidas: {consumed}")
        
        type_counts = {
            "DEPOSITO": self.lbl_depositos,
            "RETIRO": self.lbl_retiros,
            "TRANSFERENCIA": self.lbl_transferencias
        }
        
        if tx.transaction_type in type_counts:
            label = type_counts[tx.transaction_type]
            count_text = label.cget("text")
            count = int(count_text.split(": ")[1]) + 1
            label.config(text=f"{tx.transaction_type}: {count}")
    
    def _reset_stats(self) -> None:
        """Reinicia las estadísticas a cero."""
        self.lbl_producidas.config(text="Producidas: 0")
        self.lbl_consumidas.config(text="Consumidas: 0")
        self.lbl_depositos.config(text="Depósitos: 0")
        self.lbl_retiros.config(text="Retiros: 0")
        self.lbl_transferencias.config(text="Transferencias: 0")
    
    def _set_status(self, status: str, running: bool) -> None:
        """
        Actualiza el estado de la aplicación.
        
        Args:
            status: Texto de estado
            running: Indica si está en ejecución
        """
        self.status_label.config(text=f"Estado: {status}")
        
        color = "green" if running else "red"
        self.status_indicator.itemconfig(self.status_circle, fill=color)
    
    def _producer_callback(self, tx: BankingTransaction) -> None:
        """
        Callback ejecutado después de enviar una transacción.
        
        Args:
            tx: Transacción enviada
        """
        self.root.after(0, self._update_stats, tx)
    
    def _consumer_callback(self, tx: BankingTransaction) -> None:
        """
        Callback ejecutado al recibir una transacción.
        
        Args:
            tx: Transacción recibida
        """
        self._transactions_displayed += 1
        self.root.after(0, self._insert_transaction, tx, self._transactions_displayed)
    
    def _start_simulation(self) -> None:
        """Inicia la simulación de productor y consumidor."""
        try:
            self.btn_iniciar.config(state="disabled")
            self.btn_detener.config(state="normal")
            
            self.producer = TransactionProducer(
                bootstrap_servers=KAFKA_CONFIG.bootstrap_servers,
                topic=KAFKA_CONFIG.topic
            )
            self.producer.set_on_send_callback(self._producer_callback)
            self.producer.start_async()
            
            self.consumer = TransactionConsumer(
                bootstrap_servers=KAFKA_CONFIG.bootstrap_servers,
                topic=KAFKA_CONFIG.topic,
                group_id=KAFKA_CONFIG.group_id
            )
            self.consumer.set_on_message_callback(self._consumer_callback)
            self.consumer.start_async()
            
            self._set_status("Simulación Activa", True)
            
            print("[GUI] Simulación iniciada")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la simulación:\n{e}")
            self._stop_simulation()
    
    def _stop_simulation(self) -> None:
        """Detiene la simulación."""
        try:
            self.btn_iniciar.config(state="normal")
            self.btn_detener.config(state="disabled")
            
            if self.producer:
                self.producer.stop()
                self.producer = None
            
            if self.consumer:
                self.consumer.stop()
                self.consumer = None
            
            self._set_status("Detenido", False)
            print("[GUI] Simulación detenida")
            
        except Exception as e:
            print(f"[GUI ERROR] Error al detener: {e}")
    
    def _clear_text(self) -> None:
        """Limpia el área de texto."""
        self.text_area.delete(1.0, tk.END)
        self._insert_welcome_message()
        self._transactions_displayed = 0
    
    def _on_close(self) -> None:
        """Maneja el evento de cierre de la ventana."""
        self._stop_simulation()
        self.root.destroy()


def create_app() -> BankingGUI:
    """
    Función factory para crear la aplicación.
    
    Returns:
        BankingGUI: Instancia de la interfaz gráfica
    """
    root = tk.Tk()
    app = BankingGUI(root)
    return app


def run_app() -> None:
    """Ejecuta la aplicación principal."""
    root = tk.Tk()
    app = BankingGUI(root)
    root.mainloop()