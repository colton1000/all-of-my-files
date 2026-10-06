import tkinter as tk
import psutil
import GPUtil

# -----------------------------
# Color helper
# -----------------------------
def usage_color(percent):
    if percent < 50:
        return "#4CAF50"   # green
    elif percent < 80:
        return "#FFC107"   # yellow
    else:
        return "#F44336"   # red

# -----------------------------
# GPU helper
# -----------------------------
def get_gpu_usage():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None
        return gpus[0].load * 100
    except:
        return None

# -----------------------------
# Bar drawing helper
# -----------------------------
def draw_bar(canvas, x, y, width, height, percent):
    canvas.create_rectangle(x, y, x + width, y + height, fill="#333333", outline="")
    fill_width = int(width * (percent / 100))
    canvas.create_rectangle(x, y, x + fill_width, y + height, fill=usage_color(percent), outline="")

# -----------------------------
# Update loop
# -----------------------------
def update():
    canvas.delete("all")

    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    gpu = get_gpu_usage()

    stats = [
        ("CPU", cpu),
        ("RAM", mem),
        ("Disk", disk),
        ("GPU", gpu if gpu is not None else None)
    ]

    y = 10
    for label, value in stats:
        canvas.create_text(10, y, anchor="w", fill="white", font=("Consolas", 12),
                           text=f"{label}: {value:.1f}%" if value is not None else f"{label}: N/A")
        if value is not None:
            draw_bar(canvas, 100, y - 8, 90, 12, value)
        y += 30

    root.after(500, update)

# -----------------------------
# Window setup
# -----------------------------
root = tk.Tk()
root.title("System Overlay")
root.geometry("200x140+10+10")
root.resizable(False, False)
root.attributes("-topmost", True)
root.overrideredirect(True)  # borderless

canvas = tk.Canvas(root, width=200, height=140, bg="#1E1E1E", highlightthickness=0)
canvas.pack()

update()
root.mainloop()