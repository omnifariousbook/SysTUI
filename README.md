# SysTUI

**SysTUI** is a real-time, terminal-based system monitoring dashboard built entirely in Python. It runs directly in the command-line interface and displays live system metrics that refresh every second without scrolling or flickering. The dashboard covers CPU usageper core, memory and swap utilization, disk read/write throughput, network traffic per interface, and a live process table sorted by resource consumption.

Beyond the live display, SysTUI includes a snapshot logger that records system statistics to a JSON file over time, and a command-line interface that lets users configure thetool's behavior at startup.


## Dependencies

- psutil
- rich
- argparse
- json
- os / datetime

## Requirements

- Python 3.8+

## License

MIT
