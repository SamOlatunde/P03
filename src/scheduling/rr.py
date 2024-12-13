from collections import deque
from pathlib import Path 
import cpu_jobs as c
from datetime import datetime

class Process:
    """
    Represents a process in a scheduling simulation. Each process has attributes 
    such as arrival time, priority, number of bursts, and a current state. 
    It also tracks the current burst being executed, as well as performance metrics 
    like wait time and turnaround time.

    Attributes:
        arrival_time (int): The time when the process arrives in the system.
        pid (int): Unique identifier for the process.
        priority (int): The priority of the process, where lower values indicate higher priority.
        num_bursts (int): The number of bursts to be executed by the process.
        current_burst (dict): Details about the current burst, including type and duration.
        state (str): The current state of the process. Possible states are:
                     "NEW", "READY", "RUNNING", "WAITING", "TERMINATED".
        completed (bool): Indicates whether all bursts have been executed.
        wait_time (int): The total time the process has spent waiting in the ready queue.
        turnaround_time (int): The total time the process spends in the system from arrival to termination.
    """
    def __init__(self, arrival_time, pid, priority, num_bursts):
        self.arrival_time = arrival_time  # When process arrives in the system
        self.pid = pid  # Process ID
        self.priority = priority  # Process priority
        self.num_bursts = num_bursts  # number of burst to be executed 
        self.current_burst= {}  # Tracks current burst being executed includes, id, type and duration 
        self.state = "NEW"  # States: NEW, READY, RUNNING, WAITING, TERMINATED
        self.completed = False  # True if all bursts are complete
        self.wait_time = 0
        self.turnaround_time = 0 # 


    def is_cpu_burst(self):
        return self.current_burst["burst_type"] == "CPU"

    def next_burst(self, client_id, session_id, clock):
        """
        Retrieve and set the next burst for the process. If the burst is the last one, mark the process as completed.

        Args:
            client_id (str): Client ID for the session.
            session_id (str): Session ID for the session.
            clock (int): The current clock time.

        Returns: Nothing 
        """
        # get next burst 
        response = c.getBurst(client_id, session_id, self.pid)

        if not response or "data" not in response:
            raise ValueError("next_burst function: Failed to retrieve burst data.")
    
        # set the current burst of the process 
        self.current_burst = response["data"] 
        
        # set completed to true if its the last burst, no duration involed   
        if response["data"]["burst_type"] == "EXIT":
            self.completed = True
            # compute time spent in the system 
            self.turnaround_time = clock - self.arrival_time

        # Decrement the number of bursts remaining, ensuring it doesn't go negative
        self.num_bursts = max(0, self.num_bursts - 1)

    def proceed_burst(self, client_id, session_id, clock): 
        """
        Proceed with the current burst by decrementing its duration. If the burst is complete, transition to the next burst.

        Args:
            client_id (str): The client ID for the session.
            session_id (str): The session ID for the current session.
            clock (int): The current clock time.

        Raises:
            ValueError: If the current burst is invalid or not set.

        Returns:
            bool: True if the current burst is complete and the process is ready for the next burst, False otherwise.
        """
        if not self.current_burst or "duration" not in self.current_burst:
            raise ValueError("proceed_burst: Current burst is invalid or not set.")
        
        # reduce the duration of current burst every clock tick 
        self.current_burst["duration"] -= 1 
        

        # If the current burst is complete, move to the next burst
        if self.current_burst["duration"] == 0:
            self.next_burst(client_id, session_id, clock)
            # this would notifty calling function that current burst has finished.
            # calling function would remove the process from the running queue  
            return True 
        
        return False
        """ removing this cuz it needs to be controlled from main 
        # If the current burst is complete, move to the next burst
        if self.current_burst["duration"] == 0:
            self.next_burst(client_id, session_id, clock)
        """


    def update_state(self, new_state):
        self.state = new_state

    def __str__(self):
        return (f"Arrival: {self.arrival_time}, "
                f"PID: {self.pid}, State: {self.state}, "
                f"Priority: {self.priority}, "
                f"Completed: {self.completed}")


