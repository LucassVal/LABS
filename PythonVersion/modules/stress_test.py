"""
Stress Test controlado de CPU
"""
import threading
import time
import math
import multiprocessing
import psutil

class CPUStressTest:
    def __init__(self):
        self.running = False
        self.target_load = 0
        self.threads = []
        self.thread_count = 0
        
    def start(self, target_load_percent=70, thread_count=0):
        """Inicia stress test com carga específica"""
        if self.running:
            print("[WARN] Stress test já está rodando")
            return
        
        if not (10 <= target_load_percent <= 100):
            print(f"[ERROR] Carga inválida: {target_load_percent}%. Deve estar entre 10-100%")
            return
        
        self.target_load = target_load_percent
        self.thread_count = thread_count if thread_count > 0 else multiprocessing.cpu_count()
        self.running = True
        
        print(f"[INFO] Iniciando stress test: {self.target_load}% de carga em {self.thread_count} threads")
        
        # Cria worker threads
        for i in range(self.thread_count):
            thread = threading.Thread(target=self._worker_thread, args=(i,), daemon=True)
            thread.start()
            self.threads.append(thread)
        
        # Thread de monitoramento
        monitor = threading.Thread(target=self._monitor_thread, daemon=True)
        monitor.start()
        
        print("[SUCCESS] Stress test iniciado")
    
    def stop(self):
        """Para o stress test"""
        if not self.running:
            return
        
        print("[INFO] Parando stress test...")
        self.running = False
        
        # Aguarda threads finalizarem
        for thread in self.threads:
            thread.join(timeout=2)
        
        self.threads.clear()
        print("[SUCCESS] Stress test parado")
    
    def adjust_load(self, new_percent):
        """Ajusta carga durante execução"""
        if not (10 <= new_percent <= 100):
            print(f"[ERROR] Carga inválida: {new_percent}%")
            return
        
        self.target_load = new_percent
        print(f"[INFO] Carga ajustada para {self.target_load}%")
    
    def _worker_thread(self, thread_id):
        """Thread worker que gera carga na CPU"""
        check_interval_ms = 100
        
        while self.running:
            start_time = time.time()
            
            # Calcula tempo de trabalho vs descanso
            work_time_ms = (self.target_load * check_interval_ms) / 100
            sleep_time_ms = check_interval_ms - work_time_ms
            
            # Trabalha (usa CPU)
            if work_time_ms > 0:
                work_end = time.time() + (work_time_ms / 1000)
                while time.time() < work_end and self.running:
                    # Cálculos pesados
                    dummy = 0
                    for i in range(1000):
                        dummy += math.sqrt(i) * math.sin(i) * math.cos(i)
            
            # Descansa (libera CPU)
            if sleep_time_ms > 0 and self.running:
                time.sleep(sleep_time_ms / 1000)
    
    def _monitor_thread(self):
        """Monitora uso real de CPU"""
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                print(f"[STRESS] Alvo: {self.target_load}% | Atual: {cpu_percent:.1f}% | "
                      f"Threads: {self.thread_count}", end='\r')
            except:
                pass
            time.sleep(2)


if __name__ == "__main__":
    # Teste
    stress = CPUStressTest()
    
    print("Iniciando stress test com 70% de carga...")
    stress.start(target_load_percent=70)
    
    try:
        time.sleep(10)
        print("\n\nAjustando para 50%...")
        stress.adjust_load(50)
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        stress.stop()
        print("\nFinalizado")
