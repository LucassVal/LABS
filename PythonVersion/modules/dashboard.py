"""
Dashboard visual em tempo real para o Windows Optimizer
Mostra CPU, GPU, RAM, Temperatura e status de otimizações
"""
import psutil
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from datetime import datetime

class Dashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.running = False
        
        # Configuração do layout
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )
        
        # Split body em colunas
        self.layout["body"].split_row(
            Layout(name="cpu_gpu", ratio=1),
            Layout(name="memory", ratio=1)
        )
        
        # Dados para exibir
        self.stats = {
            'cpu_percent': 0,
            'cpu_temp': 0,
            'cpu_freq': 0,
            'cpu_limit': 85,
            'gpu_nvidia_name': '',
            'gpu_nvidia_percent': 0,
            'gpu_nvidia_temp': 0,
            'gpu_nvidia_mem_used': 0,
            'gpu_nvidia_mem_total': 0,
            'gpu_nvidia_power_limit': 0,  # Power limit aplicado
            'gpu_intel_name': '',
            'ram_used': 0,
            'ram_total': 0,
            'ram_percent': 0,
            'ram_cleanups': 0,
            'priority_high': 0,
            'priority_low': 0
        }
        
        # Detecta GPUs
        self.has_nvidia = False
        self.has_intel = False
        self.nvidia_handle = None
        
        # Tenta detectar NVIDIA (geralmente é o device 0)
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            if device_count > 0:
                # Pega o primeiro device
                self.nvidia_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(self.nvidia_handle)
                
                # Decodifica se for bytes
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                self.stats['gpu_nvidia_name'] = name
                self.has_nvidia = True
                print(f"[GPU] NVIDIA detectada: {name}")
        except Exception as e:
            print(f"[GPU] NVIDIA não detectada: {e}")
        
        # Detecta Intel integrada via WMI
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                if 'intel' in gpu.Name.lower():
                    self.has_intel = True
                    self.stats['gpu_intel_name'] = gpu.Name
                    print(f"[GPU] Intel detectada: {gpu.Name}")
                    break
        except Exception as e:
            print(f"[GPU] Intel não detectada: {e}")
    
    def make_header(self):
        """Cria header com título e status"""
        current_time = datetime.now().strftime("%H:%M:%S")
        header_text = f"[bold cyan]⚡ WINDOWS OPTIMIZER DASHBOARD[/bold cyan] | [yellow]{current_time}[/yellow] | [green]●[/green] ATIVO"
        return Panel(header_text, style="bold white on blue")
    
    def make_cpu_gpu_panel(self):
        """Painel de CPU e GPU"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan", width=18)
        table.add_column("Value", justify="right")
        
        # CPU
        cpu_color = "green" if self.stats['cpu_percent'] < 70 else "yellow" if self.stats['cpu_percent'] < 90 else "red"
        cpu_bar = self._make_bar(self.stats['cpu_percent'], 100, cpu_color)
        
        temp_color = "green" if self.stats['cpu_temp'] < 70 else "yellow" if self.stats['cpu_temp'] < 85 else "red"
        temp_display = f"{self.stats['cpu_temp']:.0f}°C" if self.stats['cpu_temp'] > 0 else "N/A"
        
        freq_color = "cyan"
        freq_pct = (self.stats['cpu_freq'] / 4.4) * 100 if self.stats['cpu_freq'] > 0 else 0
        
        table.add_row("[bold white]CPU[/bold white]", "")
        table.add_row("  Uso", f"[{cpu_color}]{self.stats['cpu_percent']:.1f}%[/{cpu_color}] {cpu_bar}")
        table.add_row("  Temperatura", f"[{temp_color}]{temp_display}[/{temp_color}]")
        table.add_row("  Frequência", f"[{freq_color}]{self.stats['cpu_freq']:.2f} GHz[/{freq_color}]")
        table.add_row("  Limite", f"[yellow]{self.stats['cpu_limit']}%[/yellow] (otimizado)")
        table.add_row("", "")
        
        # GPU NVIDIA (dedicada)
        if self.has_nvidia:
            gpu_color = "green" if self.stats['gpu_nvidia_percent'] < 70 else "yellow" if self.stats['gpu_nvidia_percent'] < 90 else "red"
            gpu_bar = self._make_bar(self.stats['gpu_nvidia_percent'], 100, gpu_color)
            
            gpu_temp_color = "green" if self.stats['gpu_nvidia_temp'] < 70 else "yellow" if self.stats['gpu_nvidia_temp'] < 85 else "red"
            
            table.add_row("[bold white]GPU NVIDIA[/bold white]", f"[dim]{self.stats['gpu_nvidia_name'][:20]}[/dim]")
            table.add_row("  Uso", f"[{gpu_color}]{self.stats['gpu_nvidia_percent']:.1f}%[/{gpu_color}] {gpu_bar}")
            table.add_row("  Temperatura", f"[{gpu_temp_color}]{self.stats['gpu_nvidia_temp']:.0f}°C[/{gpu_temp_color}]")
            table.add_row("  VRAM", f"{self.stats['gpu_nvidia_mem_used']:.0f} / {self.stats['gpu_nvidia_mem_total']:.0f} MB")
        
        # GPU Intel (integrada)
        if self.has_intel:
            table.add_row("", "")
            table.add_row("[bold white]GPU Intel[/bold white]", f"[dim]{self.stats['gpu_intel_name'][:20]}[/dim]")
            table.add_row("  Status", "[green]Ativa[/green] (integrada)")
        
        # Se nenhuma GPU detectada
        if not self.has_nvidia and not self.has_intel:
            table.add_row("[bold white]GPU[/bold white]", "[dim]Não detectada[/dim]")
        
        return Panel(table, title="[bold]🖥️  CPU & GPU[/bold]", border_style="cyan")
    
    def make_memory_panel(self):
        """Painel de Memória"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan", width=18)
        table.add_column("Value", justify="right")
        
        # RAM
        ram_color = "green" if self.stats['ram_percent'] < 70 else "yellow" if self.stats['ram_percent'] < 85 else "red"
        ram_bar = self._make_bar(self.stats['ram_percent'], 100, ram_color)
        
        ram_free_gb = (self.stats['ram_total'] - self.stats['ram_used']) / 1024
        ram_total_gb = self.stats['ram_total'] / 1024
        
        table.add_row("[bold white]MEMÓRIA RAM[/bold white]", "")
        table.add_row("  Uso", f"[{ram_color}]{self.stats['ram_percent']:.1f}%[/{ram_color}] {ram_bar}")
        table.add_row("  Livre", f"[green]{ram_free_gb:.1f} GB[/green] / {ram_total_gb:.1f} GB")
        table.add_row("  Limpezas", f"[yellow]{self.stats['ram_cleanups']}[/yellow] automáticas")
        table.add_row("", "")
        
        # Otimizações
        table.add_row("[bold white]OTIMIZAÇÕES[/bold white]", "")
        table.add_row("  Standby Cleaner", "[green]●[/green] Ativo")
        table.add_row("  Smart Priority", "[green]●[/green] Ativo")
        table.add_row("  CPU Limit", f"[yellow]●[/yellow] {self.stats['cpu_limit']}%")
        
        # GPU Power Limit (se aplicado)
        if self.stats['gpu_nvidia_power_limit'] > 0:
            table.add_row("  GPU Power Limit", f"[yellow]●[/yellow] {self.stats['gpu_nvidia_power_limit']}%")
        
        table.add_row("  SysMain", "[red]●[/red] Desabilitado")
        
        return Panel(table, title="[bold]💾  Memória & Status[/bold]", border_style="green")
    
    def make_footer(self):
        """Rodapé com prioridades"""
        table = Table(show_header=True, box=None, expand=True)
        table.add_column("Priorização Inteligente", style="bold cyan")
        table.add_column("Apps Alta Prioridade", justify="center", style="green")
        table.add_column("Apps Baixa Prioridade", justify="center", style="yellow")
        
        table.add_row(
            "Processos do usuário são priorizados automaticamente",
            f"⭐ {self.stats['priority_high']} processos",
            f"🔽 {self.stats['priority_low']} processos"
        )
        
        return Panel(table, title="[bold]🎯  Sistema Inteligente[/bold]", border_style="yellow")
    
    def _make_bar(self, value, max_value, color):
        """Cria uma barra de progresso visual"""
        pct = min(100, (value / max_value) * 100)
        filled = int(pct / 5)  # 20 caracteres max
        empty = 20 - filled
        return f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"
    
    def update_stats(self, services):
        """Atualiza estatísticas do sistema"""
        # CPU
        self.stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        
        # Temperatura da CPU (tentar vários métodos)
        temp_found = False
        
        # Método 1: psutil sensors (Linux-like, raramente funciona no Windows)
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                self.stats['cpu_temp'] = temps['coretemp'][0].current
                temp_found = True
        except:
            pass
        
        # Método 2: WMI MSAcpi_ThermalZoneTemperature
        if not temp_found:
            try:
                import wmi
                w = wmi.WMI(namespace="root\\wmi")
                temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                # Kelvin para Celsius
                self.stats['cpu_temp'] = (temperature_info.CurrentTemperature / 10.0) - 273.15
                temp_found = True
            except:
                pass
        
        # Método 3: WMI OpenHardwareMonitor / LibreHardwareMonitor
        if not temp_found:
            try:
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                sensors = w.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                        self.stats['cpu_temp'] = float(sensor.Value)
                        temp_found = True
                        break
            except:
                pass
        
        # Método 4: Se nada funcionar, usar temperatura da GPU NVIDIA como referência
        if not temp_found and self.has_nvidia and self.stats['gpu_nvidia_temp'] > 0:
            # CPU geralmente é 5-10°C mais quente que GPU
            self.stats['cpu_temp'] = self.stats['gpu_nvidia_temp'] + 7
            temp_found = True
        
        # Se ainda não encontrou, deixa 0 (será mostrado como "N/A")
        if not temp_found:
            self.stats['cpu_temp'] = 0
        
        # Frequência da CPU
        freq = psutil.cpu_freq()
        if freq:
            self.stats['cpu_freq'] = freq.current / 1000  # MHz para GHz
        
        # GPU NVIDIA (se disponível)
        if self.has_nvidia and self.nvidia_handle:
            try:
                import pynvml
                util = pynvml.nvmlDeviceGetUtilizationRates(self.nvidia_handle)
                self.stats['gpu_nvidia_percent'] = util.gpu
                
                temp = pynvml.nvmlDeviceGetTemperature(self.nvidia_handle, 0)
                self.stats['gpu_nvidia_temp'] = temp
                
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.nvidia_handle)
                self.stats['gpu_nvidia_mem_used'] = mem_info.used / 1024 / 1024
                self.stats['gpu_nvidia_mem_total'] = mem_info.total / 1024 / 1024
            except:
                pass
        
        # GPU Power Limit (pega do service se disponível)
        if 'gpu_ctrl' in services and hasattr(services['gpu_ctrl'], 'applied_percent'):
            self.stats['gpu_nvidia_power_limit'] = services['gpu_ctrl'].applied_percent
        
        # RAM
        mem = psutil.virtual_memory()
        self.stats['ram_used'] = mem.used / 1024 / 1024  # MB
        self.stats['ram_total'] = mem.total / 1024 / 1024  # MB
        self.stats['ram_percent'] = mem.percent
        
        # Limpezas de RAM
        if 'cleaner' in services:
            # Compatibilidade com diferentes estruturas
            if hasattr(services['cleaner'], 'clean_count'):
                self.stats['ram_cleanups'] = services['cleaner'].clean_count
            elif hasattr(services['cleaner'], 'CleanCount'):
                self.stats['ram_cleanups'] = services['cleaner'].CleanCount
        
        # Prioridades
        try:
            procs = list(psutil.process_iter(['name', 'nice']))
            high_count = 0
            low_count = 0
            for p in procs:
                try:
                    if p.info['nice']:
                        if p.info['nice'] < psutil.NORMAL_PRIORITY_CLASS:
                            high_count += 1
                        elif p.info['nice'] > psutil.NORMAL_PRIORITY_CLASS:
                            low_count += 1
                except:
                    pass
            self.stats['priority_high'] = high_count
            self.stats['priority_low'] = low_count
        except:
            pass
    
    def render(self, services):
        """Renderiza o dashboard"""
        self.update_stats(services)
        
        self.layout["header"].update(self.make_header())
        self.layout["cpu_gpu"].update(self.make_cpu_gpu_panel())
        self.layout["memory"].update(self.make_memory_panel())
        self.layout["footer"].update(self.make_footer())
        
        return self.layout
    
    def run(self, services):
        """Executa o dashboard em loop"""
        self.running = True
        
        # refresh_per_second=0.2 = atualiza a cada 5 segundos (SEM flickering!)
        with Live(self.render(services), refresh_per_second=0.2, console=self.console, screen=True) as live:
            while self.running:
                time.sleep(5)  # Aguarda 5 segundos entre atualizações
                live.update(self.render(services))


if __name__ == "__main__":
    # Teste
    dash = Dashboard()
    dash.run({})
