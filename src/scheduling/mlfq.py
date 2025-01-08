from collections import deque
import cpu_jobs
from collections import deque
from pathlib import Path 
import cpu_jobs as c
from datetime import datetime
from rich.console import Console
from rich.table import Table
import time


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
        self.remaining_time (int) : used in preemptive scheduling
        self.cpu_burst_accumulator (int) : keeps track of number of cpu bursts 
    """
    def __init__(self, arrival_time, pid, priority, num_bursts):
        self.arrival_time = arrival_time  # When process arrives in the system
        self.pid = pid  # Process ID
        self.priority = priority  # Process priority
        self.num_bursts = num_bursts  # number of burst to be executed 
        self.current_burst= {}  # Tracks current burst being executed includes, id, type and duration 
        self.state = "NEW"  # States: NEW, READY, RUNNING, WAITING, TERMINATED
        self.completed = False  # True if all bursts are complete
        self.wait_time = 0 # track wait time 
        self.turnaround_time = 0 # total time, process spends in system 
        self.remaining_time = 0 # used in round robin  for premeption
        self.cpu_burst_accumulator = 0 # sums up all cpu bursts 


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
        
        # update the burst accumulator if its a cpu burst 
        if self.is_cpu_burst():
            self.cpu_burst_accumulator += self.current_burst["duration"]
            
        # set completed to true if its the last burst, no duration involed   
        if response["data"]["burst_type"] == "EXIT":
            self.completed = True

            # compute time spent in the system 
            self.turnaround_time = clock - self.arrival_time

            # compute wait_time  = turnaround_time - burst_time
            self.wait_time = self.turnaround_time - self.cpu_burst_accumulator


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

class IO:
    """
    Represents an I/O device in a scheduling simulation. Each I/O device can handle one job at a time,
    track its active and idle times, and maintain a count of completed I/O operations.

    Attributes:
        id (int): Unique identifier for the I/O device.
        current_job (Process or None): The process currently assigned to the I/O device.
                                       None if the device is idle.
        active_time (int): Total time the I/O device has spent processing jobs.
        idle_time (int): Total time the I/O device has been idle (not processing any jobs).
        completed_io_operations (int): The total number of I/O operations the device has completed.

    Methods:
        assign_job(job):
            Assigns a job (process) to the I/O device.
        
        process_io(clock):
            Processes the current job if one is assigned. Updates active or idle
            time and increments the count of completed I/O operations if the current job
            finishes its I/O burst.
    """
    def __init__(self, id):
        self.id = id
        self.current_job = None  # The process/job assigned to this I/O device
        self.active_time = 0     # Total time the I/O device has been active
        self.idle_time = 0       # Total time the I/O device has been idle
        self.completed_io_operations = 0  # Count of completed I/O operations

    def assign_job(self, job):
        """
        Assigns a job (process) to the I/O device.

        Args:
            job (Process): The job to assign to the I/O device.
        """
        self.current_job = job

    
 
def print_queues(clock_tick, ready_queues, running_queue, waitingQ, io_devices, terminatedQ, algorithm_type):
    """
    Prints a table of processes in each queue at the current clock tick.

    Args:
        clock_tick (int): The current simulation clock tick.
        ready_queues (list of deque): List of ready queues for different priority levels.
        running_queue (list): The list of CPU objects representing the running queue.
        waitingQ (deque): The queue of processes waiting for I/O devices.
        io_devices (list): The list of IO devices and their current jobs.
        terminatedQ (deque): The queue of terminated processes.
        algorithm_type (str): The name of the scheduling algorithm being used.
    """
    console = Console()
    console.clear()

    # Create the main table
    table = Table(title=f"{algorithm_type}: Process Queues at Clock Tick {clock_tick}")
    table.add_column("Queues", style="cyan", no_wrap=True)
    table.add_column("Processes", style="cyan")

    # Process ready queues for MLFQ
    ready_queues_display = []
    for priority, queue in enumerate(ready_queues):
        if queue:
            queue_ids = [str(proc.pid) for proc in queue]
            ready_queues_display.append(f"Priority {priority}: {', '.join(queue_ids)}")
        else:
            ready_queues_display.append(f"Priority {priority}: Empty")
    ready_ids = "\n".join(ready_queues_display) if ready_queues_display else "Empty"

    # Convert the running queue (list of CPU objects)
    running_ids_list = [
        f"CPU{cpu.id}:{cpu.current_job.pid}" if cpu.current_job else f"CPU{cpu.id}:Idle"
        for cpu in running_queue
    ]
    running_ids = ", ".join(running_ids_list) if running_ids_list else "Empty"

    # Convert the I/O devices queue
    io_ids_list = [
        f"IO{io_device.id}:{io_device.current_job.pid}" if io_device.current_job else f"IO{io_device.id}:Idle"
        for io_device in io_devices
    ]
    io_ids = ", ".join(io_ids_list) if io_ids_list else "Empty"

    # Convert the waiting queue
    waiting_ids_list = [str(proc.pid) for proc in waitingQ] if waitingQ else []
    waiting_ids = ", ".join(waiting_ids_list) if waiting_ids_list else "Empty"

    # Convert the terminated queue
    terminated_ids_list = [str(proc.pid) for proc in terminatedQ] if terminatedQ else []
    terminated_ids = ", ".join(terminated_ids_list) if terminated_ids_list else "Empty"

    # Add rows to the table
    table.add_row("READY (MLFQ)", ready_ids, style="magenta")
    table.add_row("RUNNING", running_ids, style="green")
    table.add_row("WAITING", waiting_ids, style="yellow")
    table.add_row("IO DEVICES", io_ids, style="red3")
    table.add_row("TERMINATED", terminated_ids, style="orange4")

    # Print the table
    console.print(table, justify="center")

    # Shorter pause to improve responsiveness
    time.sleep(0.5)



def printAg(filename, algorithm_type, num_cpus,num_io, terminatedQ, running_queue, start_clock, end_time):
    """
    Prints the results of the scheduling algorithm execution to a file.

    Args:
        filename (str): The name of the output file.
        algorithm_type (str): The type of scheduling algorithm used.
        num_cpus (int): The number of CPUs in the system.
        num_io (int): the number of IO devices in the system 
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
    
    #wait comp
    wait_times = [job.wait_time for job in terminatedQ]
    # Fairness: Standard deviation of CPU times for all jobs
    job_times = [job.turnaround_time for job in terminatedQ]
    if len(job_times) > 1:
        mean_wait = sum(wait_times) / len(wait_times)
        mean_turnaround = sum(job_times) / len(job_times)
        fairness = (sum((x - mean_turnaround) ** 2 for x in job_times) / len(job_times)) ** 0.5
    else:
        mean_turnaround = 0
        mean_wait = 0
        fairness = 0  # Fairness not applicable with one or no jobs

    # Write results to file
    try:
        with open(filename, "w") as file:
            file.write(f"Scheduling Algorithm: {algorithm_type}\n")
            file.write(f"Number of CPUs: {num_cpus}\n")
            file.write(f"Number of IODs: {num_io}\n")
            file.write(f"Total Simulation Time: {total_time}\n")
            file.write(f"Throughput: {throughput:.2f} jobs/unit time\n")
            file.write(f"CPU Utilization: {cpu_utilization:.2f}%\n")
            file.write(f"Mean Wait Time: {mean_wait:.2f}\n")
            file.write(f"Mean Turnaround Time: {mean_turnaround:.2f}\n")
            file.write(f"Fairness (Turnaround Time Std Dev): {fairness:.2f}\n\n")
            file.write("Terminated Jobs:\n")
            file.write(f"{'PID':<10}{'Arrival':<10}{'Priority':<10}{'Wait Time':<10}{'Burst Time':<15}{'Turnaround Time':<20}\n")
            file.write("=" * 80 + "\n")
            for job in terminatedQ:
                file.write(
                    f"{job.pid:<10}{job.arrival_time:<10}{job.priority:<10}{job.wait_time:<10}{job.cpu_burst_accumulator:<15}{job.turnaround_time:<20}\n"
                )
        print(f"Results successfully written to {filename}.")
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")


