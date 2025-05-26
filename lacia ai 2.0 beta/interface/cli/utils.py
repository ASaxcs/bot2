"""
Utility functions untuk CLI Lacia AI
"""

import os
import sys
import json
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import subprocess
import platform
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

def get_terminal_size() -> Tuple[int, int]:
    """Dapatkan ukuran terminal"""
    try:
        return shutil.get_terminal_size()
    except:
        return (80, 24)  # Default size

def print_table(headers: List[str], rows: List[List[str]], 
                max_width: Optional[int] = None):
    """Print tabel yang rapi"""
    if not rows:
        return
    
    # Calculate column widths
    if max_width is None:
        max_width = get_terminal_size()[0] - 4
    
    col_widths = [len(header) for header in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Adjust widths if too wide
    total_width = sum(col_widths) + len(headers) * 3 + 1
    if total_width > max_width:
        excess = total_width - max_width
        # Reduce widths proportionally
        for i in range(len(col_widths)):
            reduction = min(col_widths[i] // 4, excess // len(col_widths))
            col_widths[i] = max(col_widths[i] - reduction, 10)
            excess -= reduction
            if excess <= 0:
                break
    
    # Print header
    header_line = "│"
    separator_line = "├"
    
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        header_line += f" {header:<{width}} │"
        separator_line += "─" * (width + 2) + ("┼" if i < len(headers) - 1 else "┤")
    
    # Top border
    top_line = "┌" + "─" * (len(header_line) - 2) + "┐"
    print(f"{Fore.CYAN}{top_line}{Style.RESET_ALL}")
    
    # Header
    print(f"{Fore.CYAN}{header_line}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{separator_line}{Style.RESET_ALL}")
    
    # Rows
    for row in rows:
        row_line = "│"
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            cell_str = str(cell)
            if len(cell_str) > width:
                cell_str = cell_str[:width-3] + "..."
            row_line += f" {cell_str:<{width}} │"
        print(row_line)
    
    # Bottom border
    bottom_line = "└" + "─" * (len(header_line) - 2) + "┘"
    print(f"{Fore.CYAN}{bottom_line}{Style.RESET_ALL}")

def print_progress_bar(current: int, total: int, width: int = 50, 
                      prefix: str = "", suffix: str = ""):
    """Print progress bar"""
    if total == 0:
        return
    
    percent = current / total
    filled_length = int(width * percent)
    
    bar = "█" * filled_length + "░" * (width - filled_length)
    percent_str = f"{percent:.1%}"
    
    print(f"\r{prefix} [{Fore.GREEN}{bar}{Style.RESET_ALL}] {percent_str} {suffix}", end="")
    
    if current == total:
        print()  # New line when complete

def format_file_size(size_bytes: int) -> str:
    """Format ukuran file"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """Format durasi waktu"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def validate_json(json_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """Validasi string JSON"""
    try:
        data = json.loads(json_str)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, str(e)

def safe_input(prompt: str, default: str = "", password: bool = False) -> str:
    """Input yang aman dengan default value"""
    try:
        if password:
            import getpass
            value = getpass.getpass(prompt)
        else:
            display_prompt = f"{prompt} [{default}]: " if default else f"{prompt}: "
            value = input(display_prompt).strip()
        
        return value if value else default
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return default
    except EOFError:
        return default

def confirm_action(message: str, default: bool = False) -> bool:
    """Konfirmasi aksi dari user"""
    default_str = "Y/n" if default else "y/N"
    prompt = f"{message} ({default_str}): "
    
    try:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return False

def get_system_info() -> Dict[str, Any]:
    """Dapatkan informasi sistem"""
    info = {
        'platform': platform.platform(),
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }
    
    # CPU info
    try:
        if platform.system() == "Windows":
            info['cpu_count'] = os.cpu_count()
        else:
            info['cpu_count'] = os.cpu_count()
    except:
        info['cpu_count'] = 'Unknown'
    
    # Memory info (basic)
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemTotal:' in line:
                        total_kb = int(line.split()[1])
                        info['memory_total'] = format_file_size(total_kb * 1024)
                        break
        else:
            info['memory_total'] = 'Unknown'
    except:
        info['memory_total'] = 'Unknown'
    
    return info

def check_dependencies() -> Dict[str, bool]:
    """Check apakah dependencies tersedia"""
    dependencies = {
        'colorama': False,
        'json': True,  # Built-in
        'pathlib': True,  # Built-in
        'argparse': True,  # Built-in
    }
    
    # Check external dependencies  
    try:
        import colorama
        dependencies['colorama'] = True
    except ImportError:
        pass
    
    return dependencies

def create_backup(file_path: str, backup_dir: str = "backups") -> Optional[str]:
    """Buat backup file"""
    try:
        source = Path(file_path)
        if not source.exists():
            return None
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"{source.stem}_{timestamp}{source.suffix}"
        
        shutil.copy2(source, backup_file)
        return str(backup_file)
    
    except Exception:
        return None

def cleanup_old_files(directory: str, max_age_days: int = 30, 
                     pattern: str = "*") -> int:
    """Cleanup file lama"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return 0
        
        count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    count += 1
        
        return count
    
    except Exception:
        return 0

def export_data(data: Any, filename: str, format_type: str = "json") -> bool:
    """Export data ke file"""
    try:
        file_path = Path(filename)
        
        if format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        elif format_type.lower() == "txt":
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(data, (list, tuple)):
                    for item in data:
                        f.write(f"{item}\n")
                else:
                    f.write(str(data))
        
        else:
            return False
        
        return True
    
    except Exception:
        return False

def import_data(filename: str, format_type: str = "json") -> Tuple[bool, Any, Optional[str]]:
    """Import data dari file"""
    try:
        file_path = Path(filename)
        
        if not file_path.exists():
            return False, None, "File not found"
        
        if format_type.lower() == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return True, data, None
        
        elif format_type.lower() == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
                return True, data, None
        
        else:
            return False, None, "Unsupported format"
    
    except Exception as e:
        return False, None, str(e)

def run_command(command: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """Jalankan command sistem"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return (
            result.returncode == 0,
            result.stdout,
            result.stderr
        )
    
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def get_available_ports(start_port: int = 8000, count: int = 10) -> List[int]:
    """Dapatkan port yang tersedia"""
    import socket
    available_ports = []
    
    for port in range(start_port, start_port + count * 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                available_ports.append(port)
                if len(available_ports) >= count:
                    break
        except OSError:
            continue
    
    return available_ports

def format_json_output(data: Any, colored: bool = True) -> str:
    """Format JSON untuk output yang rapi"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    if not colored:
        return json_str
    
    # Simple syntax highlighting
    lines = json_str.split('\n')
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('"') and '":' in stripped:
            # Key
            key_part, value_part = line.split(':', 1)
            formatted_line = f"{Fore.BLUE}{key_part}{Style.RESET_ALL}:{value_part}"
        elif stripped.startswith('"') and stripped.endswith('",'):
            # String value
            formatted_line = f"{Fore.GREEN}{line}{Style.RESET_ALL}"
        elif any(stripped.startswith(x) for x in ['{', '}', '[', ']']):
            # Brackets
            formatted_line = f"{Fore.CYAN}{line}{Style.RESET_ALL}"
        else:
            formatted_line = line
        
        formatted_lines.append(formatted_line)
    
    return '\n'.join(formatted_lines)

def create_config_template(filename: str = "config_template.json") -> bool:
    """Buat template konfigurasi"""
    template = {
        "ai_core": {
            "model": "default",
            "temperature": 0.7,
            "max_tokens": 2048
        },
        "memory": {
            "enabled": True,
            "max_history": 1000,
            "persist_sessions": True
        },
        "extensions": {
            "auto_load": True,
            "extension_dirs": ["extensions", "plugins"]
        },
        "interfaces": {
            "cli": {
                "enabled": True,
                "colored_output": True
            },
            "api": {
                "enabled": False,
                "host": "localhost",
                "port": 8000
            }
        },
        "logging": {
            "level": "INFO",
            "file": "logs/lacia.log",
            "max_size": "10MB"
        }
    }
    
    return export_data(template, filename, "json")

class CLIProgressBar:
    """Progress bar untuk CLI"""
    
    def __init__(self, total: int, width: int = 50, desc: str = "Progress"):
        self.total = total
        self.width = width
        self.desc = desc
        self.current = 0
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current = min(self.current + increment, self.total)
        self._display()
    
    def set_progress(self, current: int):
        """Set progress absolut"""
        self.current = min(current, self.total)
        self._display()
    
    def _display(self):
        """Display progress bar"""
        if self.total == 0:
            return
        
        percent = self.current / self.total
        filled_length = int(self.width * percent)
        
        bar = "█" * filled_length + "░" * (self.width - filled_length)
        percent_str = f"{percent:.1%}"
        
        # Calculate ETA
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = format_duration(eta)
        else:
            eta_str = "∞"
        
        print(f"\r{self.desc}: [{Fore.GREEN}{bar}{Style.RESET_ALL}] {percent_str} ETA: {eta_str}", end="")
        
        if self.current == self.total:
            print()  # New line when complete
    
    def finish(self):
        """Finish progress bar"""
        self.current = self.total
        self._display()

class CLISpinner:
    """Spinner untuk loading"""
    
    def __init__(self, message: str = "Loading"):
        self.message = message
        self.spinning = False
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_char = 0
    
    def start(self):
        """Start spinner"""
        import threading
        import time
        
        self.spinning = True
        
        def spin():
            while self.spinning:
                char = self.spinner_chars[self.current_char]
                print(f"\r{Fore.YELLOW}{char}{Style.RESET_ALL} {self.message}", end="")
                self.current_char = (self.current_char + 1) % len(self.spinner_chars)
                time.sleep(0.1)
        
        self.thread = threading.Thread(target=spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: str = "Done"):
        """Stop spinner"""
        self.spinning = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=0.2)
        print(f"\r{Fore.GREEN}✓{Style.RESET_ALL} {final_message}")

def print_banner(text: str, char: str = "=", width: Optional[int] = None):
    """Print banner dengan teks"""
    if width is None:
        width = get_terminal_size()[0]
    
    text_width = len(text)
    if text_width >= width - 4:
        print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
        return
    
    padding = (width - text_width - 2) // 2
    banner_line = char * width
    text_line = char + " " * padding + text + " " * padding + char
    
    # Adjust if odd width
    if len(text_line) < width:
        text_line += char
    
    print(f"{Fore.CYAN}{banner_line}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text_line}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{banner_line}{Style.RESET_ALL}")

def print_error(message: str, exit_code: Optional[int] = None):
    """Print error message"""
    print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}", file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)

def print_warning(message: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}Warning: {message}{Style.RESET_ALL}")

def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}Success: {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Print info message"""
    print(f"{Fore.BLUE}Info: {message}{Style.RESET_ALL}")

# Context manager untuk temporary directory
class TempDirectory:
    """Temporary directory context manager"""
    
    def __init__(self, prefix: str = "lacia_temp_"):
        self.prefix = prefix
        self.temp_dir = None
    
    def __enter__(self):
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp(prefix=self.prefix))
        return self.temp_dir
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

# Decorator untuk measure execution time
def measure_time(func):
    """Decorator untuk mengukur waktu eksekusi"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        print(f"{Fore.CYAN}Execution time: {format_duration(duration)}{Style.RESET_ALL}")
        
        return result
    return wrapper