class CPU:
    """
    Represents a CPU in a scheduling simulation. Each CPU can handle one job at a time, 
    track its active and idle times, and maintain a count of completed jobs.

    Attributes:
        id (int): Unique identifier for the CPU.
        current_job (Process or None): The process currently assigned to the CPU. 
                                       None if the CPU is idle.
        active_time (int): Total time the CPU has spent processing jobs.
        idle_time (int): Total time the CPU has been idle (not processing any jobs).
        completed_jobs (int): The total number of jobs the CPU has completed.

    Methods:
        assign_job(job):
            Assigns a job (process) to the CPU.
        
        process_job(clock):
            Processes the current job if one is assigned. Updates active or idle 
            time and increments the count of completed jobs if the current job 
            finishes its burst.
    """
    def __init__(self, id):
        self.id = id
        self.current_job = None  # The process/job assigned to this CPU
        self.active_time = 0     # Total time CPU has been active
        self.idle_time = 0       # Total time CPU has been idle
        self.completed_jobs = 0  # Count of jobs completed by this CPU

    def assign_job(self, job):
        self.current_job = job

    """def process_job(self, client_id, session_id, clock):
        if self.current_job:
            self.current_job.proceed_burst(client_id, session_id, clock)
            self.active_time += 1
            if self.current_job.current_burst["duration"] == 0:
                self.completed_jobs += 1
                self.current_job = None
        else:
            self.idle_time += 1"""



def parse_input_file(file_path):
    """
    Parses an input file and loads the processes into a queue.

    Args:
        file_path (str or Path): Path to the input file.

    Returns:
        deque: A queue containing Process objects.
    """
    process_queue = deque()
    
    file_path = Path(file_path)  # Ensure file_path is a Path object

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                parts = line.split(' ')
                
                # Parse process attributes
                arrival_time = int(parts[0].strip())
                pid = int(parts[1].strip())
                priority = int(parts[2].strip())
                
                bursts = []
                #load the rest of  lists into burst 
                for p in parts[3:]:
                    stripped_p = p.strip()
                    bursts.append(int(stripped_p))
              

                # Create a Process instance and add it to the queue
                process = Process(arrival_time, pid, priority, bursts)
                process_queue.append(process)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")

    return process_queue

def round_robin(running_queue, readyQ, time_quantum):
    """
    Implements the Round Robin (RR) scheduling algorithm.

    Args:
        running_queue (list): A list of CPU objects representing the running CPUs.
        readyQ (deque): A deque containing the processes ready for execution.
        time_quantum (int): The fixed time quantum for each process.

    Returns:
        None
    """
    print("Running Round Robin Scheduling!!!")

    for cpu in running_queue:
        # If the CPU is idle (current_job is None)
        if not cpu.current_job:
            if readyQ:
                # Assign the next job from the ready queue to the CPU
                job = readyQ.popleft()
                cpu.assign_job(job)
                cpu.current_job.remaining_time = min(time_quantum, job.current_burst["duration"])
                cpu.current_job.update_state("RUNNING")
                print(f"Assigned Job {job.pid} to CPU {cpu.id} with time quantum {time_quantum}.")
        else:
            # Decrement the remaining time for the job on this CPU
            cpu.current_job.remaining_time -= 1
            cpu.current_job.current_burst["duration"] -= 1

            # Check if the job's current burst is complete
            if cpu.current_job.current_burst["duration"] == 0:
                print(f"Job {cpu.current_job.pid} completed its burst on CPU {cpu.id}.")
                cpu.current_job.next_burst(client_id, session_id, clock)

                if cpu.current_job.completed:
                    cpu.current_job.update_state("TERMINATED")
                    terminatedQ.append(cpu.current_job)
                    print(f"Job {cpu.current_job.pid} has been terminated.")
                elif cpu.current_job.is_cpu_burst():
                    cpu.current_job.update_state("READY")
                    readyQ.append(cpu.current_job)
                    print(f"Job {cpu.current_job.pid} added back to ready queue.")
                else:
                    cpu.current_job.update_state("WAITING")
                    waitingQ.append(cpu.current_job)
                    print(f"Job {cpu.current_job.pid} moved to waiting queue for I/O.")
                cpu.current_job = None  # Free up the CPU
            elif cpu.current_job.remaining_time == 0:
                # Time quantum expired, preempt the job
                print(f"Job {cpu.current_job.pid} preempted on CPU {cpu.id}.")
                cpu.current_job.update_state("READY")
                readyQ.append(cpu.current_job)  # Add back to the ready queue
                cpu.current_job = None  # Free up the CPU


