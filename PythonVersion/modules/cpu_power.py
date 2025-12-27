"""
Gerenciador de energia e frequência da CPU
"""
import ctypes
from ctypes import wintypes
import subprocess

class CPUPowerManager:
    def __init__(self):
        self.powrprof = ctypes.WinDLL('powrprof')
        
        # GUIDs
        self.GUID_PROCESSOR_SETTINGS = "{54533251-82be-4824-96c1-47b60b740d00}"
        self.GUID_MAX_THROTTLE = "{bc5038f7-23e0-4960-96da-33abaf5935ec}"
        self.GUID_MIN_THROTTLE = "{893dee8e-2bef-41e0-89c6-b55d0929964c}"
    
    def set_max_cpu_frequency(self, percentage):
        """Define frequência máxima da CPU (5-100%)"""
        if not (5 <= percentage <= 100):
            print(f"[ERROR] Percentual inválido: {percentage}%. Deve estar entre 5-100%")
            return False
        
        try:
            print(f"[INFO] Configurando frequência máxima da CPU para {percentage}%")
            
            # Usa powercfg.exe (mais simples e confiável)
            result = subprocess.run(
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 self.GUID_PROCESSOR_SETTINGS, self.GUID_MAX_THROTTLE, str(percentage)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Aplica mudanças
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'])
                print(f"[SUCCESS] Frequência máxima definida para {percentage}%")
                return True
            else:
                print(f"[ERROR] Falha ao configurar: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Erro ao definir frequência: {e}")
            return False
    
    def set_min_cpu_frequency(self, percentage):
        """Define frequência mínima da CPU (0-100%)"""
        if not (0 <= percentage <= 100):
            print(f"[ERROR] Percentual inválido: {percentage}%")
            return False
        
        try:
            print(f"[INFO] Configurando frequência mínima da CPU para {percentage}%")
            
            result = subprocess.run(
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 self.GUID_PROCESSOR_SETTINGS, self.GUID_MIN_THROTTLE, str(percentage)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'])
                print(f"[SUCCESS] Frequência mínima definida para {percentage}%")
                return True
            else:
                print(f"[ERROR] Falha: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Erro: {e}")
            return False
    
    def restore_defaults(self):
        """Restaura configurações padrão (100% max, 5% min)"""
        print("[INFO] Restaurando configurações padrão de CPU")
        return self.set_max_cpu_frequency(100) and self.set_min_cpu_frequency(5)


if __name__ == "__main__":
    # Teste
    manager = CPUPowerManager()
    
    print("Testando controle de CPU...")
    print("1. Definindo máximo para 80%")
    manager.set_max_cpu_frequency(80)
    
    input("\nPressione ENTER para restaurar padrões...")
    manager.restore_defaults()
