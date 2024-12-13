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

def fcfs(running_queue, readyQ):
    """
    Implements the First-Come, First-Served (FCFS) scheduling algorithm.

    Assigns jobs from the ready queue to idle CPUs in the running queue.

    Args:
        running_queue (list): A list of CPU objects representing the running CPUs.
        readyQ (deque): A deque containing the processes ready for execution (CPU bursts only).
    """
    print("Running FCFS!!!")

    for cpu in running_queue:
        # If the CPU is idle (current_job is None)
        if not cpu.current_job:
            print(f"CPU {cpu.id} is idle. Checking ready queue...")
            if readyQ:
                # Assign the job at the front of the ready queue to the CPU
                job = readyQ.popleft()
                print(f"Assigning Job {job.pid} (Priority: {job.priority}) to CPU {cpu.id}.")
                cpu.assign_job(job)
                cpu.current_job.update_state("RUNNING")
            else:
                print(f"No jobs in the ready queue to assign to CPU {cpu.id}.")
        else:
            print(f"CPU {cpu.id} is busy with Job {cpu.current_job.pid}.") # Update state for the assigned job

def sjf(running_queue, readyQ):
    """
    Implements the Shortest Job First (SJF) scheduling algorithm.

    Assigns jobs from the ready queue to idle CPUs in the running queue based on the shortest CPU burst.

    Args:
        running_queue (list): A list of CPU objects representing the running CPUs.
        readyQ (deque): A deque containing the processes ready for execution (CPU bursts only).
    """
    for cpu in running_queue:
        # If the CPU is idle (current_job is None)
        if not cpu.current_job:
            print(f"CPU {cpu.id} is idle. Checking ready queue for the shortest job...")
            if readyQ:
                # Find the job with the shortest CPU burst duration
                shortest_job = min(readyQ, key=lambda job: job.current_burst["duration"])
                print(f"Selected Job {shortest_job.pid} with burst duration {shortest_job.current_burst['duration']} as the shortest job.")
                
                readyQ.remove(shortest_job)  # Remove the selected job from the ready queue
                cpu.assign_job(shortest_job)
                cpu.current_job.update_state("RUNNING")
                print(f"Assigned Job {shortest_job.pid} to CPU {cpu.id}.")
            else:
                print(f"No jobs in the ready queue to assign to CPU {cpu.id}.")
        else:
            print(f"CPU {cpu.id} is busy with Job {cpu.current_job.pid}.")


def priority_scheduling(running_queue, readyQ):
    """
    Implements the Non-Preemptive Priority Scheduling algorithm.

    Assigns the highest-priority job (smallest priority value) from the ready queue to idle CPUs.

    Args:
        running_queue (list): A list of CPU objects representing the running CPUs.
        readyQ (deque): A deque containing the processes ready for execution (CPU bursts only).
    """
    print("Running Priority Scheduling!!!")
    
    for cpu in running_queue: 
        # If the CPU is idle (current_job is None)
        if not cpu.current_job:
            print(f"CPU {cpu.id} is idle. Checking ready queue for the highest priority job...")
            if readyQ:
                # Find the job with the highest priority (lowest priority number)
                highest_priority_job = min(readyQ, key=lambda process: process.priority)
                print(f"Selected Job {highest_priority_job.pid} with priority {highest_priority_job.priority} as the highest priority job.")

                # Remove the highest-priority job from the ready queue
                readyQ.remove(highest_priority_job)
                print(f"Removed Job {highest_priority_job.pid} from the ready queue.")

                # Update the state of the job to "RUNNING"
                highest_priority_job.update_state("RUNNING")
                print(f"Updated Job {highest_priority_job.pid} state to RUNNING.")

                # Assign the job to the idle CPU
                cpu.assign_job(highest_priority_job)
                print(f"Assigned Job {highest_priority_job.pid} to CPU {cpu.id}.")
            else:
                print(f"No jobs in the ready queue to assign to CPU {cpu.id}.")
        else:
            print(f"CPU {cpu.id} is busy with Job {cpu.current_job.pid}.")

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


