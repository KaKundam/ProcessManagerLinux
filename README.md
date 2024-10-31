# ProcessManagerLinux


--- Process Manager CLI ---

Cài về và chạy file ProcessManager.py bằng python
Lưu ý trong máy cần có thư viện psutil và tabulate

Chưa có thì có thể cài bằng các câu lệnh sau

pip install psutil
pip install tabulate

Các câu lệnh sẵn có trong ứng dụng



1. Nhấn Enter để làm mới danh sách.
2. Nhập 'kill pid=<PID>' để kết thúc một process bằng PID.
3. Nhập 'kill name=<command>' để kết thúc một process bằng tên lệnh.
4. Nhập 'sort <thuộc tính>' để sắp xếp, bao gồm: PID, USER, PR, RES, %CPU, %MEM, COMMAND. VD: sort %cpu, sort command, ...
5. Nhập 'exit' để thoát chương trình.



Created by KaKundam and LHH
