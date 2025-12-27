"""
Controle de ventoinhas - força 100% de velocidade
Windows não tem API nativa para controle direto de ventoinhas,
então usamos WMI quando disponível
"""
import subprocess
import os

class FanController:
    def __init__(self):
        self.enabled = False
        self.method = None
        
    def detect_fan_control_method(self):
        """Detecta qual método de controle está disponível"""
        # Método 1: Tentar via WMI Dell
        if self._try_wmi_dell():
            self.method = "WMI_DELL"
            return True
        
        # Método 2: Via NoteBook FanControl (se instalado)
        if self._check_nbfc():
            self.method = "NBFC"
            return True
        
        # Método 3: Informar que precisa de ferramenta externa
        self.method = "EXTERNAL"
        return False
    
    def _try_wmi_dell(self):
        """Tenta controle via WMI (funciona em alguns laptops Dell)"""
        try:
            import wmi
            c = wmi.WMI(namespace="root\\wmi")
            # Verifica se tem suporte Dell Thermal
            thermal = c.query("SELECT * FROM DellThermalSetting")
            return len(thermal) > 0
        except:
            return False
    
    def _check_nbfc(self):
        """Verifica se NoteBook FanControl está instalado"""
        try:
            result = subprocess.run(['nbfc', 'status'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def set_max_speed(self):
        """Define ventoinhas no máximo"""
        if self.method == "WMI_DELL":
            return self._set_dell_performance_mode()
        elif self.method == "NBFC":
            return self._set_nbfc_max()
        else:
            return False
    
    def _set_dell_performance_mode(self):
        """Define modo performance em Dell (ventoinhas no máximo)"""
        try:
            import wmi
            c = wmi.WMI(namespace="root\\wmi")
            thermal = c.DellThermalSetting()[0]
            thermal.SetThermalSetting(ThermalMode=2)  # 2 = Performance
            print("[FAN] ✓ Modo Performance ativado (ventoinhas no máximo)")
            return True
        except Exception as e:
            print(f"[FAN] Erro ao configurar: {e}")
            return False
    
    def _set_nbfc_max(self):
        """Define NBFC para velocidade máxima"""
        try:
            subprocess.run(['nbfc', 'set', '-s', '100'], 
                         check=True,
                         capture_output=True)
            print("[FAN] ✓ NBFC configurado para 100%")
            return True
        except:
            return False
    
    def get_recommendation(self):
        """Retorna recomendação de ferramenta para controle de ventoinhas"""
        return """
╔════════════════════════════════════════════════════════════╗
║  CONTROLE DE VENTOINHAS - Configuração Manual Necessária  ║
╚════════════════════════════════════════════════════════════╝

O Windows não permite controle direto de ventoinhas via software.

OPÇÕES RECOMENDADAS:

1. 📱 NOTEBOOK FAN CONTROL (NBFC) - Recomendado
   • Download: https://github.com/hirschmann/nbfc/releases
   • Compatível com a maioria dos laptops
   • Interface gráfica simples
   • Após instalar, rode: nbfc set -s 100

2. 🔧 BIOS/UEFI
   • Reinicie e entre na BIOS (F2 ou DEL)
   • Procure por "Fan Control" ou "Thermal Settings"
   • Mude para "Performance" ou "Full Speed"

3. 🎮 SOFTWARE DO FABRICANTE
   • Dell: Dell Power Manager
   • HP: HP Command Center
   • Lenovo: Lenovo Vantage
   • ASUS: Armoury Crate

APÓS CONFIGURAR MANUALMENTE:
✓ Ventoinhas sempre a 100%
✓ CPU a 85% (temperatura controlada)
✓ Sistema estável e fresco!
"""


if __name__ == "__main__":
    controller = FanController()
    
    print("Detectando método de controle de ventoinhas...")
    if controller.detect_fan_control_method():
        print(f"✓ Método detectado: {controller.method}")
        controller.set_max_speed()
    else:
        print(controller.get_recommendation())