if __name__== '__main__':
  
    ag_path = Path(__file__).resolve().parent.parent.parent / "aggregate"

    # Initialize CPUs
    num_cpus = 4
    running_queue = [CPU(id=i) for i in range(num_cpus)]

    readyQ = deque()
    waitingQ = deque()
    terminatedQ = deque()

    # type of scheduling algorithm to run 
    algorithm_type = 'FCFS'
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
      
    while True:
        # Check remaining jobs
        jobs_left = c.getJobsLeft(client_id, session_id)

        #print(type(jobs_left))
        
        if  not jobs_left:
            # Generate a unique filename using a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = ag_path / f"results_{timestamp}.txt"
            printAg(filename,algorithm_type,num_cpus,terminatedQ,running_queue,start_clock,clock)
            break

        
        # get job 
        response = c.getJob(client_id,session_id, clock)

        

        if response and response["success"]:
            if response["data"]:
                for data in response["data"]:
                    process =  Process(
                        data["arrival_time"], 
                        data["job_id"],
                        data["priority"],
                        c.getBurstsLeft(client_id,session_id, data["job_id"]) # would only happen once for every job
                        )
                    # this time, it would fill it with the first burst 
                    process.next_burst(client_id, session_id,clock)

                    if process.is_cpu_burst():
                        # Set state of process to READY
                        process.state = "READY"

                        # Add process to ready queue
                        readyQ.append(process)
                    else:
                        # Handle I/O burst processes
                        process.state = "WAITING"
                        
                        # Add process to waiting queue
                        waitingQ.append(process)

        
        # choose which algorithm to run 
        if algorithm_type == "FCFS":
            fcfs(running_queue,readyQ)
        elif algorithm_type == "SJF":
            sjf(running_queue,readyQ)
        elif algorithm_type == "p":
            priority_scheduling(running_queue,readyQ)
            


        # Process jobs on each CPU
        for cpu in running_queue:
            # If the CPU has a job assigned
            if cpu.current_job:
                #true if current burst is completed, automatically calls next burst function 
                completed_burst = cpu.current_job.proceed_burst(client_id, session_id, clock)

                # Update CPU active time
                cpu.active_time += 1

                # If the current burst is completed
                if completed_burst:
                    # Check if the job itself is completed (all bursts done)
                    if cpu.current_job.completed:
                        cpu.current_job.state = "TERMINATED"
                        # Move the job to the terminated queue
                        terminatedQ.append(cpu.current_job)
                        print(f"Job {cpu.current_job.pid} has completed and is moved to the terminated queue.")

                        # Increment completed jobs counter
                        cpu.completed_jobs += 1

                        # Free up the CPU
                        cpu.current_job = None
                    else:
                        # if Job has more bursts, the next bursts
                        # has already been loaded by proceed burst 
                        

                        # If the next burst is an I/O burst, move the job to the waiting queue
                        if not cpu.current_job.is_cpu_burst():
                            cpu.current_job.state = "WAITING"
                            waitingQ.append(cpu.current_job)
                            print(f"Job {cpu.current_job.pid} moved to the waiting queue for an I/O burst.")

                            # Free up the CPU
                            cpu.current_job = None
            else:
                # If the CPU is idle, increment idle time
                cpu.idle_time += 1
                print(f"CPU {cpu.id} is currently idle.")
           
        # Process the waiting queue
        for process in list(waitingQ):  # Use list to avoid modifying the deque while iterating
            # Decrement the I/O burst duration
            io_burst_complete = process.proceed_burst(client_id, session_id, clock)

            # If the I/O burst is completed
            if io_burst_complete:
                waitingQ.remove(process)  # Remove from the waiting queue

                """next burst already gotten from call to proceed_burst"""

                if process.completed:
                    process.state = "TERMINATED"

                    terminatedQ.append(process)
                    print(f"Job {process.pid} has completed and is moved to the terminated queue.")
                else:
                    # If the next burst is a CPU burst, move the process to the ready queue
                    if process.is_cpu_burst():
                        process.state = "READY"
                        readyQ.append(process)
                        print(f"Job {process.pid} has completed I/O and is moved to ready queue.")
                    else:
                        # If the next burst is another I/O burst, re-add to the waiting queue
                        process.state = "WAITING"
                        waitingQ.append(process)
                        print(f"Job {process.pid} continues with another I/O burst.")
        
        # Advance the clock
        clock += 1


