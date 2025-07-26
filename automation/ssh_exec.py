
import subprocess

def execute_remote_command(host, command, user='root'):
    try:
        ssh_command = ["ssh", f"{user}@{host}", command]
        result = subprocess.run(ssh_command, capture_output=True, timeout=10, text=True)
        return {
            "host": host,
            "command": command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0
        }
    except Exception as e:
        return {"host": host, "error": str(e), "success": False}
