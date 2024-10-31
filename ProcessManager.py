import os
import time
import psutil
from tabulate import tabulate

sort_by=None

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

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sắp xếp danh sách process theo thuộc tính được chọn
    if sort_by:
        idx = {"PID": 0, "USER": 1, "PR": 2, "RES": 3, "%CPU": 5, "%MEM": 6, "COMMAND": 7}.get(sort_by.upper(), 0)
        processes.sort(key=lambda x: x[idx], reverse=(sort_by.upper() in ["%CPU", "%MEM"]))
    return processes

def display_processes(processes):
    headers = ["PID", "USER", "PRIORITY", "RES (KiB)", "S", "%CPU", "%MEM", "COMMAND"]
    table = tabulate(processes, headers=headers, tablefmt="pretty")
    os.system('clear')
    print(table)

def kill_process(pid=None, name=None):
    try:
        if pid:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Process với PID {pid} đã bị kết thúc.")
        elif name:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == name:
                    proc.terminate()
                    print(f"Process {name} đã bị kết thúc.")
                    return
            print(f"Không tìm thấy process có tên {name}.")
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"Lỗi: {e}")

def main():
    while True:
        

        processes = get_process_info()
        display_processes(processes)

        # Nhận lệnh từ người dùng
        print("\n--- Process Manager CLI ---")
        print("Các lệnh có sẵn:")
        print("1. Nhấn Enter để làm mới danh sách.")
        print("2. Nhập 'kill pid=<PID>' để kết thúc một process bằng PID.")
        print("3. Nhập 'kill name=<command>' để kết thúc một process bằng tên lệnh.")
        print("4. Nhập 'sort <thuộc tính>' để sắp xếp, bao gồm: PID, USER, PR, RES, %CPU, %MEM, COMMAND. VD: sort %cpu, sort command, ...")
        print("5. Nhập 'exit' để thoát chương trình.")
        print("\nDanh sách process hiện tại:")
        command = input("Nhập lệnh: ").strip().lower()

        if command == "exit":
            print("Thoát chương trình.")
            break
        elif command.startswith("kill"):
            try:
                if "pid=" in command:
                    pid = int(command.split("=")[1])
                    kill_process(pid=pid)
                elif "name=" in command:
                    name = command.split("=")[1]
                    kill_process(name=name)
            except ValueError:
                print("Lỗi: PID phải là một số nguyên .")
            time.sleep(2)
        elif command.startswith("sort"):
            global sort_by
            sort_by = command.split(" ")[1]
            processes = get_process_info()
            display_processes(processes)
        else:
            print("Lệnh không hợp lệ. Vui lòng thử lại.")

if __name__ == "__main__":
    main()

