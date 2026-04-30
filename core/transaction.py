"""Clase BankingTransaction - Modelo de datos para transacciones bancarias."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
import uuid
import random


@dataclass
class BankingTransaction:    
    transaction_types_available: ClassVar[tuple] = ("DEPOSITO", "RETIRO", "TRANSFERENCIA")
    
    transaction_id: str
    account_number: str
    transaction_type: str
    amount: float
    timestamp: datetime
    status: str = "COMPLETADA"
    description: str = ""
    
    @staticmethod
    def generate_random() -> "BankingTransaction":
        transaction_id = str(uuid.uuid4())[:8].upper()
        account_number = f"CUENTA{random.randint(100000, 999999)}"
        transaction_type = random.choice(BankingTransaction.transaction_types_available)
        amount = round(random.uniform(100.0, 5000.0), 2)
        timestamp = datetime.now()
        
        descriptions = {
            "DEPOSITO": "Depósito en ventanilla",
            "RETIRO": "Retiro en cajero automático",
            "TRANSFERENCIA": "Transferencia interbancaria"
        }
        description = descriptions.get(transaction_type, "")
        
        return BankingTransaction(
            transaction_id=transaction_id,
            account_number=account_number,
            transaction_type=transaction_type,
            amount=amount,
            timestamp=timestamp,
            status="COMPLETADA",
            description=description
        )
    
    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "account_number": self.account_number,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BankingTransaction":
        
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
    
    def __str__(self) -> str:
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"{self.transaction_type:15} ${self.amount:>10.2f} | "
            f"Cuenta: {self.account_number} | "
            f"ID: {self.transaction_id}"
        )