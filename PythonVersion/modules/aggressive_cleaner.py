"""
Modo AGRESSIVO de limpeza de Standby Cache
Limpa periodicamente, não só quando threshold é atingido
"""
import time
import threading
from modules.standby_cleaner import StandbyMemoryCleaner

class AggressiveStandbyCleaner(StandbyMemoryCleaner):
    def __init__(self, clean_interval_seconds=30):
        """
        clean_interval_seconds: Limpa a cada X segundos (padrão: 30s)
        """
        super().__init__(threshold_mb=0, check_interval=clean_interval_seconds)
        self.clean_interval = clean_interval_seconds
        
    def _monitoring_loop(self):
        """Loop que limpa periodicamente SEMPRE"""
        print(f"[AGGRESSIVE] Limpeza periódica ativa: a cada {self.clean_interval}s")
        
        while self.running:
            try:
                # Limpa SEMPRE, não verifica threshold
                freed_mb = self.clean_standby_memory()
                
                if freed_mb > 0:
                    print(f"[CLEAN] Liberado: {freed_mb}MB | "
                          f"Total limpezas: {self.clean_count}")
                else:
                    print(f"[CLEAN] Cache já estava limpo")
                
                time.sleep(self.clean_interval)
            except Exception as e:
                print(f"[ERROR] Erro: {e}")
                time.sleep(10)


if __name__ == "__main__":
    # Teste: limpa a cada 10 segundos
    cleaner = AggressiveStandbyCleaner(clean_interval_seconds=10)
    cleaner.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleaner.stop()
        print("\n[INFO] Finalizado")
