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
                
            elif self.os_name == "Linux":
                # Consolidated single-shot Bash terminal string
                cmd = ("echo '{"
                       "\"cpu_company_name\": \\\"$(lscpu | grep \"Model name\" | cut -d: -f2 | xargs)\\\", "
                       "\"physical_cores\": $(lscpu | grep \"Core(s) per socket\" | awk \"{print \\$4}\"), "
                       "\"cpu_percentage_use\": $(vmstat 1 2 | tail -1 | awk \"{print 100 - \\$15}\"), "
                       "\"ram_total_gb\": $(free -g | awk \"/^Mem:/ {print \\$2}\"), "
                       "\"ram_available_gb\": $(free -g | awk \"/^Mem:/ {print \\$7}\")"
                       "}'")
                
            elif self.os_name == "Darwin":  # macOS
                # Consolidated native Zsh query mapping Apple hardware controllers
                cmd = ("echo '{"
                       "\"cpu_company_name\": \\\"$(sysctl -n machdep.cpu.brand_string)\\\", "
                       "\"physical_cores\": $(sysctl -n hw.physicalcpu), "
                       "\"cpu_percentage_use\": $(ps -A -o %cpu | awk \"{s+=\\$1} END {print s}\"), "
                       "\"ram_total_gb\": $(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024)), "
                       "\"ram_available_gb\": $(($(vm_stat | awk \"/Pages free/ {print \\$3}\" | sed \"s/\\\\.//\") * 4096 / 1024 / 1024 / 1024))"
                       "}'")
            else:
                return {"error": "Unsupported Operating System"}

            # Fire the single terminal execution
            raw_output = subprocess.check_output(cmd, shell=True).decode().strip()
            dynamic_data = json.loads(raw_output)

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
