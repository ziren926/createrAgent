from gui.main_gui import MainApp
import tkinter as tk

def main():
    # 创建 Tkinter 根窗口
    root = tk.Tk()

    # 初始化并运行主应用
    app = MainApp(root)

    # 启动 Tkinter 主循环
    root.mainloop()

if __name__ == "__main__":
    main()