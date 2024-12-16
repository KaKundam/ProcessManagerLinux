import os
import time
import psutil
from tabulate import tabulate
import datetime

sort_by = None

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'username', 'nice', 'memory_info', 'status', 'cpu_percent', 'memory_percent', 'name']):
        try:
            # Lấy thông tin process
            pid = proc.info['pid']
            user = proc.info['username']
            priority = proc.info['nice']
            memory = proc.info['memory_info'].rss // 1024  # Chuyển sang KiB
            status = proc.info['status']
            cpu_usage = proc.info['cpu_percent']
            memory_usage = proc.info['memory_percent']
            command = proc.info['name']

            # Thêm vào danh sách
            processes.append([pid, user, priority, memory, status, cpu_usage, memory_usage, command])

        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            pass
        except psutil.AccessDenied:
            print(f"Error: Access denied to get the infromation of the process with PID {proc.pid}.")
            pass

    # Sắp xếp danh sách process theo thuộc tính được chọn
    if sort_by:
        idx = {"PID": 0, "USER": 1, "PR": 2, "RES": 3, "%CPU": 5, "%MEM": 6, "COMMAND": 7}.get(sort_by.upper(), 0)
        processes.sort(key=lambda x: x[idx], reverse=(sort_by.upper() in ["%CPU", "%MEM"]))
    return processes

def display_processes(processes):
    headers = ["PID", "USER", "PRIORITY", "RES (KiB)", "STATUS", "%CPU", "%MEM", "COMMAND"]
    table = tabulate(processes, headers=headers, tablefmt="pretty")
    os.system('clear')
    print(table)

def kill_process(pid=None, name=None):
    """Kết thúc một the process dựa trên PID hoặc tên lệnh."""
    try:
        if pid:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Process with PID {pid} has been terminated.")
        elif name:
            CountKill=0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == name:
                    proc.terminate()
                    CountKill+=1
            if CountKill>0:
                print(f"{CountKill} Process {name} has been terminated.")
            else:
                print(f"Can not find process with name {name}.")
    except psutil.AccessDenied:
        print("Error: Access denied to terminate the process.")
    except psutil.NoSuchProcess:
        print("Error: Can not find the process.")
    except Exception as e:
        print(f"Other Error: {e}")

def change_priority(command):
    """Thay đổi độ ưu tiên của một the process."""
    try:
        parts = command.split()
        pid_part = next(part for part in parts if part.startswith("pid="))
        value_part = next(part for part in parts if part.startswith("value="))
        pid = int(pid_part.split("=")[1])
        new_priority = int(value_part.split("=")[1])

        process = psutil.Process(pid)
        process.nice(new_priority)
        print(f"The value of priority of PID {pid} changed to {new_priority}.")
        input("Press Enter to observe the result")

    except psutil.AccessDenied:
        print("Error: Access denied change priority of the process.")
        input("Press Enter to escape")
    except psutil.NoSuchProcess:
        print("Error: Can not find the process.")
        input("Press Enter to escape")
    except StopIteration:
        print("Error: Please enter correct format 'priority pid=<PID> value=<new_priority>'.")
        input("Press Enter to escape")
    except ValueError:
        print("Error: PID or value of priority must be an integer.")
        input("Press Enter to escape")
    except Exception as e:
        print(f"Other Error: {e}")
        input("Press Enter to escape")

def view_process_details(pid):
    """Hiển thị chi tiết của một the process."""
    try:
        process = psutil.Process(pid)
        details = process.as_dict(attrs=['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'create_time', 'cmdline'])
        
        detail_output = "\nProcess details:\n"
        for key, value in details.items():
            detail_output += f"{key.capitalize()}: {value}\n"
        
        print(detail_output)
        input("Press Enter to return.")
    
    except psutil.AccessDenied:
        print("Error: Access deniedto view detail of this process.")
        input("Press Enter to return.")
    except psutil.NoSuchProcess:
        print("Error: Can not find the process.")
        input("Press Enter to return.")
    except Exception as e:
        print(f"Other Error: {e}")
        input("Press Enter to return.")

def filter_by_name(processes, name):
    name = name.lower()
    return [proc for proc in processes if name in proc[7].lower()]

def filter_by_user(processes, username):
    username = username.lower()
    return [proc for proc in processes if proc[1] and username in proc[1].lower()]


def main():
    global sort_by
    while True:
        processes = get_process_info()
        display_processes(processes)

        print("\n--- Process Manager CLI ---")
        print("Availiable Command:")
        print("1. Press Enter to refresh.")
        print("2. Typing 'kill pid=<PID>' to terminate process by PID.")
        print("3. Typing 'kill name=<command>' to terminate process by the command name.")
        print("4. Typing 'sort <parameter>' for sorting, include: PID, USER, PR, RES, %CPU, %MEM, COMMAND.")
        print("5. Typing 'priority pid=<PID> value=<new_priority>' to change the priority of specific process.")
        print("6. Typing 'details pid=<PID>' to show detail of specific process.")
        print("7. Typing 'filter name=<name> to filter process which contains the  parameter name in the command.")
        print("8. Typing 'filter user=<user> to filter process which belong to user.")
        print("9. Typing 'exit' to exit program.")
        command = input("Input Command: ").strip().lower()

        if command == "exit":
            print("Exit program.")
            break
        elif command == "":
            continue
        elif command.startswith("kill"):
            try:
                if "pid=" in command:
                    pid = int(command.split("pid=")[1])
                    kill_process(pid=pid)
                elif "name=" in command:
                    name = command.split("name=")[1]
                    kill_process(name=name)
            except ValueError:
                print("Error: PID must be an integer .")
            time.sleep(3)
        elif command.startswith("sort"):
            sort_by = command.split(" ")[1]
        elif command.startswith("priority"):
            change_priority(command)
        elif command.startswith("details"):
            try:
                pid = int(command.split("pid=")[1])
                view_process_details(pid)
            except (ValueError, IndexError):
                print("Error: PID must be an integer.")
        elif command.startswith("filter"):
            if "name=" in command:
                name = command.split("name=")[1]
                filtered_processes = filter_by_name(processes, name)
                if filtered_processes:
                    display_processes(filtered_processes)
                else:
                    print(f"No process found with name '{name}'.")
            elif "user=" in command:
                user = command.split("user=")[1]
                filtered_processes = filter_by_user(processes, user)
                if filtered_processes:
                    display_processes(filtered_processes)
                else:
                    print(f"No process found for user '{user}'.")
            else:
                print("Error: Invalid filter format. Use 'filter name=<name>' or 'filter user=<user>'.")
            input("Press Enter to return.")
        else:
            print("Invalid Command. Please try again.")

if __name__ == "__main__":
    main()
