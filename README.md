# SysTUI

**SysTUI** is a real-time, terminal-based system monitoring dashboard built entirely in Python. It runs directly in the command-line interface and displays live system metrics that refresh every second without scrolling or flickering. The dashboard covers CPU usageper core, memory and swap utilization, disk read/write throughput, network traffic per interface, and a live process table sorted by resource consumption.

Beyond the live display, SysTUI includes a snapshot logger that records system statistics to a JSON file over time, and a command-line interface that lets users configure thetool's behavior at startup.

# To Do List

## Take arguments from command line

- [ ] Use argparse to take argument and return information accordingly. ex: `systui -v` return app version.

## src/panes/top

### Network

- [ ] Create a fucntion `def getNetInfo() -> list:` that return a list of all NIC as dictionaries. **1 dictionary per NIC**. each dictionary need to have the following information as a key:
```
"name",
"Status"
"Speed in MBps"
"MTU"
"Duplex"
"IPv4"
"IPv6"
"MAC"
"Packets sent"
"Packets receive"
"Errors in"
"Errors out"
"Drops in"
"Drops out"
```

### Disk

- [ ] Create a fucntion that return disk information base on the partition argument `def getDiskInfo(partition) -> list:`. Partition argument is from `psutil.disk_partitions()`, you can check our this psutil function first. So basically we take one of the `psutil.disk_partitions()` values and put into the function then the function need to return values as a dictionary with the following as a keys:

```
"Mount"
"FS" 
"Total"
"Used" 
"Free"
```

