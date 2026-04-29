# Simulador de Transacciones Bancarias con Apache Kafka

Sistema de simulación para actividad universitaria de Bases de Datos Masivas. Un productor genera transacciones bancarias cada segundo y un consumidor las procesa en tiempo real mediante Apache Kafka usando kafka-python.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Productor      │     │   Kafka Broker   │     │   Consumidor    │
│   (Genera TX)    │────▶│   (ZooKeeper)    │────▶│   (Procesa TX)  │
│                 │     │   puerto 9092   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │   Interfaz GUI   │
                                                │   (Tkinter)      │
                                                └─────────────────┘
```

## Estructura del Proyecto

```
kafka-banking-sim/
├── docker-compose.yml    # Infraestructura Kafka
├── requirements.txt      # Dependencias Python
├── main.py               # Punto de entrada
├── README.md            # Este archivo
│
├── config/
│   └── __init__.py      # Configuración centralizada
│
├── core/
│   ├── __init__.py
│   ├── transaction.py   # Modelo BankingTransaction
│   ├── producer.py      # Clase TransactionProducer
│   └── consumer.py      # Clase TransactionConsumer
│
└── gui/
    ├── __init__.py
    └── app.py           # Interfaz Tkinter
```

## Requisitos

- **Docker** y **Docker Compose** instalados
- **Python 3.8+** con pip
- **Git** (opcional, para clonar)

## Pasos de Implementación

### 1. Levantar Infraestructura Kafka

```bash
# Navegar al directorio del proyecto
cd kafka-banking-sim

# Levantar servicios (ZooKeeper + Kafka)
docker-compose up -d

# Verificar que los servicios estén corriendo
docker-compose ps

# Ver logs de Kafka (esperar mensaje "started")
docker-compose logs -f kafka
```

**Nota:** Espere aproximadamente 30 segundos antes de continuar, hasta que Kafka esté completamente iniciado.

### 2. Instalar Dependencias Python

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows (Git Bash/MSYS):
source venv/Scripts/activate
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación

```bash
python main.py
```

## Uso de la Aplicación

1. **Iniciar Simulación**: Presione el botón verde "▶ Iniciar Simulación"
2. **Observar**: Las transacciones aparecerán en tiempo real en el área de texto
3. **Detener**: Presione el botón "■ Detener Simulación"
4. **Limpiar**: Borra el área de texto

## Tipos de Transacciones

| Tipo | Descripción | Color en GUI |
|------|-------------|--------------|
| DEPOSITO | Depósito en cuenta | Verde |
| RETIRO | Retiro en cajero | Naranja |
| TRANSFERENCIA | Transferencia interbancaria | Azul |

## Validación del Entorno

### Verificar Kafka (opcional)

```bash
# Crear topic manualmente
docker exec kafka kafka-topics --create --topic banking-transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Listar topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Ver detalles del topic
docker exec kafka kafka-topics --describe --topic banking-transactions --bootstrap-server localhost:9092
```

### Probar Productor y Consumidor por Consola

```bash
# Terminal 1: Crear consumidor
docker exec -it kafka kafka-console-consumer --topic banking-transactions --from-beginning --bootstrap-server localhost:9092

# Terminal 2: Enviar mensaje de prueba
docker exec -it kafka kafka-console-producer --topic banking-transactions --broker-list localhost:9092
```

## Principios POO Aplicados

### Encapsulamiento
- Atributos privados con `_` prefix
- Métodos de acceso controlados
- Interface limpia hacia el exterior

### Herencia y Polimorfismo
- Patrones de diseño (Producer, Observer, Factory)
- Callbacks configurables

### Composición
- `BankingGUI` composa `TransactionProducer` y `TransactionConsumer`
- Desacoplamiento de responsabilidades

### Gestión de Recursos
- Context managers (`__enter__`, `__exit__`)
- Limpieza en cierres (`stop()`, `_cleanup()`)
- Hilos daemon para no bloquear el cierre

## Excepciones y Manejo de Errores

- Errores de conexión Kafka
- Mensajes corruptos o malformados
- Cierre forzado de ventanas
- Timeouts en operaciones de red

## Extensiones Sugeridas

### Nivel Básico
- [ ] Modificar velocidad de generación (intervalo configurable)
- [ ] Añadir más tipos de transacciones

### Nivel Intermedio
- [ ] Persistir transacciones en SQLite
- [ ] Añadir validación de saldo suficiente
- [ ] Gráficos de estadísticas en tiempo real

### Nivel Avanzado
- [ ] Implementar exactamente-una-vez (EOS)
- [ ] Usar Avro con Schema Registry
- [ ] Añadir múltiples particiones
- [ ] Cluster Kafka con múltiples brokers

## Detener el Entorno

```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v

# Desactivar entorno virtual
deactivate
```

## Solución de Problemas

### Kafka no inicia
```bash
# Ver logs detallados
docker-compose logs kafka

# Reiniciar servicios
docker-compose restart
```

### Error de conexión
- Verificar que Kafka esté en puerto 9092
- Verificar que ZooKeeper responda en 2181

### Error de permisos
```bash
# En Linux, puede necesitar permisos
sudo chown -R $USER:$USER kafka-banking-sim/
```

## Créditos

Actividad diseñada para el curso de **Bases de Datos Masivas**.
Universidad: UniMinuto

## Licencia

MIT License