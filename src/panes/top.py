# Platform module
import platform

# Subprocess module
import subprocess

# psutil library
import psutil

# Collection library
from collections import deque

# Socket module
import socket

systemName = platform.system()
cores = psutil.cpu_count(logical=False)


# -----------------------------------GET Processor name----------------------------------------

def processorName():
    # Windows OS 
    if systemName == "Windows":
        name = platform.processor()

        # Check if it return something
        return name if name else "Processors Status"


    # Linux OS 
    # it seem platform.processor() does not work for every devices and other module take some type to fecth the data so i decided to use linux build in tools and called it directly and use output instead
    elif systemName == "Linux":
        try:
            result = subprocess.run(
                ["lscpu"],
                capture_output=True,
                text=True
            )
            # there are many lines so i used splitlines() to turn each line into list's value
            for line in result.stdout.splitlines():
                if "Model name" in line:
                    # Split at ":" and make it into list then take the first part and strip the space at the end and at the beginning
                    return line.split(":")[1].strip()
        except Exception:
            return "Error"

    # Macbook OS
    elif systemName == "Darwin":
        try:
            result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True
                    )
            return result.stdout.strip()
        except Exception:
            return "Error"

    return "Processors Status"


# -----------------------------------------CPU Bar----------------------------------------------

def bar(percent: float, totalBlock=50, showPercent=False):
    filled = int((percent * totalBlock) // 100)
    unfilled = totalBlock - filled

    color = "$success" if percent < 60 else ("$warning" if 60 < percent < 80 else "$error")
    unfilledBarcolor = "$secondary"

    filledBlock = f"[{color}]{filled * "▰"}[/{color}]"
    unfilledBlock = f"[{unfilledBarcolor}]{(unfilled) * "▱"}[/{unfilledBarcolor}]"

    coloredPercent = f"[{color}]{percent:<5.1f}[/{color}]"
    if not showPercent:
        return filledBlock + unfilledBlock
    else:
        return f"{filledBlock + unfilledBlock} {coloredPercent}%"

# -------------------------------------CPU Cores status-----------------------------------------

def perCoreDisplay(percents: list[float], width):
    lines = []
    separator = 0
    remainSpace = width - 45 #45 is the total lenght of "right", "left", "|"
    for i in range(remainSpace, 0, -1):
        if i % 2 == 0:
            separator += i // 2
            break
    for i in range(0, len(percents), 2):
        right = f"C{i:<2}: {bar(percents[i], totalBlock=10, showPercent=True)}"
        # to prevent out of bound we will check if the next index is still smaller than the list length
        left = f"C{i+1:<2}: {bar(percents[i+1], totalBlock=10, showPercent=True)}" if i + 1 < len(percents) else ""
        if width > 46:
            lines.append(f"{right}{" "*separator}|{" "*separator}{left}")
        else:
            lines.append(right)
            lines.append(left)

    return "\n".join(lines)


# ------------------------------------------Graph-----------------------------------------------

#BLOCKS = " ▁▂▃▄▅▆▇█"
#
#def renderGraph(history: deque, width: int, height: int, color="cyan") -> str:
#    values = list(history)
#
#    if len(values) < width:
#        values = [0.0] * (width - len(values)) + values
#    else:
#        values = values[-width:]
#
#    rows = []
#    for row in range(height, 0, -1):
#        line = ""
#        threshold = (row / height) * 100
#        prev_threshold = ((row - 1) / height) * 100
#
#        for val in values:
#            if val >= threshold:
#                char = "█"
#            elif val > prev_threshold:
#                fraction = (val - prev_threshold) / (threshold - prev_threshold) char = BLOCKS[max(1, int(fraction * 8))]  # never map to space
#            else:
#                char = "_" if (row == 1 and val > 0) else " "  # floor guarantee
#            line += char
#
#        rows.append(f"[{color}]{line}[/{color}]")
#
#    return "\n".join(rows)


# This graph is base on the actual number and for one full character we got 8 "⣿" dots and so it need the height of 13 at least to reach 100 or 104 to be precise
def renderGraph(history: list, height:int, maxValue: float, colorInput: str="", upsidedown: bool = False):
    dots = ["⢀", "⡀", "⣀", "⣠", "⣰", "⣸","⣼", "⣾","⣿"]
    upsidedownDots = ["⠈", "⠁", "⠉", "⠙", "⠹", "⢹", "⢻", "⢿", "⣿"]
    rows = []
    # prevent division by zero
    if maxValue == 0:
        maxValue = 1
    if not upsidedown:
        for row in range(height, 0, -1):
            line = ""
            for column in history:
                # Convert those percentages using suitable ratio
                percent = (column * (8 * height)) / maxValue
                if colorInput == "":
                    color = "$success" if percent < 60 else ("$warning" if 60 < percent < 80 else "$error")
                else:
                    color = colorInput
                start = (percent // 8) + 1
                peak = int(percent % 8)

                if row == start:
                    # we don't want "-" to be on the peak
                    if peak == 0 and start > 1:
                        line += " "
                    else:
                        line += f"[{color}]{dots[peak]}[/{color}]"

                elif row < start:
                    line += f"[{color}]{dots[-1]}[/{color}]"

                else:
                    line += " "

            rows.append(line)
    else:
        for row in range(1, height + 1):
            line = ""
            for column in history:
                percent = (column * (8 * height)) / maxValue
                if colorInput == "":
                    color = "$success" if percent < 60 else ("$warning" if 60 < percent < 80 else "$error")
                else:
                    color = colorInput
                end = (percent // 8) + 1
                peak = int(percent % 8)

                if row == end:
                    if peak == 0 and end > 1:
                        line += " "
                    else:
                        line += f"[{color}]{upsidedownDots[peak]}[/{color}]"

                elif row < end:
                    line += f"[{color}]{upsidedownDots[-1]}[/{color}]"

                else:
                    line += " "
                    
            rows.append(line)

    return "\n".join(rows)
        



# ------------------------------------------Tank-----------------------------------------------


def renderTank(ram: float, height: int, width: int):
    rows = []
    maxBlock = height * width
    filled = (ram * (maxBlock)) / 100
    start = int(filled / width) + 1
    remain = int(filled % width)
    color = "$success" if filled/maxBlock < 0.6 else ("$warning" if 0.6 < filled/maxBlock < 0.8 else "$error")

    for row in range(height, 0, -1):
        line = ""
        if row == start:
            line += f"[{color}]{"⣿" * remain}[/][$primary]{"⣿" * (width - remain)}[/]"
        elif row < start:
            line += f"[{color}]{"⣿" * width}[/]"
        else:
            line += f"[$primary]{"⣿" * width}[/]"
        rows.append(line)

    return "\n".join(rows)



# ------------------------------------------DISK-----------------------------------------------

def speedPerSecond(value1: int, value2: int, time1: float, time2: float):
    elapsed = time2 - time1
    valueInps = (value2 - value1) / elapsed
    return valueInps



def getUnit(value:float):
    units  = ["", "K", "M", "G", "T"]
    # we want to return it as su"the levels of branchitable unit
    for i in range(1, len(units) + 1):
        readSize = value / (1024 ** i)
        if readSize < 1000:
            return f"{readSize:<5.1f}{units[i]}"
        elif readSize >= 1000 and i == len(units):
            # we will return it as our biggest unit even if it more than that
            return f"{readSize:<5.1f}{units[i]}"

# All the unnecessary stuff we don't need 
SKIP_FS = {"tmpfs", "devtmpfs", "squashfs", "overlay", "proc", "sysfs", "efivarfs"}





# TODO: Create a fucntion that return disk information as dictionary
def getDiskInfo(partition) -> dict:
    return {}










# ------------------------------------------NETWORK-----------------------------------------------

# TODO: Create a fucntion that return net information as dictionary
def getNetInfo() -> list:
    return []



