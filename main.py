import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import TimelapseApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = TimelapseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
