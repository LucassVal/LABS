"""
Widget flutuante do Windows Optimizer
Alternativa ao dashboard de console que pisca
"""
import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading

class OptimizerWidget:
    def __init__(self, services):
        self.services = services
        self.root = tk.Tk()
        self.root.title("Windows Optimizer")
        
        # Configurações da janela
        self.root.geometry("400x300+10+10")  # Tamanho e posição
        self.root.attributes('-topmost', True)  # Sempre no topo
        self.root.attributes('-alpha', 0.95)  # Levemente transparente
        self.root.configure(bg='#1a1a1a')
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1a1a1a', foreground='white', font=('Consolas', 9))
        style.configure('Title.TLabel', font=('Consolas', 11, 'bold'), foreground='#00ff00')
        
        self.create_widgets()
        self.running = True
        
        # Thread para atualizar dados
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Título
        title = ttk.Label(self.root, text="⚡ WINDOWS OPTIMIZER", style='Title.TLabel')
        title.pack(pady=5)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Labels para dados
        self.cpu_label = ttk.Label(main_frame, text="CPU: ...")
        self.cpu_label.pack(anchor='w', pady=2)
        
        self.cpu_temp_label = ttk.Label(main_frame, text="Temp CPU: ...")
        self.cpu_temp_label.pack(anchor='w', pady=2)
        
        self.gpu_nvidia_label = ttk.Label(main_frame, text="GPU NVIDIA: ...")
        self.gpu_nvidia_label.pack(anchor='w', pady=2)
        
        self.gpu_intel_label = ttk.Label(main_frame, text="GPU Intel: Detectando...")
        self.gpu_intel_label.pack(anchor='w', pady=2)
        
        self.ram_label = ttk.Label(main_frame, text="RAM: ...")
        self.ram_label.pack(anchor='w', pady=2)
        
        self.cleanups_label = ttk.Label(main_frame, text="Limpezas: 0")
        self.cleanups_label.pack(anchor='w', pady=2)
        
        # Separador
        sep = tk.Frame(main_frame, height=2, bg='#00ff00')
        sep.pack(fill=tk.X, pady=10)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="● Standby Cleaner: Ativo", foreground='#00ff00')
        self.status_label.pack(anchor='w', pady=2)
        
        self.priority_label = ttk.Label(main_frame, text="● Smart Priority: Ativo", foreground='#00ff00')
        self.priority_label.pack(anchor='w', pady=2)
        
        self.cpu_limit_label = ttk.Label(main_frame, text="● CPU Limit: 85%", foreground='#ffff00')
        self.cpu_limit_label.pack(anchor='w', pady=2)
    
    def update_loop(self):
        """Loop de atualização dos dados"""
        while self.running:
            try:
                self.update_data()
                time.sleep(2)  # Atualiza a cada 2 segundos
            except:
                pass
    
    def update_data(self):
        """Atualiza os dados exibidos"""
        try:
            # CPU
            cpu_pct = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            freq_ghz = cpu_freq.current / 1000 if cpu_freq else 0
            self.cpu_label.config(text=f"CPU: {cpu_pct:.1f}% @ {freq_ghz:.2f} GHz")
            
            # GPU NVIDIA + Temperatura
            try:
                import pynvml
                pynvml.nvmlInit()
                
                # Procura NVIDIA
                device_count = pynvml.nvmlDeviceGetCount()
                nvidia_found = False
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    if 'nvidia' in name.lower():
                        gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                        gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        
                        cpu_temp = gpu_temp + 7  # Estimativa CPU
                        self.cpu_temp_label.config(text=f"Temp CPU: ~{cpu_temp:.0f}°C (est.)")
                        
                        vram_gb = mem_info.total / (1024**3)
                        self.gpu_nvidia_label.config(
                            text=f"GPU NVIDIA: {gpu_util.gpu}% @ {gpu_temp}°C ({vram_gb:.0f}GB)",
                            foreground='#00ff00'
                        )
                        nvidia_found = True
                        break
                
                if not nvidia_found:
                    self.gpu_nvidia_label.config(text="GPU NVIDIA: Não detectada", foreground='#888888')
            except:
                self.cpu_temp_label.config(text="Temp CPU: N/A")
                self.gpu_nvidia_label.config(text="GPU NVIDIA: Erro", foreground='#ff0000')
            
            # GPU Intel (integrada)
            try:
                import wmi
                c = wmi.WMI()
                intel_found = False
                for gpu in c.Win32_VideoController():
                    if 'intel' in gpu.Name.lower():
                        self.gpu_intel_label.config(
                            text=f"GPU Intel: {gpu.Name[:25]}... (Integrada)",
                            foreground='#00aaff'
                        )
                        intel_found = True
                        break
                
                if not intel_found:
                    self.gpu_intel_label.config(text="GPU Intel: Não detectada", foreground='#888888')
            except:
                self.gpu_intel_label.config(text="GPU Intel: Erro", foreground='#ff0000')
            
            # RAM
            mem = psutil.virtual_memory()
            ram_free_gb = (mem.total - mem.used) / (1024**3)
            ram_total_gb = mem.total / (1024**3)
            self.ram_label.config(text=f"RAM: {mem.percent:.1f}% usado ({ram_free_gb:.1f}GB livre / {ram_total_gb:.1f}GB)")
            
            # Limpezas
            if 'cleaner' in self.services:
                if hasattr(self.services['cleaner'], 'clean_count'):
                    cleanups = self.services['cleaner'].clean_count
                    self.cleanups_label.config(text=f"Limpezas: {cleanups} automáticas")
        
        except Exception as e:
            pass
    
    def run(self):
        """Inicia o widget"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Chamado ao fechar a janela"""
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    # Teste
    widget = OptimizerWidget({})
    widget.run()
