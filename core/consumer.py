from kafka import KafkaConsumer
from kafka.errors import KafkaError
from typing import Callable, Optional, List
import json
import threading
from core.transaction import BankingTransaction

class TransactionConsumer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "banking-transactions",
        group_id: str = "banking-consumer-group"
    ):
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
        return self._topic
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    @property
    def transactions_count(self) -> int:
        return len(self._transactions_received)
    
    def set_on_message_callback(self, callback: Callable[[BankingTransaction], None]) -> None:
        self._on_message_callback = callback
    
    def _create_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers.split(','),
            group_id=self._group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
    
    def start_consuming(self) -> None:
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
        print("[CONSUMER] Deteniendo consumidor...")
        self._running = False
        
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        
        self._cleanup()
        print("[CONSUMER] Consumidor detenido exitosamente")
    
    def __enter__(self) -> "TransactionConsumer":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
