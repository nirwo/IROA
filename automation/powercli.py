
import subprocess

def shutdown_vm(vm_name):
    cmd = f'powershell.exe -Command "Stop-VM -Name '{vm_name}' -Confirm:$false"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "vm": vm_name,
        "command": cmd,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "success": result.returncode == 0
    }

def resize_vm(vm_name, cpu, memory_gb):
    cmd = f'powershell.exe -Command "Set-VM -Name '{vm_name}' -NumCpu {cpu} -MemoryGB {memory_gb} -Confirm:$false"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "vm": vm_name,
        "command": cmd,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "success": result.returncode == 0
    }
