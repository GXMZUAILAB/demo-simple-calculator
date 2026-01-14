import customtkinter as ctk

class CalculatorView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.controller = None # 初始化时控制器为空，稍后注入

        # --- 窗口基础设置 ---
        self.title("简易计算器")
        self.geometry("400x520")  # 稍微加宽以适应更多按钮
        self.resizable(False, False)

        # --- 1. 顶部模式切换 ---
        self.mode_segment = ctk.CTkSegmentedButton(
            self, 
            values=["标准模式", "程序员"],
            command=self.on_mode_segment_click
        )
        self.mode_segment.pack(pady=(10, 5))
        self.mode_segment.set("标准模式")

        # --- 2. 显示区域 ---
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.pack(padx=20, pady=(10, 10), fill="x")

        self.entry = ctk.CTkEntry(
            self.display_frame, 
            height=60, 
            font=("Inter", 32, "bold"), 
            justify="right",
            corner_radius=10,
            border_width=2
        )
        self.entry.pack(fill="x")
        self.entry.insert(0, "0")
        
        self.sub_label = ctk.CTkLabel(self.display_frame, text="", font=("Inter", 12), text_color="gray")
        self.sub_label.pack(anchor="e", padx=5)

        # --- 3. 按钮区域容器 ---
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # 初始加载标准按钮
        self.setup_standard_buttons()

    def set_controller(self, controller):
        """注入控制器"""
        self.controller = controller

    def on_mode_segment_click(self, value):
        """当模式切换被点击时，通知控制器"""
        if self.controller:
            self.controller.handle_mode_change(value)

    def update_display(self, main_text, sub_text=None):
        """更新主显示屏"""
        self.entry.delete(0, "end")
        self.entry.insert(0, main_text)
        if sub_text is not None:
            self.sub_label.configure(text=sub_text)

    def resize_window(self, width, height):
        self.geometry(f"{width}x{height}")

    def clear_button_frame(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def setup_standard_buttons(self):
        self.clear_button_frame()
        buttons = [
            ('CLEAR', 0, 0, "danger"), ('Backspace', 0, 1, "action", 2), ('/', 0, 3, "action"),
            ('7', 1, 0, "normal"), ('8', 1, 1, "normal"), ('9', 1, 2, "normal"), ('*', 1, 3, "action"),
            ('4', 2, 0, "normal"), ('5', 2, 1, "normal"), ('6', 2, 2, "normal"), ('-', 2, 3, "action"),
            ('1', 3, 0, "normal"), ('2', 3, 1, "normal"), ('3', 3, 2, "normal"), ('+', 3, 3, "action"),
            ('0', 4, 0, "normal", 2), ('.', 4, 2, "normal"), ('=', 4, 3, "success")
        ]
        self._create_grid(buttons, cols=4)

    def setup_programmer_buttons(self):
        """程序员模式：按照指定布局排列按钮"""
        self.clear_button_frame()
        # 按照指定布局排列
        buttons = [
            ('CLEAR', 0, 0, "danger"), ('Backspace', 0, 1, "action"), ('<<', 0, 2, "action"), ('>>', 0, 3, "action"),
            ('0', 1, 0, "normal"), ('1', 1, 1, "normal"), ('+', 1, 2, "action"), ('-', 1, 3, "action"),
            ('(', 2, 0, "normal"), (')', 2, 1, "normal"), ('*', 2, 2, "action"), ('/', 2, 3, "action"),
            ('NOT', 3, 0, "hex"), ('AND', 3, 1, "hex"), ('OR', 3, 2, "hex"), ('XOR', 3, 3, "hex"),
            ('=', 4, 0, "success", 4)
        ]
        self._create_grid(buttons, cols=4)

    def _create_grid(self, buttons, cols):
        for i in range(cols):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.button_frame.grid_rowconfigure(i, weight=1)

        for btn_data in buttons:
            text = btn_data[0]
            row = btn_data[1]
            col = btn_data[2]
            style = btn_data[3]
            colspan = btn_data[4] if len(btn_data) > 4 else 1
            self.create_button(text, row, col, colspan, style)

    def create_button(self, text, row, col, colspan, style):
        colors = {
            "danger": ("#FF6B6B", "#EE5253"),
            "action": ("#54a0ff", "#2e86de"),
            "success": ("#1dd1a1", "#10ac84"),
            "normal": ("#576574", "#222f3e"),
            "hex":    ("#a5b1c2", "#4b6584") 
        }
        display_text = "C" if text == "CLEAR" else text

        btn = ctk.CTkButton(
            self.button_frame,
            text=display_text, 
            corner_radius=8,
            font=("Inter", 18, "bold"),
            fg_color=colors.get(style, colors["normal"]),
            command=lambda t=text: self.controller.handle_button_click(t) if self.controller else None
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=3, pady=3, sticky="nsew")