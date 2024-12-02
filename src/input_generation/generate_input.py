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
         

def get_run_count(file_name="run_count.txt"):
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


def update_run_count(file_name="run_count.txt", count=None):
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