def handle_job_completion(process, ready_queues, terminated_queue, waiting_queue):
    """
    Handle job completion and state transitions.
    
    Args:
        process (Process): The process to handle.
        ready_queues (list): List of ready queues.
        terminated_queue (deque): Queue for terminated jobs.
        waiting_queue (deque): Queue for waiting jobs.
    """
    if process.completed:
        process.update_state("TERMINATED")
        terminated_queue.append(process)
        print(f"Job {process.pid} has been terminated.")
    elif process.is_cpu_burst():
        process.update_state("READY")
        process.priority = 0  # Reset to highest priority queue
        ready_queues[0].append(process)
    else:
        process.update_state("WAITING")
        waiting_queue.append(process)

def mlfq_scheduling(
    running_queue, 
    ready_queues, 
    waiting_queue, 
    io_devices, 
    terminated_queue, 
    time_quanta, 
    clock, 
    client_id=None, 
    session_id=None,
    io_queue=None
):
    """
    Multi-Level Feedback Queue Scheduling Algorithm with advanced job management.
    
    Args:
        running_queue (list): List of CPU objects representing the CPUs.
        ready_queues (list): List of ready queues for different priority levels.
        waiting_queue (deque): Queue for jobs waiting for resources.
        io_devices (list): List of I/O device objects.
        terminated_queue (deque): Queue for completed jobs.
        time_quanta (list): Time quantum for each priority level.
        clock (int): Current simulation clock time.
        client_id (str, optional): Client ID for API calls.
        session_id (str, optional): Session ID for API calls.
        io_queue (deque, optional): Queue for I/O waiting jobs.
    """
    
    
   

    # Handle running jobs on CPUs
    for cpu in running_queue:
        if not cpu.current_job:
            cpu.idle_time += 1
            continue

        # Process current job on CPU
        cpu.current_job.remaining_time -= 1
        cpu.active_time += 1

        # Check if job burst is complete
        if cpu.current_job.remaining_time <= 0:
            #print(f"Job {cpu.current_job.pid} completed its burst on CPU {cpu.id}.")
            
            try:
                burst_completed = cpu.current_job.proceed_burst(client_id, session_id, clock)
                if burst_completed:
                    handle_job_completion(
                        cpu.current_job, 
                        ready_queues, 
                        terminated_queue, 
                        waiting_queue
                    )
            except Exception as e:
                print(f"Error processing job {cpu.current_job.pid}: {e}")
            
            cpu.current_job = None  # Free the CPU

        # Check time quantum expiration
        elif (cpu.current_job.remaining_time > 0 and 
              (cpu.current_job.current_burst["duration"] - cpu.current_job.remaining_time) % time_quanta[cpu.current_job.priority] == 0):
            print(f"Time quantum expired for Job {cpu.current_job.pid} on CPU {cpu.id}.")
            
            # Demote job priority
            next_priority = min(len(ready_queues) - 1, cpu.current_job.priority + 1)
            cpu.current_job.priority = next_priority
            cpu.current_job.update_state("READY")
            ready_queues[next_priority].append(cpu.current_job)
            cpu.current_job = None  # Free the CPU

    # Assign jobs from ready queues to idle CPUs
    for priority, queue in enumerate(ready_queues):
        while queue and any(cpu.current_job is None for cpu in running_queue):
            try:
                job = queue.popleft()
                idle_cpu = next((cpu for cpu in running_queue if cpu.current_job is None), None)
                
                if idle_cpu:
                    print(f"Assigning Job {job.pid} from priority {priority} queue to CPU {idle_cpu.id}.")
                    idle_cpu.assign_job(job)
                    job.remaining_time = min(time_quanta[priority], job.current_burst["duration"])
                    job.update_state("RUNNING")
            except Exception as e:
                print(f"Error assigning job from priority {priority} queue: {e}")

    # Process waiting queue
    for process in list(waiting_queue):
        process.current_burst["duration"] -= 1
        
        if process.current_burst["duration"] <= 0:
            waiting_queue.remove(process)
            
            try:
                burst_completed = process.next_burst(client_id, session_id, clock)
                if burst_completed:
                    handle_job_completion(
                        process, 
                        ready_queues, 
                        terminated_queue, 
                        waiting_queue
                    )
            except Exception as e:
                print(f"Error processing waiting job {process.pid}: {e}")

    # Handle I/O devices
    for io_device in io_devices:
        if not io_device.current_job:
            io_device.idle_time += 1
            continue

        # Process current job on I/O device
        io_device.current_job.current_burst["duration"] -= 1
        io_device.active_time += 1

        if io_device.current_job.current_burst["duration"] <= 0:
            print(f"Job {io_device.current_job.pid} completed its I/O burst on IO{io_device.id}.")
            
            process = io_device.current_job
            io_device.current_job = None  # Free the I/O device
            io_device.completed_io_operations += 1

            try:
                burst_completed = process.next_burst(client_id, session_id, clock)
                if burst_completed:
                    handle_job_completion(
                        process, 
                        ready_queues, 
                        terminated_queue, 
                        waiting_queue
                    )
            except Exception as e:
                print(f"Error processing I/O job {process.pid}: {e}")

    # Assign jobs to idle I/O devices
    for process in list(io_queue):
        idle_io_device = next((io for io in io_devices if io.current_job is None), None)
        if idle_io_device:
            try:
                io_queue.remove(process)
                idle_io_device.assign_job(process)
                print(f"Assigning Job {process.pid} to IO{idle_io_device.id}.")
            except Exception as e:
                print(f"Error assigning job to I/O device: {e}")

            




