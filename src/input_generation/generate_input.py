from pathlib import Path
import random 


#configuration data 
config = {
        "min_jobs": 5,
        "max_jobs": 20,

        #min and max burst have to 
        #be odd numbered so we end with a cpu burst 
        "min_bursts": 11, 
        "max_bursts": 51,

        "min_job_interval": 1,
        "max_job_interval": 5,
        "burst_type_ratio": 0.5,
        "min_cpu_burst_interval": 15,
        "max_cpu_burst_interval": 50,
        "min_io_burst_interval": 30,
        "max_io_burst_interval": 70,
        "min_ts_interval": 5,
        "max_ts_interval": 5,
        "prioritys": [1,2,3,4,5]
}

def biased_randint(low, high, biased_range, mid_range=None , m_weight=2, b_weight=5):
    if (mid_range):
        """
    Generate a random integer between `low` and `high` (inclusive) with customizable bias.

    The function increases the likelihood of selecting integers from specified ranges 
    (`biased_range` and optionally `mid_range`) by assigning higher weights to them.

    Parameters:
        low (int): The lower bound of the range (inclusive).
        high (int): The upper bound of the range (inclusive).
        biased_range (iterable): A range of numbers to assign a higher selection weight (`b_weight`).
        mid_range (iterable, optional): An additional range of numbers to assign a moderate selection weight (`m_weight`).
                                         Defaults to None, meaning no mid-range weighting is applied.
        m_weight (int, optional): The weight assigned to numbers in the `mid_range`. Defaults to 2.
        b_weight (int, optional): The weight assigned to numbers in the `biased_range`. Defaults to 5.

    Returns:
        int: A randomly selected integer between `low` and `high`, with bias applied based on the weights.

    Example:
        >>> biased_randint(1, 10, biased_range=[3, 4, 5], mid_range=[7, 8], m_weight=3, b_weight=6)
        5  # More likely but not guaranteed to be in the biased_range or mid_range
    """
        # generate full list 
        numbers = range(low,high+1)
        
        # give each num in biased_range,
        # higher weight, increase chances of selection
        weights = [
            b_weight if num in biased_range else  m_weight if num in mid_range else 1
            for num in numbers
            ]
        
        return random.choices(numbers, weights, k=1)[0]
    else:
        # generate full list 
        numbers = range(low,high+1)
        
        # give each num in biased_range,
        # higher weight, increase chances of selection
        weights = [
            b_weight if num in biased_range else 1
            for num in numbers
            ]
        
        return random.choices(numbers, weights, k=1)[0]

