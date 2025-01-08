# CPU Scheduling Simulator

## Overview

This project simulates various CPU scheduling algorithms to manage and execute processes efficiently. It models how processes transition between different states (e.g., ready, running, waiting) and tracks key metrics like CPU utilization, throughput, and fairness. The project supports multiple scheduling algorithms, including **First-Come, First-Served (FCFS)**, **Round Robin (RR)**, **Priority Scheduling**, and **Multi-Level Feedback Queue (MLFQ)**.

## Features

- **Multiple Scheduling Algorithms**:
  - **FCFS**: Processes are scheduled in the order of their arrival.
  - **Round Robin**: Time-sharing algorithm with a configurable time quantum.
  - **Priority Scheduling**: Processes are scheduled based on their priority.
  - **Multi-Level Feedback Queue (MLFQ)**: Processes move between multiple queues based on execution history and behavior.
- **Multi-CPU Support**:
  - Simulate multiple CPUs working concurrently.
- **Process State Transitions**:
  - Processes move between `READY`, `RUNNING`, `WAITING`, and `TERMINATED` states based on their current bursts.
- **Metrics Collection**:
  - **Throughput**: Number of completed jobs per unit time.
  - **CPU Utilization**: Percentage of time CPUs are active.
  - **Fairness**: Standard deviation of turnaround times.

---

## Project Structure

```plaintext
.
├── src/
│   ├── scheduling/
│   │   ├── cpu.py          # CPU class handling job execution
│   │   ├── process.py      # Process class representing individual jobs
│   │   ├── algorithms.py   # Implementation of scheduling algorithms
│   │   └── simulation.py   # Main simulation logic
│   └── utils/
│       ├── io.py           # Input/output utilities for file handling
│       └── metrics.py      # Functions for calculating performance metrics
├── aggregate/              # Output files with simulation results
├── test/                   # Test cases for algorithms and components
└── README.md               # Project documentation
```

---

## Setup

### Requirements

- **Python 3.8+**
- Required Libraries:
  - `collections`
  - `pathlib`
  - `datetime`
  - `requests` (if external API calls are used)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cpu-scheduling-simulator.git
   cd cpu-scheduling-simulator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the Simulation**:
   ```bash
   python src/simulation.py
   ```

2. **Choose Scheduling Algorithm**:
   - Modify the `algorithm_type` variable in the simulation to use your desired algorithm:
     - `FCFS`, `Round Robin`, `Priority`, or `MLFQ`.

3. **Generate Results**:
   - Simulation results are saved in the `aggregate/` directory with a timestamped filename.

---

## Supported Scheduling Algorithms

### First-Come, First-Served (FCFS)
- **Type**: Non-preemptive.
- **Behavior**: Processes are scheduled in the order they arrive.
- **Use Case**: Simple, but may cause long waiting times for longer processes.

### Round Robin (RR)
- **Type**: Preemptive.
- **Behavior**: Time-sharing algorithm with a fixed time quantum.
- **Use Case**: Fair for processes of varying lengths, minimizes starvation.

### Priority Scheduling
- **Type**: Non-preemptive.
- **Behavior**: Processes are scheduled based on priority (lower value = higher priority).
- **Use Case**: Prioritizes critical tasks but can lead to starvation of low-priority tasks.

### Multi-Level Feedback Queue (MLFQ)
- **Type**: Preemptive and Adaptive.
- **Behavior**:
  - Multiple queues with varying priority levels.
  - Jobs move between queues based on execution history:
    - Long-running processes are demoted to lower-priority queues.
    - Short-running processes are promoted for faster execution.
- **Use Case**: Balances responsiveness and throughput by dynamically adjusting priorities.

---

## How It Works

1. **Initialization**:
   - Processes are loaded into the `ready queue`.
   - CPUs are initialized to simulate a multi-core environment.

2. **Scheduling**:
   - The selected scheduling algorithm determines which process is assigned to each CPU.

3. **Multi-Level Feedback Queue**:
   - Processes start in the highest-priority queue.
   - If a process exceeds its time quantum, it is demoted to a lower-priority queue.
   - Lower-priority queues use larger time quantums to favor I/O-bound processes.

4. **Metrics Calculation**:
   - Metrics like throughput, CPU utilization, and fairness are calculated at the end of the simulation.

5. **Output**:
   - Results are saved to a timestamped file for analysis.

---

## Metrics

### **Example Output**

#### Simulation Configuration
- Number of CPUs: 4
- Algorithm: Round Robin
- Time Quantum: 4

#### Metrics
```plaintext
Scheduling Algorithm: Round Robin
Number of CPUs: 4
Total Simulation Time: 120
Throughput: 10.00 jobs/unit time
CPU Utilization: 85.00%
Fairness (Turnaround Time Std Dev): 2.35

Terminated Jobs:
PID       Arrival    Priority   Turnaround Time
==============================================
101       0          2          45
102       3          1          30
103       5          3          50
```

---



## Contact

For questions or feedback, feel free to reach out:
- **Email**: psalmyz735@gmail.com
```

