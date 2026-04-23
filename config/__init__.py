"""Módulo de configuración centralizada."""

from dataclasses import dataclass


@dataclass
class KafkaConfig:
    """Configuración para conexión con Apache Kafka."""
    
    bootstrap_servers: str = "localhost:9092"
    topic: str = "banking-transactions"
    group_id: str = "banking-consumer-group"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 1000


@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    
    app_title: str = "Simulador de Transacciones Bancarias - Kafka"
    window_width: int = 800
    window_height: int = 600
    transactions_per_second: int = 1
    max_display_transactions: int = 100


@dataclass
class TransactionConfig:
    """Configuración para generación de transacciones."""
    
    account_prefix: str = "CUENTA"
    min_amount: float = 10.0
    max_amount: float = 10000.0
    transaction_types: tuple = ("DEPOSITO", "RETIRO", "TRANSFERENCIA")


CONFIG = AppConfig()
KAFKA_CONFIG = KafkaConfig()
TRANSACTION_CONFIG = TransactionConfig()