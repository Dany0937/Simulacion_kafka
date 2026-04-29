"""Clase TransactionProducer - Generador de transacciones hacia Kafka."""

from kafka import KafkaProducer
from typing import Callable, Optional
import json
import time
import threading
from core.transaction import BankingTransaction


class TransactionProducer:
    """
    Productor de transacciones bancarias hacia Apache Kafka.
    
    Implementa el patrón de diseño Producer para enviar mensajes
    a un topic de Kafka de forma continua.
    
    Attributes:
        bootstrap_servers: Servidores Kafka para conexión
        topic: Topic de destino
        producer: Instancia del productor de confluent-kafka
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "banking-transactions"
    ):
        """
        Inicializa el productor de transacciones.
        
        Args:
            bootstrap_servers: Dirección del broker Kafka
            topic: Nombre del topic donde publicar
        """
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8'),
            linger_ms=10,
            acks='all'
        )
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_send_callback: Optional[Callable[[BankingTransaction], None]] = None
    
    @property
    def topic(self) -> str:
        """Topic de destino."""
        return self._topic
    
    @property
    def is_running(self) -> bool:
        """Verifica si el productor está activo."""
        return self._running
    
    def set_on_send_callback(self, callback: Callable[[BankingTransaction], None]) -> None:
        """
        Establece un callback para ejecutar después de cada envío.
        
        Args:
            callback: Función a ejecutar con la transacción enviada
        """
        self._on_send_callback = callback
    
    def start_producing(self) -> None:
        """
        Inicia la generación continua de transacciones.
        Cada transacción se genera con un intervalo de 1 segundo.
        """
        self._running = True
        
        print(f"[PRODUCER] Iniciando productor -> Topic: {self._topic}")
        print("[PRODUCER] Generando transacciones cada 1 segundo...")
        
        while self._running:
            try:
                transaction = BankingTransaction.generate_random()
                
                self._producer.send(
                    topic=self._topic,
                    value=transaction.to_dict(),
                    key=transaction.transaction_id
                )
                
                if self._on_send_callback:
                    self._on_send_callback(transaction)
                
                print(f"[PRODUCER] Enviada: {transaction}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"[PRODUCER ERROR] Error en generación: {e}")
                time.sleep(1)
        
        print("[PRODUCER] Productor detenido")
    
    def start_async(self) -> None:
        """Inicia el productor en un hilo separado."""
        if self._thread is not None and self._thread.is_alive():
            print("[PRODUCER] El productor ya está en ejecución")
            return
        
        self._thread = threading.Thread(
            target=self.start_producing,
            daemon=True,
            name="KafkaProducerThread"
        )
        self._thread.start()
        print(f"[PRODUCER] Hilo iniciado: {self._thread.name}")
    
    def stop(self) -> None:
        """Detiene el productor de forma segura."""
        print("[PRODUCER] Deteniendo productor...")
        self._running = False
        
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        
        self._producer.flush(timeout=5.0)
        print("[PRODUCER] Productor detenido exitosamente")
    
    def send_transaction(self, transaction: BankingTransaction) -> None:
        """
        Envía una transacción específica inmediatamente.
        
        Args:
            transaction: Transacción a enviar
        """
        self._producer.send(
            topic=self._topic,
            value=transaction.to_dict(),
            key=transaction.transaction_id
        )
    
    def __enter__(self) -> "TransactionProducer":
        """ Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """ Cierra recursos al salir del context manager."""
        self.stop()