# if no_burst is not passed, we set it to the min number of bursts 
def burst_generator(process_type, no_bursts=config["min_bursts"]): 
    """
    Generates a sequence of CPU and I/O bursts for a process based on its type.

    This function creates a list of bursts, alternating between CPU and I/O operations. 
    The number of bursts is validated and adjusted to ensure an even count, so the sequence 
    always ends with a CPU burst. The burst values are generated either randomly or with 
    specific biases depending on the `process_type`.

    Parameters:
        process_type (str): 
            The type of process. Can be one of:
                - 'P': Priority-based. Bursts are generated with no bias.
                - 'C': CPU-intensive. CPU bursts are biased towards higher values, and 
                       I/O bursts are biased towards lower values.
                - 'I': I/O-intensive. CPU bursts are biased towards lower values, and 
                       I/O bursts are biased towards higher values.
        no_bursts (int, optional): 
            The number of bursts to generate. Defaults to `config["min_bursts"]`. 
            If not within the range [`config["min_bursts"]`, `config["max_bursts"]`], 
            it is set to `config["max_bursts"]`.

    Returns:
        list: A list of burst values, alternating between CPU and I/O bursts.

    Notes:
        - The `biased_randint` function is used to introduce biases in burst generation 
          for CPU- and I/O-intensive processes.

    Example:
        >>> burst_generator('P', 5)
        [20, 15, 30, 12, 25]  # Alternates CPU and I/O bursts with no bias.

        >>> burst_generator('C', 6)
        [90, 5, 85, 7, 92, 6]  # CPU bursts are higher; I/O bursts are lower.

        >>> burst_generator('I', 4)
        [3, 95, 2, 90]  # CPU bursts are lower; I/O bursts are higher.
    """
    bursts = []

    # validate the no_bursts variable
    valid_no_bursts = no_bursts if no_bursts in range(config["min_bursts"], config["max_bursts"]+1) else config["max_bursts"]

    # ensures valid_no_burst is even so we end wih a cpu burst 
    valid_no_bursts = (valid_no_bursts + 1) if valid_no_bursts % 2 == 0 else valid_no_bursts  

    if process_type =='P': #priority based 
        for i in range(valid_no_bursts):

            if i % 2 == 0:#cpu burst 
                burst_value = random.randint(config["min_cpu_burst_interval"], config["max_cpu_burst_interval"])
                bursts.append(burst_value)

            else: #io burst 
                burst_value = random.randint(config["min_io_burst_interval"], config["max_io_burst_interval"])
                bursts.append(burst_value)

    elif process_type == 'C': # cpu based 
        for i in range(valid_no_bursts):

            if i % 2 == 0:#cpu burst 
                l = config["min_cpu_burst_interval"]
                h = config["max_cpu_burst_interval"]
                
                #denotes the begining of high intrvals 
                high_interval_start =  h - (h// 3)

                # generate a  random value  for cpu burst
                #  but biased towards higher numbers 
                burst_value = biased_randint(l,h,range(high_interval_start,h+1), b_weight= 7)
                bursts.append(burst_value)

            else: #io burst 
                l = config["min_io_burst_interval"]
                h = config["max_io_burst_interval"]

                #denotes the end of low interval
                low_interval_end = l + ((h - l) // 3)
  
                # generate a  random value  for io burst
                #  but biased towards lower numbers 
                burst_value = biased_randint(l,h,range(l, low_interval_end+1), b_weight= 7)
                bursts.append(burst_value)
    else: #io based 
        for i in range(valid_no_bursts):

            if i % 2 == 0:#cpu burst 
                l = config["min_cpu_burst_interval"]
                h = config["max_cpu_burst_interval"]
                
                #denotes the end of low interval
                low_interval_end = l + ((h - l) // 3)
                

                # generate a  random value  for cpu burst
                #  but biased towards lower numbers 
                burst_value = biased_randint(l,h,range(l,low_interval_end+1), b_weight= 7)
                bursts.append(burst_value)

            else: #io burst 
                l = config["min_io_burst_interval"]
                h = config["max_io_burst_interval"]

                #denotes the begining of high intrvals 
                high_interval_start =  h - (h// 3)
  
                # generate a  random value  for io burst
                #  but biased towards higher numbers 
                burst_value = biased_randint(l,h,range(high_interval_start, h+1), b_weight= 7)
                bursts.append(burst_value)
  
    return bursts




def generate_file(filename, num_processes, process_type):
    """
    Generate a file containing simulated process data, sorted by arrival time.

    This function creates a specified number of processes with arrival times, process IDs, 
    priorities, and CPU/I/O bursts. The generated processes are written to a file in a format 
    where each line represents one process. Processes are sorted by their arrival time.

    Parameters:
        filename (str): 
            The name of the file to write the process data to.
        num_processes (int): 
            The number of processes to generate.
        process_type (str): 
            The type of process. Can be one of:
                - 'P': Priority-based. Assigns higher weights to high-priority values 
                       when generating priorities.
                - 'C' or 'I': CPU- or I/O-intensive. Generates priorities randomly 
                              without bias.

    Notes:
        - Each process is represented as a list: [arrival_time, pid, priority, bursts...].
        - `config` is assumed to be a global dictionary containing:
            - "prioritys": A list defining the range of priority values.
            - "min_bursts" and "max_bursts": The minimum and maximum number of bursts per process.
        - The `biased_randint` function is used for biased random priority generation.
        - The `burst_generator` function is used to create the CPU and I/O burst sequences.

    Output:
        - The file contains one line per process, with space-separated values:
          <arrival_time> <pid> <priority> <burst_1> <burst_2> ...

    Example:
        >>> generate_file("processes.txt", 5, 'P')
        # The file "processes.txt" is created with 5 priority-based processes.
    """
    #open file 
    with open(filename, 'w') as file:
        processes = [] # holds all proceses generated 

        if (process_type == 'P'):
        # create "num_processes"  number of processes 
            for i in range(num_processes):
                # assign a random arrival time 
                arrival_time = random.randint(0,20)
                # assign process id incrementally as process are created 
                pid = i + 1
                
                l = config["prioritys"][0]  # smallest number is highest priority 
                h = config["prioritys"][len(config["prioritys"]) - 1] # largest number is lowest priority 
                
                last_high_priorty  =  l + ((h - l) // 3) # last value in priority we count as high 

                #bias to higher priority with 'l' beign the highest
                priority = biased_randint(l,h, range(l, last_high_priorty +1))
                
                #generate cpu/io burst 
                bursts = burst_generator(process_type, random.randint(config["min_bursts"], config["max_bursts"]))

                process = [arrival_time, pid, priority] + bursts

                processes.append(process)

        else :
          # create "num_processes"  number of processes 
            for i in range(num_processes):
                 # assign a random arrival time 
                arrival_time = random.randint(0,20)
                # assign process id incrementally as process are created 
                pid = i + 1
                
                l = config["prioritys"][0]  # smallest number is highest priority 
                h = config["prioritys"][len(config["prioritys"]) - 1] # largest number is lowest priority 

                # assign random prioirty 
                priority = random.randint(l,h)
                
                #generate cpu/io burst 
                bursts = burst_generator(process_type,  random.randint(config["min_bursts"], config["max_bursts"]))

                process = [arrival_time, pid, priority] + bursts

                processes.append(process)
        
        # sort all processes by arrrival time 
        processes.sort(key=lambda x:x[0])
        
        # print all processes, line by line 
        for process in processes: 
            file.write(' '.join(map(str,process ))+ '\n')
         

def get_run_count(file_name=Path(__file__).resolve().parent / "run_count.txt"):
    """
    Retrieves the program's run count from a file. Returns 0 if the file doesn't exist.
    
    Args:
        file_name (str): The file to read the run count from. Default is "run_count.txt".
    
    Returns:
        int: The run count.
    """
    try:
        with open(file_name, "r") as file:
            count = int(file.read().strip())
    except FileNotFoundError:
        count = 0
    return count


def update_run_count(file_name=Path(__file__).resolve().parent / "run_count.txt", count=None):
    """
    Updates the run count in a file. If no count is provided, increments the current count.
    
    Args:
        file_name (str): The file to update the run count in. Default is "run_count.txt".
        count (int, optional): The new count. Defaults to None, which increments the count.
    
    Returns:
        None
    """
    if count is None:
        count = get_run_count(file_name) + 1
    with open(file_name, "w") as file:
        file.write(str(count))

         
   
   

if __name__ == "__main__":
     
   process_types = ['P','C','I']
   num_processes = 20
   current_run_count = get_run_count()
   
   # Define the relative path from src to the test directory
   test_path = Path(__file__).resolve().parent.parent.parent / 'test'
   for process_type in process_types:
       
       # format for every file name is processType_num_processesId
       # so "P_20_0.txt"  means  priority based file with 20 processes and (id = 0 = first of its kind)
       filename = test_path / f"{process_type}_{num_processes}_{current_run_count}.txt"

       generate_file(filename,num_processes,process_type)

   update_run_count()

