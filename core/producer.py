from kafka import KafkaProducer
from typing import Callable, Optional
import json
import time
import threading
from core.transaction import BankingTransaction


class TransactionProducer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "banking-transactions"
    ):
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
        return self._topic
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def set_on_send_callback(self, callback: Callable[[BankingTransaction], None]) -> None:
        self._on_send_callback = callback
    
    def start_producing(self) -> None:
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
        print("[PRODUCER] Deteniendo productor...")
        self._running = False
        
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        
        self._producer.flush(timeout=5.0)
        print("[PRODUCER] Productor detenido exitosamente")
    
    def send_transaction(self, transaction: BankingTransaction) -> None:
        self._producer.send(
            topic=self._topic,
            value=transaction.to_dict(),
            key=transaction.transaction_id
        )
    
    def __enter__(self) -> "TransactionProducer":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()