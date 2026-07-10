# WinPulse ⚡

A lightweight, blazingly fast cross-platform system metric telemetry engine for Python. Natively pulls system stats in milliseconds with zero heavy dependencies.

## Features

- **Cross-Platform Support**: Identical API performance across Windows, Linux, and macOS.
- **Ultra Lightweight**: Zero bulky external package dependencies. Uses fast, consolidated native shell execution blocks.
- **Accurate Telemetry**: Tracks true physical CPU core boundaries, memory utilization scales, and process loads safely.

## Installation

```bash
pip install winpulse

import json
from winpulse import WinPulse

# Initialize the engine
pulse = WinPulse()

# Retrieve dynamic system metrics
details = pulse.get_all_system_details()
print(json.dumps(details, indent=4))