import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading
import queue
from PIL import Image

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        start_renaming(folder)

def start_renaming(folder):
    progress = ttk.Progressbar(root, mode='indeterminate', length=300)
    progress.pack(pady=20)
    progress.start()

    status_label.config(text="Đang xử lý...")

    q = queue.Queue()
    thread = threading.Thread(target=rename_worker, args=(folder, q))
    thread.start()
    check_queue(q, progress)

def rename_worker(folder, q):
    # Các định dạng ảnh hỗ trợ
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    images = [f for f in os.listdir(folder) if f.lower().endswith(image_extensions)]
    images.sort()  # Sắp xếp theo tên file để thứ tự ổn định

    for i, img_name in enumerate(images, 1):
        old_path = os.path.join(folder, img_name)
        new_name = f"Anh ({i}).jpg"
        new_path = os.path.join(folder, new_name)

        # Kiểm tra nếu tên mới đã tồn tại, tránh ghi đè
        if os.path.exists(new_path):
            q.put('error')
            return

        try:
            with Image.open(old_path) as img:
                # Chuyển sang RGB và lưu dưới dạng JPEG
                img.convert('RGB').save(new_path, 'JPEG', quality=95)
            os.remove(old_path)  # Xóa file cũ
        except Exception as e:
            q.put('error')
            return

    q.put('done')

def check_queue(q, progress):
    try:
        msg = q.get_nowait()
        if msg == 'done':
            progress.stop()
            progress.pack_forget()
            status_label.config(text="Hoàn thành!")
            messagebox.showinfo("Thông báo", "Đã đổi tên tất cả ảnh thành công!")
        elif msg == 'error':
            progress.stop()
            progress.pack_forget()
            status_label.config(text="Lỗi!")
            messagebox.showerror("Lỗi", "Có lỗi xảy ra trong quá trình đổi tên. Có thể tên file mới đã tồn tại hoặc file không phải ảnh.")
        else:
            root.after(200, check_queue, q, progress)
    except queue.Empty:
        root.after(200, check_queue, q, progress)

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Công cụ đổi tên ảnh hàng loạt")
root.geometry("400x200")

# Nút chọn thư mục
select_button = tk.Button(root, text="Chọn thư mục ảnh", command=select_folder)
select_button.pack(pady=20)

# Label trạng thái
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