if __name__== '__main__':
    
    ag_path = Path(__file__).resolve().parent.parent.parent / "aggregate"

    # Initialize CPUs
    num_cpus = 4
    running_queue = [CPU(id=i) for i in range(num_cpus)]

    #initialize io devices 
    num_io = 4
    io_queue = [IO(id = i) for i in range(num_io)]

    # Initialize MLFQ-specific data structures
    num_priority_levels = 3
    ready_queues = [deque() for _ in range(num_priority_levels)]
    terminated_queue = deque()
    time_quanta = [4, 8, 16]  # Example time quanta for each priority level
    waitingQ = deque()
   

    # type of scheduling algorithm to run 
    algorithm_type = 'MLFQ'
    #make sure to remove the temporary one if you are chaninge back to this 
    # client_id = "BigSam"

    config = c.getConfig(0)
    base_url = 'http://profgriffin.com:8000/'
    response = c.init(config)
  
    #temporary way of getting client id 
    client_id = config["client_id"]

    start_clock = response['start_clock']
    session_id = response['session_id']
    
    clock = start_clock
      
    

# Main loop
    while True:
        jobs_left = c.getJobsLeft(client_id, session_id)
        if jobs_left == 0 and not any(queue for queue in ready_queues) and not io_queue and not any(cpu.current_job for cpu in running_queue):
            print("No jobs left. Simulation complete.")
            break
        
        # Fetch new jobs from the API and add to the highest-priority queue
        response = c.getJob(client_id, session_id, clock)
        if response and response["success"]:
            for data in response["data"]:
                process = Process(
                    data["arrival_time"],
                    data["job_id"],
                    data["priority"],
                    c.getBurstsLeft(client_id, session_id, data["job_id"])
                )
                process.next_burst(client_id, session_id, clock)
                ready_queues[0].append(process)

        # Run the MLFQ scheduler
        mlfq_scheduling(running_queue, ready_queues, waitingQ,io_queue,terminated_queue,time_quanta,clock,client_id,session_id)
        
        print_queues(clock,ready_queues, running_queue,waitingQ,io_queue,terminated_queue, algorithm_type)
        
        # Increment clock
        clock += 1 