"""
Simulador de Transacciones Bancarias con Apache Kafka.

Punto de entrada principal de la aplicación.
Actividad universitaria para Bases de Datos Masivas.

Uso:
    python main.py

Requisitos:
    - Docker y Docker Compose instalados
    - Python 3.8+
    - Ejecutar 'docker-compose up -d' antes de iniciar
"""

import sys
import tkinter as tk
from gui.app import create_app


def check_python_version() -> bool:
    """
    Verifica que la versión de Python sea compatible.
    
    Returns:
        bool: True si es compatible
    """
    if sys.version_info < (3, 8):
        print("ERROR: Se requiere Python 3.8 o superior")
        print(f"Versión actual: {sys.version}")
        return False
    return True


def main() -> None:
    """
    Punto de entrada principal de la aplicación.
    """
    if not check_python_version():
        sys.exit(1)
    
    print("=" * 60)
    print("  Simulador de Transacciones Bancarias - Apache Kafka")
    print("  Actividad: Bases de Datos Masivas")
    print("=" * 60)
    print()
    print("Iniciando interfaz gráfica...")
    print()
    
    try:
        app = create_app()
        print("Interfaz iniciada correctamente")
        print("Presione 'Iniciar Simulación' para comenzar")
        print()
        app.root.mainloop()
        
    except tk.TclError as e:
        print(f"ERROR: No se pudo iniciar la interfaz gráfica")
        print(f"Detalles: {e}")
        print()
        print("Asegúrese de tener un entorno gráfico disponible")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario")
        sys.exit(0)
    
    except Exception as e:
        print(f"ERROR: Fallo inesperado")
        print(f"Detalles: {e}")
        sys.exit(1)
    
    print()
    print("Aplicación finalizada")


if __name__ == "__main__":
    main()