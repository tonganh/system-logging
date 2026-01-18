# System Monitoring Tool

A lightweight Python-based tool to monitor system resources (CPU, Memory, Disk) and network connectivity. This tool is designed to help diagnose server issues by logging performance metrics and connectivity states, which is useful for post-mortem analysis when a server becomes unreachable.

## Problem Statement
Servers occasionally become unresponsive or inaccessible via SSH. Without logs, it is difficult to determine if the cause was resource exhaustion (OOM, high CPU) or network failure.

## Solution
This background script periodically collects system metrics and checks for internet connectivity. If dangerous thresholds are breeched, it logs detailed process information to help identify the culprit.

## Metrics Monitored

1.  **CPU**:
    - Usage Percentage (Global)
    - Load Average (1, 5, 15 min)
2.  **Memory**:
    - Total, Available, Used, Free
    - Percentage Used
3.  **Disk**:
    - Root partition usage
4.  **Network**:
    - Internet connectivity check (Ping 8.8.8.8)

## Features
- **Structured Logging**: Active logs are saved to `logs/system_monitor.log`.
- **Log Rotation**: automatic daily rotation. At midnight, the current log is renamed (e.g., `system_monitor.log.2023-10-27`) and a new file is started.
- **Alerting**: Captures top processes by CPU/Memory when usage exceeds 90%.

## Prerequisites
- Python 3.6+
- `psutil` library

## Installation & Usage

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Monitor**
    ```bash
    python3 monitor.py &
    ```
    *Note: Run with `nohup` or `screen`/`tmux` for session persistence, or configure as a systemd service.*

3.  **Run with Docker (Recommended)**
    ```bash
    docker compose up -d --build
    ```
    This will start the monitor in a container with `pid: host` mode to accurately monitor the host's processes. Logs will be available in the local `logs/` directory.

## Output Format
Logs are written in the following format:
```
2023-10-27 10:00:00,000 [INFO] CPU: 15.2% | RAM: 45.1% | DISK: 22.0% | NET: OK
```
Warnings will include process details:
```
2023-10-27 10:05:00,000 [WARNING] High CPU (95%) detected! Top processes:
...
```
