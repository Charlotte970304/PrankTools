import time
import json
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import qrcode
import ctypes

# -------------------------------------------------
# Load external config (fall back to defaults if missing)
# -------------------------------------------------
DEFAULT_DELAY_SECONDS = 5
DEFAULT_PERCENT_SPEED = 80   # animation speed (ms)
DEFAULT_HOLD_AFTER_100 = 3   # seconds to hold black screen after reaching 100%

try:
    with open("bsod_config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}

DELAY_SECONDS   = cfg.get("delay_seconds",   DEFAULT_DELAY_SECONDS)
PERCENT_SPEED   = cfg.get("percent_speed",   DEFAULT_PERCENT_SPEED)
HOLD_AFTER_100  = cfg.get("hold_after_100",  DEFAULT_HOLD_AFTER_100)

# Get screen resolution
user32 = ctypes.windll.user32
W = user32.GetSystemMetrics(0)
H = user32.GetSystemMetrics(1)


def generate_windows_bsod_qr(size):

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=9,
        border=3   # Windows QR border is very thin
    )

    qr.add_data("https://www.windows.com/stopcode")
    qr.make(fit=True)

    # Windows BSOD QR uses: white background + blue dots (not black)
    blue = "#0078D7"   # Windows 10 BSOD blue
    white = "white"

    img = qr.make_image(
        fill_color=blue,    # black → blue
        back_color=white
    ).convert("RGB")

    img = img.resize((size, size), Image.NEAREST)
    return img


def generate_bsod_background(width, height):

    img = Image.new("RGB", (width, height), "#0078d7")
    draw = ImageDraw.Draw(img)

    # Windows default fonts
    face_font  = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", int(height * 0.155))
    text_font  = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",  int(height * 0.032))
    small_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",  int(height * 0.015))

    # Official MS layout ratios
    LEFT = int(width * 0.085)
    TOP  = int(height * 0.21)

    # :(
    draw.text((LEFT, TOP), ":(", fill="white", font=face_font)

    # Line height for main text
    line_h = int(height * 0.032 * 1.55)

    TEXT_Y = TOP + int(height * 0.155)
    text_lines = [
        "Your PC ran into a problem and needs to restart. We're just",
        "collecting some error info, and then we'll restart for you."
    ]
    for i, line in enumerate(text_lines):
        draw.text((LEFT, TEXT_Y + i * line_h), line, fill="white", font=text_font)

    # Percentage position: one blank line after main text
    last_text_y = TEXT_Y + line_h * len(text_lines)
    PERCENT_Y   = last_text_y + line_h * 0.7

    # QR position: another blank line after percentage
    QR_SIZE = int(height * 0.11)
    QR_Y    = int(PERCENT_Y + line_h * 1.20) + int(line_h * 0.5)

    qr_img = generate_windows_bsod_qr(QR_SIZE)
    img.paste(qr_img, (LEFT, int(QR_Y)))

    # QR Description text
    info_x = LEFT + QR_SIZE + int(width * 0.015)
    info_y = QR_Y 

    info_text = (
        "For more information about this issue and possible fixes, visit"
        " https://www.windows.com/stopcode\n\n"
        "If you call a support person, give them this info:\n"
        "Stop code: CRITICAL_PROCESS_DIED"
    )
    draw.multiline_text(
        (info_x, info_y),
        info_text,
        fill="white",
        font=small_font,
        spacing=int(height * 0.013)
    )

    img.save("bsod_bg.png")
    return "bsod_bg.png", PERCENT_Y


def popup_dynamic(bg_path, percent_y):

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="black")
    # Keep ESC available to close (avoid overly restricting exit)
    root.bind("<Escape>", lambda e: root.destroy())

    bg = tk.PhotoImage(file=bg_path)
    canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="black")
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=bg)

    # Percentage font = same style as main text
    percent_font = ("Segoe UI", int(H * 0.024))

    percent_text = canvas.create_text(
        int(W * 0.085),
        percent_y,
        anchor="nw",
        fill="white",
        font=percent_font,
        text="0% complete"
    )

    def show_black_then_surprise():
        """Switch to a full black screen, wait a bit, then show the surprise message."""
        canvas.delete("all")
        canvas.configure(bg="black")
        root.configure(bg="black")

        root.after(int(HOLD_AFTER_100 * 1000), show_surprise)

    def show_surprise():
        """Show the final message telling the user how to exit."""
        canvas.delete("all")
        canvas.configure(bg="black")
        root.configure(bg="black")

        text = (
            "Surprise! This is just a playful fake blue screen 😆\n\n"
            "Press ESC to close the window"
        )
        canvas.create_text(
            W // 2,
            H // 2,
            text=text,
            fill="white",
            font=("Segoe UI", int(H * 0.035)),
            anchor="center",
            justify="center"
        )

    def update_percent(p=0):
        canvas.itemconfig(percent_text, text=f"{p}% complete")
        if p < 100:
            root.after(PERCENT_SPEED, update_percent, p + 1)
        else:
            # Once reaching 100%, immediately transition to black → then show surprise
            show_black_then_surprise()

    update_percent()
    root.mainloop()


print(f"Waiting {DELAY_SECONDS} seconds before showing the fake BSOD...")
time.sleep(DELAY_SECONDS)

bg_path, percent_y = generate_bsod_background(W, H)
popup_dynamic(bg_path, percent_y)
