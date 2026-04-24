# Platform module
import platform

# psutil library
import psutil

# Datetime module
import datetime




def getSysInfo():
    nodeName = platform.node()
    machine = platform.machine()
    system = platform.platform()
    version = platform.version()
    pythonVersion = platform.python_version()

    return f"""\
[$secondary]{"Node":<8}[/]: {nodeName}

[$secondary]{"System":<8}[/]: {system}

[$secondary]{"Version":<8}[/]: {version}

[$secondary]{"Uptime":<8}[/]: {upTime()}

[orange]{"Python":<8}[/]: {pythonVersion}
"""

def upTime():
    bootTime = psutil.boot_time()
    # contain decimal point e.g. 12:26:46.709660
    findUptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(bootTime)
    return str(findUptime).split(".")[0]

def logUpdate(cpuOverall: float, memOverall: float, swapOverall: float):
    log = ""
    cpu = "[underline]CPU[/]:\n\n"
    mem = "[underline]MEMORY[/]:\n\n"
    swap = "[underline]SWAP MEMORY[/]:\n\n"
    # check cpu usage
    if cpuOverall < 60:
        cpu += f"- [$success]Normal[/]: Low CPU usage ({cpuOverall}%)\n\n"
    elif 60 < cpuOverall < 80:
        cpu += f"- [$warning]Caution[/]: Mederate CPU usage ({cpuOverall}%)\n\n"
    elif cpuOverall > 80:
        cpu += f"- [$error]Warning[/]: High CPU usage ({cpuOverall}%)\n\n"
    log += cpu

    if memOverall < 60:
        mem += f"- [$success]Normal[/]: Low Memory usage ({memOverall}%)\n\n"
    elif 60 < memOverall < 80:
        mem += f"- [$warning]Caution[/]: Mederate Memory usage ({memOverall}%)\n\n"
    elif memOverall > 80:
        mem += f"- [$error]Warning[/]: High Memory usage ({memOverall}%)\n\n"
    log += mem

    if swapOverall == 0:
        swap += f"- Swap unused ({swapOverall}%)\n\n"
    elif 0 < swapOverall < 60:
        swap += f"- [$success]Normal[/]: Low Swap memory usage ({swapOverall}%)\n\n"
    elif 60 < swapOverall < 80:
        swap += f"- [$warning]Caution[/]: Mederate Swap memory usage ({swapOverall}%)\n\n"
    elif swapOverall > 80:
        swap += f"- [$error]Warning[/]: High Swap memory usage ({swapOverall}%)\n\n"
    log += swap
 
    return log