def printAg(filename, algorithm_type, num_cpus, terminatedQ, running_queue, start_clock, end_time):
    """
    Prints the results of the scheduling algorithm execution to a file.

    Args:
        filename (str): The name of the output file.
        algorithm_type (str): The type of scheduling algorithm used.
        num_cpus (int): The number of CPUs in the system.
        terminatedQ (deque): A deque containing the processes that have completed execution.
        start_clock (int): The simulation's start time.
        end_time (int): The simulation's end time.

    Returns:
        None
    """
    # Calculate total time
    total_time = end_time - start_clock

    # Throughput: Number of jobs completed per unit of time
    throughput = len(terminatedQ) / total_time if total_time > 0 else 0

    # Collect CPU utilization metrics
    total_cpu_time = total_time * num_cpus
    active_time = sum(cpu.active_time for cpu in running_queue)  
    cpu_utilization = (active_time / total_cpu_time) * 100 if total_cpu_time > 0 else 0

    # Fairness: Standard deviation of CPU times for all jobs
    job_times = [job.turnaround_time for job in terminatedQ]
    if len(job_times) > 1:
        mean_turnaround = sum(job_times) / len(job_times)
        fairness = (sum((x - mean_turnaround) ** 2 for x in job_times) / len(job_times)) ** 0.5
    else:
        fairness = 0  # Fairness not applicable with one or no jobs

    # Write results to file
    try:
        with open(filename, "w") as file:
            file.write(f"Scheduling Algorithm: {algorithm_type}\n")
            file.write(f"Number of CPUs: {num_cpus}\n")
            file.write(f"Total Simulation Time: {total_time}\n")
            file.write(f"Throughput: {throughput:.2f} jobs/unit time\n")
            file.write(f"CPU Utilization: {cpu_utilization:.2f}%\n")
            file.write(f"Fairness (Turnaround Time Std Dev): {fairness:.2f}\n\n")
            file.write("Terminated Jobs:\n")
            file.write(f"{'PID':<10}{'Arrival':<10}{'Priority':<10}{'Turnaround Time':<20}\n")
            file.write("=" * 50 + "\n")
            for job in terminatedQ:
                file.write(
                    f"{job.pid:<10}{job.arrival_time:<10}{job.priority:<10}{job.turnaround_time:<20}\n"
                )
        print(f"Results successfully written to {filename}.")
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")


if __name__ == '__main__':
    ag_path = Path(__file__).resolve().parent.parent.parent / "aggregate"
    ag_path.mkdir(parents=True, exist_ok=True)

    num_cpus = 4
    running_queue = [CPU(id=i) for i in range(num_cpus)]
    readyQ, waitingQ, terminatedQ = deque(), deque(), deque()

    algorithm_type = 'Round Robin'
    config = c.getConfig(0)
    response = c.init(config)
    client_id, session_id = config["client_id"], response["session_id"]
    start_clock, clock = response['start_clock'], response['start_clock']
    time_quantum = response.get("time_slice", 4)

    max_simulation_time = 10000

    while True:
        jobs_left = c.getJobsLeft(client_id, session_id)

        if jobs_left == 0 and not readyQ and not any(cpu.current_job for cpu in running_queue):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = ag_path / f"results_{timestamp}.txt"
            printAg(filename, algorithm_type, num_cpus, terminatedQ, running_queue, start_clock, clock)
            break

        response = c.getJob(client_id, session_id, clock)
        if response and response["success"]:
            for data in response["data"]:
                process = Process(
                    data["arrival_time"], data["job_id"], data["priority"],
                    c.getBurstsLeft(client_id, session_id, data["job_id"])
                )
                process.next_burst(client_id, session_id, clock)
                (readyQ if process.is_cpu_burst() else waitingQ).append(process)

        round_robin(running_queue, readyQ, time_quantum)

        for process in list(waitingQ):
            if process.proceed_burst(client_id, session_id, clock):
                waitingQ.remove(process)
                if process.completed:
                    process.update_state("TERMINATED")
                    terminatedQ.append(process)
                elif process.is_cpu_burst():
                    process.update_state("READY")
                    readyQ.append(process)

        clock += 1
        if clock - start_clock > max_simulation_time:
            print("Max simulation time reached. Terminating.")
            break
