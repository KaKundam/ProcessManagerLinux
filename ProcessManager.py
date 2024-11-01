import os
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
            print(f"Lỗi: Không đủ quyền truy cập để lấy thông tin tiến trình PID {proc.pid}.")
            pass

    # Sắp xếp danh sách process theo thuộc tính được chọn
    if sort_by:
        idx = {"PID": 0, "USER": 1, "PRIORITY": 2, "RES": 3, "%CPU": 5, "%MEM": 6, "COMMAND": 7}.get(sort_by.upper(), 0)
        processes.sort(key=lambda x: x[idx], reverse=(sort_by.upper() in ["%CPU", "%MEM"]))
    return processes

def display_processes(processes):
    headers = ["PID", "USER", "PRIORITY", "RES (KiB)", "STATUS", "%CPU", "%MEM", "COMMAND"]
    table = tabulate(processes, headers=headers, tablefmt="pretty")
    os.system('clear')
    print(table)

def kill_process(pid=None, name=None):
    """Kết thúc một tiến trình dựa trên PID hoặc tên lệnh."""
    try:
        if pid:
            process = psutil.Process(pid)
            process.terminate()
            log_action(f"Killed process with PID {pid}.")
            print(f"Process với PID {pid} đã bị kết thúc.")
        elif name:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == name:
                    proc.terminate()
                    log_action(f"Killed process with name {name}.")
                    print(f"Process {name} đã bị kết thúc.")
                    return
            print(f"Không tìm thấy process có tên {name}.")
    except psutil.AccessDenied:
        print("Lỗi: Không đủ quyền truy cập để kết thúc tiến trình này.")
    except psutil.NoSuchProcess:
        print("Lỗi: Không tìm thấy tiến trình.")
    except Exception as e:
        print(f"Lỗi khác: {e}")

def change_priority(command):
    """Thay đổi độ ưu tiên của một tiến trình."""
    try:
        parts = command.split()
        pid_part = next(part for part in parts if part.startswith("pid="))
        value_part = next(part for part in parts if part.startswith("value="))
        pid = int(pid_part.split("=")[1])
        new_priority = int(value_part.split("=")[1])

        process = psutil.Process(pid)
        process.nice(new_priority)
        log_action(f"Changed priority of PID {pid} to {new_priority}.")
        print(f"Độ ưu tiên của PID {pid} đã được thay đổi thành {new_priority}.")
        input("Press Enter to observe the result")

    except psutil.AccessDenied:
        print("Lỗi: Không đủ quyền truy cập để thay đổi độ ưu tiên của tiến trình này.")
        input("Press Enter to escape")
    except psutil.NoSuchProcess:
        print("Lỗi: Không tìm thấy tiến trình.")
        input("Press Enter to escape")
    except StopIteration:
        print("Lỗi: Vui lòng nhập đúng định dạng 'priority pid=<PID> value=<new_priority>'.")
        input("Press Enter to escape")
    except ValueError:
        print("Lỗi: PID và giá trị ưu tiên phải là số nguyên.")
        input("Press Enter to escape")
    except Exception as e:
        print(f"Lỗi khác: {e}")
        input("Press Enter to escape")

def view_process_details(pid):
    """Hiển thị chi tiết của một tiến trình."""
    try:
        process = psutil.Process(pid)
        details = process.as_dict(attrs=['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'create_time', 'cmdline'])
        
        detail_output = "\nChi tiết tiến trình:\n"
        for key, value in details.items():
            detail_output += f"{key.capitalize()}: {value}\n"
        
        print(detail_output)
        input("Nhấn Enter để quay lại.")
    
    except psutil.AccessDenied:
        print("Lỗi: Không đủ quyền truy cập để xem chi tiết của tiến trình này.")
        input("Nhấn Enter để quay lại.")
    except psutil.NoSuchProcess:
        print("Lỗi: Không tìm thấy tiến trình.")
        input("Nhấn Enter để quay lại.")
    except Exception as e:
        print(f"Lỗi khác: {e}")
        input("Nhấn Enter để quay lại.")

def log_action(action):
    with open("process_manager_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {action}\n")

def main():
    global sort_by
    while True:
        processes = get_process_info()
        display_processes(processes)

        print("\n--- Process Manager CLI ---")
        print("Các lệnh có sẵn:")
        print("1. Nhấn Enter để làm mới danh sách.")
        print("2. Nhập 'kill pid=<PID>' để kết thúc một process bằng PID.")
        print("3. Nhập 'kill name=<command>' để kết thúc một process bằng tên lệnh.")
        print("4. Nhập 'sort <thuộc tính>' để sắp xếp, bao gồm: PID, USER, PRIORITY, RES, %CPU, %MEM, COMMAND.")
        print("5. Nhập 'priority pid=<PID> value=<new_priority>' để thay đổi độ ưu tiên.")
        print("6. Nhập 'details pid=<PID>' để xem chi tiết của một process.")
        print("7. Nhập 'exit' để thoát chương trình.")
        command = input("Nhập lệnh: ").strip().lower()

        if command == "exit":
            print("Thoát chương trình.")
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
                print("Lỗi: PID phải là một số nguyên.")
        elif command.startswith("sort"):
            sort_by = command.split(" ")[1]
        elif command.startswith("priority"):
            change_priority(command)
        elif command.startswith("details"):
            try:
                pid = int(command.split("pid=")[1])
                view_process_details(pid)
            except (ValueError, IndexError):
                print("Lỗi: PID phải là một số nguyên.")
        else:
            print("Lệnh không hợp lệ. Vui lòng thử lại.")

if __name__ == "__main__":
    main()
