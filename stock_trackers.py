import tkinter as tk
from tkinter import ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import matplotlib.dates as mdates
import sys

def format_price(price):
    if price is None:
        return "N/A"
    return f"{price:,.2f}".replace(",", "x").replace(".", ",").replace("x", ".")

def format_date(date):
    return date.strftime("%d-%m-%Y")

class IndonesianStockTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Indonesian Stock Tracker")
        self.master.geometry("800x600")
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.stock_var = tk.StringVar()
        self.is_dark_mode = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.apply_theme()

    def create_widgets(self):
        self.frame = ttk.Frame(self.master, padding="10", style='Custom.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.frame, text="Enter stock symbol (e.g., BBCA.JK):", style='Custom.TLabel').pack(pady=10)
        ttk.Entry(self.frame, textvariable=self.stock_var, style='Custom.TEntry').pack()
        self.fetch_button = ttk.Button(self.frame, text="Fetch Data", command=self.fetch_stock_data)
        self.fetch_button.pack(pady=10)

        self.info_frame = ttk.Frame(self.frame, style='Custom.TFrame')
        self.info_frame.pack(pady=10, fill=tk.X)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.dark_mode_toggle = ttk.Checkbutton(self.frame, text="Dark Mode", variable=self.is_dark_mode, command=self.toggle_theme, style='Custom.TCheckbutton')
        self.dark_mode_toggle.pack(pady=10)

    def fetch_stock_data(self):
        symbol = self.stock_var.get()
        stock = yf.Ticker(symbol)
        
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        info = stock.info
        self.create_info_label(f"Company: {info.get('longName', 'N/A')}")
        self.create_info_label(f"Current Price: {format_price(info.get('currentPrice'))} {info.get('currency', 'IDR')}")
        self.create_info_label(f"Day's Range: {format_price(info.get('dayLow'))} - {format_price(info.get('dayHigh'))}")

        hist = stock.history(period="1mo")
        self.ax.clear()
        line, = self.ax.plot(hist.index, hist['Close'])
        self.ax.set_title(f"{symbol} - Last Month")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Closing Price (IDR)")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_price(x)))
        self.fig.autofmt_xdate()

        cursor = mplcursors.cursor(line, hover=True)
        cursor.connect(
            "add", lambda sel: sel.annotation.set_text(
                f'Date: {format_date(mdates.num2date(sel.target[0]))}\nPrice: {format_price(sel.target[1])} IDR'
            )
        )

        self.apply_theme()
        self.canvas.draw()

    def create_info_label(self, text):
        label = ttk.Label(self.info_frame, text=text, style='Custom.TLabel')
        label.pack(anchor="w")

    def toggle_theme(self):
        self.apply_theme()

    def apply_theme(self):
        style = ttk.Style()
        if self.is_dark_mode.get():
            bg_color = '#2E2E2E'
            fg_color = 'white'
            button_bg = '#4A4A4A'
            button_fg = 'white'
        else:
            bg_color = 'white'
            fg_color = 'black'
            button_bg = '#E0E0E0'
            button_fg = 'black'

        self.master.configure(bg=bg_color)
        self.frame.configure(style='Custom.TFrame')
        style.configure('Custom.TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=button_bg, foreground=button_fg)
        style.map('TButton', background=[('active', button_bg)], foreground=[('active', button_fg)])
        style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
        style.map('TCheckbutton', background=[('active', bg_color)])
        style.configure('TEntry', fieldbackground=bg_color, foreground=fg_color)

        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color, which='both')
        for spine in self.ax.spines.values():
            spine.set_edgecolor(fg_color)
            self.ax.xaxis.label.set_color(fg_color)
            self.ax.yaxis.label.set_color(fg_color)
            self.ax.title.set_color(fg_color)

        for widget in self.frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(style='Custom.TLabel')
            elif isinstance(widget, ttk.Entry):
                widget.configure(style='Custom.TEntry')

            style.configure('Custom.TLabel', background=bg_color, foreground=fg_color)
            style.configure('Custom.TEntry', fieldbackground=bg_color, foreground=fg_color)

            self.canvas.draw()

    def on_closing(self):
        self.master.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = IndonesianStockTracker(root)
    root.mainloop()