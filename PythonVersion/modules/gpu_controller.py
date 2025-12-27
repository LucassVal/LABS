"""
Módulo de controle de GPU NVIDIA
Aplica Power Limit via pynvml (alternativa ao undervolt manual)
"""
import pynvml

class GPUController:
    def __init__(self):
        self.handle = None
        self.max_power = 0
        self.initialized = False
        self.applied_percent = 0  # Guarda percentual aplicado
        
        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Pega power limit máximo
            self.max_power = pynvml.nvmlDeviceGetPowerManagementLimit(self.handle)
            self.initialized = True
            
            name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            print(f"[GPU] {name} detectada")
            print(f"[GPU] Power Limit máximo: {self.max_power / 1000:.1f}W")
        except Exception as e:
            print(f"[GPU] Erro ao inicializar: {e}")
    
    def set_power_limit_percent(self, percent):
        """
        Define power limit em porcentagem
        percent: 50-100 (ex: 90 = 90% do máximo)
        """
        if not self.initialized:
            print("[GPU] Controlador não inicializado")
            return False
        
        try:
            if percent < 50 or percent > 100:
                print(f"[GPU] Porcentagem inválida: {percent}% (use 50-100)")
                return False
            
            new_limit = int((self.max_power * percent) / 100)
            
            # Tenta aplicar
            result = pynvml.nvmlDeviceSetPowerManagementLimit(self.handle, new_limit)
            
            # Verifica se aplicou
            current = pynvml.nvmlDeviceGetPowerManagementLimit(self.handle)
            
            if abs(current - new_limit) < 1000:  # Margem de 1W
                self.applied_percent = percent
                print(f"[GPU] ✓ Power limit ajustado: {percent}% ({new_limit / 1000:.1f}W)")
                print(f"[GPU] Verificado: {current / 1000:.1f}W aplicado")
                return True
            else:
                print(f"[GPU] ⚠ Comando enviado mas limite não mudou")
                print(f"[GPU] Esperado: {new_limit / 1000:.1f}W, Atual: {current / 1000:.1f}W")
                return False
                
        except pynvml.NVMLError_NotSupported:
            print(f"[GPU] ✗ Power limit não suportado neste modelo/driver")
            return False
        except pynvml.NVMLError_NoPermission:
            print(f"[GPU] ✗ Sem permissão (tente executar como Admin)")
            return False
        except Exception as e:
            print(f"[GPU] ✗ Erro ao ajustar: {e}")
            print(f"[GPU] Tipo de erro: {type(e).__name__}")
            return False
    
    def get_current_stats(self):
        """Retorna estatísticas atuais da GPU"""
        if not self.initialized:
            return None
        
        try:
            stats = {
                'temperature': pynvml.nvmlDeviceGetTemperature(self.handle, 0),
                'power_usage': pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000,  # mW para W
                'gpu_util': pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu,
                'mem_util': pynvml.nvmlDeviceGetUtilizationRates(self.handle).memory,
            }
            return stats
        except:
            return None


if __name__ == "__main__":
    # Teste
    gpu = GPUController()
    
    if gpu.initialized:
        print("\n=== Status Atual ===")
        stats = gpu.get_current_stats()
        if stats:
            print(f"Temperatura: {stats['temperature']}°C")
            print(f"Consumo: {stats['power_usage']:.1f}W")
            print(f"GPU Uso: {stats['gpu_util']}%")
        
        # Exemplo: limitar a 90%
        # gpu.set_power_limit_percent(90)
