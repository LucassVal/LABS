"""
Gerenciador inteligente de prioridades de processos
Detecta automaticamente processos iniciados pelo usuário e prioriza
"""
import psutil
import time
import threading

class SmartProcessManager:
    def __init__(self):
        self.running = False
        self.thread = None
        
        # Lista de processos do sistema que NUNCA devem ter prioridade alta
        self.system_processes = {
            'svchost.exe', 'csrss.exe', 'dwm.exe', 'winlogon.exe',
            'services.exe', 'lsass.exe', 'smss.exe', 'wininit.exe',
            'System', 'Registry', 'Idle'
        }
        
        # Processos que devem ter prioridade BAIXA (mesmo se iniciados pelo usuário)
        # Navegadores e apps em background
        self.low_priority_apps = {
            'chrome.exe', 'msedge.exe', 'firefox.exe', 'opera.exe',
            'discord.exe', 'spotify.exe', 'steam.exe',  # Background apps
            'onedrive.exe', 'dropbox.exe', 'googledrivesync.exe'
        }
        
        # Processos já ajustados (para não ficar reajustando)
        self.adjusted_pids = set()
        
    def start(self):
        """Inicia monitoramento inteligente"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
        print("[INFO] SmartProcessManager iniciado - Priorizando processos do usuário automaticamente")
    
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Loop de monitoramento contínuo"""
        while self.running:
            try:
                self._scan_and_prioritize()
                time.sleep(10)  # Verifica a cada 10 segundos
            except Exception as e:
                print(f"[ERROR] Erro no monitoramento: {e}")
                time.sleep(30)
    
    def _scan_and_prioritize(self):
        """Escaneia processos e ajusta prioridades automaticamente"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'nice']):
                try:
                    # Pula se já ajustamos este PID
                    if proc.pid in self.adjusted_pids:
                        continue
                    
                    # Pula processos do sistema
                    if proc.info['name'].lower() in self.system_processes:
                        continue
                    
                    # Pula se não conseguir pegar username (processos protegidos)
                    if not proc.info['username']:
                        continue
                    
                    # Detecta se é processo do usuário (não é SYSTEM)
                    is_user_process = 'SYSTEM' not in proc.info['username'].upper()
                    
                    if is_user_process:
                        proc_name_lower = proc.info['name'].lower()
                        
                        # Prioridade BAIXA para navegadores e apps de background
                        if proc_name_lower in self.low_priority_apps:
                            self._set_low_priority(proc)
                        else:
                            # PRIORIDADE ALTA para qualquer outro app do usuário!
                            self._set_high_priority(proc)
                        
                        # Marca como ajustado
                        self.adjusted_pids.add(proc.pid)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Limpa PIDs de processos que já não existem
            self._cleanup_dead_pids()
        
        except Exception as e:
            print(f"[ERROR] Erro ao escanear processos: {e}")
    
    def _set_high_priority(self, proc):
        """Define prioridade ALTA"""
        try:
            # Prioridade de CPU: High
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
            
            # Prioridade de I/O: High (apenas Windows)
            try:
                proc.ionice(psutil.IOPRIO_HIGH)
            except:
                pass  # Nem sempre disponível
            
            print(f"[PRIORITY] ⭐ ALTA → {proc.info['name']} (PID: {proc.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _set_low_priority(self, proc):
        """Define prioridade BAIXA"""
        try:
            # Prioridade de CPU: Below Normal
            proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            
            # Prioridade de I/O: Low
            try:
                proc.ionice(psutil.IOPRIO_LOW)
            except:
                pass
            
            print(f"[PRIORITY] 🔽 BAIXA → {proc.info['name']} (PID: {proc.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _cleanup_dead_pids(self):
        """Remove PIDs de processos que já não existem"""
        try:
            alive_pids = {p.pid for p in psutil.process_iter()}
            self.adjusted_pids = self.adjusted_pids.intersection(alive_pids)
        except:
            pass


if __name__ == "__main__":
    # Teste
    manager = SmartProcessManager()
    manager.start()
    
    print("\nMonitorando processos...")
    print("Qualquer app iniciado pelo usuário receberá prioridade ALTA automaticamente!")
    print("\nPressione Ctrl+C para parar\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("\n[INFO] Finalizado")
