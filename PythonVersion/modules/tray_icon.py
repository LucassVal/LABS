"""
System Tray Icon with Window Hide/Show
Permite minimizar o otimizador para a bandeja do sistema
Requer: pip install pystray pillow
"""
import threading
import sys
import os
import ctypes

# Tenta importar pystray (pode não estar instalado)
TRAY_AVAILABLE = False
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    print("[TRAY] pystray não instalado. Execute: pip install pystray pillow")

# Windows API para esconder/mostrar janela
def get_console_window():
    """Retorna handle da janela do console"""
    return ctypes.windll.kernel32.GetConsoleWindow()

def hide_console():
    """Esconde a janela do console"""
    hwnd = get_console_window()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0

def show_console():
    """Mostra a janela do console"""
    hwnd = get_console_window()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW = 5
        ctypes.windll.user32.SetForegroundWindow(hwnd)

class SystemTrayIcon:
    """Gerencia ícone na bandeja do sistema"""
    
    def __init__(self, optimizer_services=None, on_quit_callback=None):
        self.services = optimizer_services or {}
        self.on_quit = on_quit_callback
        self.icon = None
        self.running = False
        self.console_visible = True
        
        if not TRAY_AVAILABLE:
            print("[TRAY] Sistema de tray não disponível")
            return
    
    def _create_icon_image(self, color='green'):
        """Cria imagem do ícone (círculo colorido)"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Cores baseadas no status
        colors = {
            'green': (0, 200, 80, 255),
            'yellow': (255, 200, 0, 255),
            'red': (255, 60, 60, 255)
        }
        fill_color = colors.get(color, colors['green'])
        
        # Desenha círculo
        margin = 4
        draw.ellipse([margin, margin, size-margin, size-margin], fill=fill_color)
        
        # Adiciona borda
        draw.ellipse([margin, margin, size-margin, size-margin], outline=(255, 255, 255, 200), width=2)
        
        return image
    
    def _create_menu(self):
        """Cria menu de contexto do tray"""
        menu_items = [
            pystray.MenuItem('Status: Ativo ✓', None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('📺 Mostrar/Esconder', self._toggle_console, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('🎮 Perfil Gaming', lambda: self._set_profile('gaming')),
            pystray.MenuItem('💼 Perfil Produtividade', lambda: self._set_profile('productivity')),
            pystray.MenuItem('🔋 Perfil Economia', lambda: self._set_profile('battery_saver')),
            pystray.MenuItem('⚖️ Perfil Balanceado', lambda: self._set_profile('balanced')),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('🧹 Limpar RAM Agora', self._force_clean),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('❌ Sair', self._quit)
        ]
        return pystray.Menu(*menu_items)
    
    def _toggle_console(self):
        """Alterna visibilidade do console (Mostrar/Esconder)"""
        if self.console_visible:
            hide_console()
            self.console_visible = False
            print("[TRAY] Console minimizado para bandeja")
        else:
            show_console()
            self.console_visible = True
    
    def _set_profile(self, profile_name):
        """Muda perfil via menu"""
        try:
            from modules.profiles import get_manager, OptimizationProfile
            manager = get_manager()
            manager.set_services(self.services)
            
            profile_map = {
                'gaming': OptimizationProfile.GAMING,
                'productivity': OptimizationProfile.PRODUCTIVITY,
                'battery_saver': OptimizationProfile.BATTERY_SAVER,
                'balanced': OptimizationProfile.BALANCED
            }
            
            if profile_name in profile_map:
                manager.apply_profile(profile_map[profile_name])
        except Exception as e:
            print(f"[TRAY] Erro ao mudar perfil: {e}")
    
    def _force_clean(self):
        """Força limpeza de RAM"""
        if 'cleaner' in self.services:
            freed = self.services['cleaner'].clean_standby_memory()
            print(f"[TRAY] Limpeza manual: {freed}MB liberados")
    
    def _quit(self):
        """Fecha o programa"""
        self.running = False
        show_console()  # Mostra console antes de sair
        if self.icon:
            self.icon.stop()
        if self.on_quit:
            self.on_quit()
        sys.exit(0)
    
    def start(self):
        """Inicia o ícone na bandeja"""
        if not TRAY_AVAILABLE:
            print("[TRAY] Tray não disponível - continuando sem ícone")
            return False
        
        self.running = True
        
        try:
            self.icon = pystray.Icon(
                name="NVMe Optimizer",
                icon=self._create_icon_image('green'),
                title="Windows NVMe Optimizer V3.0\nClique para mostrar/esconder",
                menu=self._create_menu()
            )
            
            # Roda em thread separada
            tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            tray_thread.start()
            
            print("[TRAY] ✓ Ícone na bandeja ativado (clique direito para opções)")
            return True
            
        except Exception as e:
            print(f"[TRAY] Erro ao iniciar tray: {e}")
            return False
    
    def minimize_to_tray(self):
        """Minimiza para a bandeja"""
        hide_console()
        self.console_visible = False
    
    def update_status(self, status='green', tooltip=""):
        """Atualiza cor e tooltip do ícone"""
        if self.icon:
            self.icon.icon = self._create_icon_image(status)
            if tooltip:
                self.icon.title = tooltip
    
    def stop(self):
        """Para o ícone"""
        self.running = False
        show_console()
        if self.icon:
            self.icon.stop()


if __name__ == "__main__":
    # Teste
    def on_quit():
        print("Saindo...")
        sys.exit(0)
    
    tray = SystemTrayIcon(on_quit_callback=on_quit)
    if tray.start():
        print("Tray iniciado. Clique com botão direito no ícone.")
        print("Clique em 'Mostrar/Esconder' para minimizar para bandeja.")
        try:
            while tray.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            tray.stop()
    else:
        print("Falha ao iniciar tray. Instale: pip install pystray pillow")
