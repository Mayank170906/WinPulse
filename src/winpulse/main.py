import subprocess
import platform
import json
import os
class WinPulse:
    def __init__(self):
        # 1. Immediate Static Meta Data (Instant execution via Python standard library)
        self.os_name = platform.system()               # Windows, Linux, Darwin
        self.architecture = platform.machine()         # AMD64, x86_64, arm64
        self.logical_cores = os.cpu_count() or 1       # Always reports 12 on your Ryzen 5 5600H

    def get_all_system_details(self):
        """
        Fires exactly ONE fast native shell command per OS to fetch all remaining dynamic metrics 
        such as true physical cores, company name, CPU usage, and total/available RAM.
        """
        try:
            if self.os_name == "Windows":
                # Single-line PowerShell pipeline outputting structured JSON
                cmd = ("powershell -Command \""
                       "$cpu = Get-CimInstance Win32_Processor; "
                       "$osInfo = Get-CimInstance Win32_OperatingSystem; "
                       "$cpuUsage = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; "
                       "$totalRam = $osInfo.TotalVisibleMemorySize * 1024; "
                       "$freeRam = $osInfo.FreePhysicalMemory * 1024; "
                       "@{cpu_company_name=$cpu.Name.Trim(); "
                       "physical_cores=$cpu.NumberOfCores; "
                       "cpu_percentage_use=[math]::Round($cpuUsage, 1); "
                       "ram_total_gb=[math]::Round($totalRam / 1GB, 1); "
                       "ram_available_gb=[math]::Round($freeRam / 1GB, 1)} "
                       "| ConvertTo-Json\"")
                
                # Execute and parse JSON directly inside the Windows block
                raw_output = subprocess.check_output(cmd, shell=True).decode().strip()
                dynamic_data = json.loads(raw_output)
                
            elif self.os_name == "Linux":
                # Safe Linux flat token execution separated by pipes
                cmd = ("echo \"$(lscpu | grep 'Model name:' | cut -d: -f2 | xargs)|"
                       "$(lscpu | grep 'Core(s) per socket:' | awk '{print $4}')|"
                       "$(vmstat 1 2 | tail -1 | awk '{print 100 - $15}')|"
                       "$(free -m | awk '/^Mem:/ {print $2}')|"
                       "$(free -m | awk '/^Mem:/ {print $7}')\"")
                
                raw_output = subprocess.check_output(cmd, shell=True).decode().strip()
                parts = raw_output.split('|')
                
                # Math translation converting MB allocations to clean float GB metrics
                tot_gb = round(int(parts[3]) / 1024, 1) if parts[3].isdigit() else 0.0
                avail_gb = round(int(parts[4]) / 1024, 1) if parts[4].isdigit() else 0.0
                
                dynamic_data = {
                    "cpu_company_name": parts[0],
                    "physical_cores": int(parts[1]) if parts[1].isdigit() else self.logical_cores,
                    "cpu_percentage_use": parts[2],
                    "ram_total_gb": tot_gb,
                    "ram_available_gb": avail_gb
                }                
            elif self.os_name == "Darwin":  # macOS
                # Safe Mac Zsh single line telemetry extraction separated by pipes
                cmd = ("echo \"$(sysctl -n machdep.cpu.brand_string)|"
                       "$(sysctl -n hw.physicalcpu)|"
                       "$(ps -A -o %cpu | awk '{s+=$1} END {print s}')|"
                       "$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))|"
                       "$(($(vm_stat | awk '/Pages free/ {print $3}' | tr -d '.') * 4096 / 1024 / 1024 / 1024))\"")
                
                raw_output = subprocess.check_output(cmd, shell=True).decode().strip()
                parts = raw_output.split('|')
                
                mac_usage = round(float(parts[2]) / self.logical_cores, 1) if parts[2] else 0.0
                
                dynamic_data = {
                    "cpu_company_name": parts[0],
                    "physical_cores": int(parts[1]) if parts[1].isdigit() else self.logical_cores,
                    "cpu_percentage_use": mac_usage,
                    "ram_total_gb": parts[3],
                    "ram_available_gb": parts[4]
                }            
            else:
                return {"error": "Unsupported Operating System"}

            # Combine everything cleanly into your final flat output dictionary
            return {
                "os_name": self.os_name,
                "architecture": self.architecture,
                "cpu_company_name": dynamic_data.get("cpu_company_name"),
                "physical_cores": dynamic_data.get("physical_cores"),
                "logical_cores": self.logical_cores,
                "cpu_percentage_use": f"{dynamic_data.get('cpu_percentage_use')}%",
                "ram_total": f"{dynamic_data.get('ram_total_gb')} GB",
                "ram_available": f"{dynamic_data.get('ram_available_gb')} GB"
            }

        except Exception as e:
            return {"error": f"Failed to gather system telemetry: {str(e)}"}