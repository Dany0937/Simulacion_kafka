"""Clase TransactionConsumer - Consumidor de transacciones desde Kafka."""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from typing import Callable, Optional, List
import json
import threading
from core.transaction import BankingTransaction


class TransactionConsumer:
    """
    Consumidor de transacciones bancarias desde Apache Kafka.
    
    Implementa el patrón de diseño Observer para procesar
    mensajes de un topic de Kafka en tiempo real.
    
    Attributes:
        bootstrap_servers: Servidores Kafka para conexión
        topic: Topic de origen
        group_id: Identificador del grupo de consumidores
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "banking-transactions",
        group_id: str = "banking-consumer-group"
    ):
        """
        Inicializa el consumidor de transacciones.
        
        Args:
            bootstrap_servers: Dirección del broker Kafka
            topic: Nombre del topic a consumir
            group_id: Identificador del grupo de consumidores
        """
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._group_id = group_id
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_message_callback: Optional[Callable[[BankingTransaction], None]] = None
        self._transactions_received: List[BankingTransaction] = []
    
    @property
    def topic(self) -> str:
        """Topic de origen."""
        return self._topic
    
    @property
    def is_running(self) -> bool:
        """Verifica si el consumidor está activo."""
        return self._running
    
    @property
    def transactions_count(self) -> int:
        """Cantidad de transacciones recibidas."""
        return len(self._transactions_received)
    
    def set_on_message_callback(self, callback: Callable[[BankingTransaction], None]) -> None:
        """
        Establece un callback para procesar cada mensaje recibido.
        
        Args:
            callback: Función a ejecutar con cada transacción
        """
        self._on_message_callback = callback
    
    def _create_consumer(self) -> KafkaConsumer:
        """
        Crea y configura el consumidor de Kafka.
        
        Returns:
            Consumer: Instancia configurada del consumidor
        """
        return KafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers.split(','),
            group_id=self._group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
    
    def start_consuming(self) -> None:
        """
        Inicia el consumo continuo de transacciones.
        Procesa mensajes del topic hasta que se detenga.
        """
        self._consumer = self._create_consumer()
        self._running = True
        
        print(f"[CONSUMER] Consumidor iniciado -> Topic: {self._topic}")
        print("[CONSUMER] Esperando transacciones...")
        
        try:
            for msg in self._consumer:
                if not self._running:
                    break
                self._process_message(msg)
        except Exception as e:
            print(f"[CONSUMER ERROR] Excepción: {e}")
        finally:
            self._cleanup()
        
        print("[CONSUMER] Consumidor detenido")
    
    def _process_message(self, msg) -> None:
        """
        Procesa un mensaje recibido de Kafka.
        
        Args:
            msg: Mensaje recibido
        """
        try:
            value = msg.value
            if value is None:
                return
            
            data = json.loads(value.decode("utf-8"))
            transaction = BankingTransaction.from_dict(data)
            
            self._transactions_received.append(transaction)
            
            print(f"[CONSUMER] Recibida: {transaction}")
            
            if self._on_message_callback:
                self._on_message_callback(transaction)
            
        except json.JSONDecodeError as e:
            print(f"[CONSUMER ERROR] Error al decodificar JSON: {e}")
        except Exception as e:
            print(f"[CONSUMER ERROR] Error al procesar mensaje: {e}")
    
    def _cleanup(self) -> None:
        """Limpia recursos del consumidor."""
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
    
    def start_async(self) -> None:
        """Inicia el consumidor en un hilo separado."""
        if self._thread is not None and self._thread.is_alive():
            print("[CONSUMER] El consumidor ya está en ejecución")
            return
        
        self._thread = threading.Thread(
            target=self.start_consuming,
            daemon=True,
            name="KafkaConsumerThread"
        )
        self._thread.start()
        print(f"[CONSUMER] Hilo iniciado: {self._thread.name}")
    
    def stop(self) -> None:
        """Detiene el consumidor de forma segura."""
        print("[CONSUMER] Deteniendo consumidor...")
        self._running = False
        
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        
        self._cleanup()
        print("[CONSUMER] Consumidor detenido exitosamente")
    
    def __enter__(self) -> "TransactionConsumer":
        """Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cierra recursos al salir del context manager."""
        self.stop()
