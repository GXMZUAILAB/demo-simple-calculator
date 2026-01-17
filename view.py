import customtkinter as ctk

class CalculatorView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.controller = None # 初始化时控制器为空，稍后注入
        self.buttons = {}      # 存储按钮对象
        self.base_buttons = {} # 存储进制切换按钮

        # --- 窗口基础设置 ---
        self.title("简易计算器")
        self.geometry("340x520")
        self.resizable(False, False)

        # --- 1. 顶部模式切换 ---
        self.mode_segment = ctk.CTkSegmentedButton(
            self, 
            values=["标准模式", "程序员", "时间"], 
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

        # --- 2.5 进制切换区域 (仅程序员模式) ---
        self.base_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self._setup_base_buttons()

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

    def get_display_text(self):
        """Get current text from the main display."""
        return self.entry.get()

    def resize_window(self, width, height):
        self.geometry(f"{width}x{height}")

    def clear_button_frame(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.buttons = {}

    def _setup_base_buttons(self):
        """创建 HEX, DEC, OCT, BIN 按钮"""
        bases = ["HEX", "DEC", "OCT", "BIN"]
        for base in bases:
            btn = ctk.CTkButton(
                self.base_frame,
                text=base,
                height=24,
                font=("Inter", 12, "bold"),
                anchor="w",
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("#dfe4ea", "#2f3542"),
                command=lambda b=base: self.controller.handle_base_change(b) if self.controller else None
            )
            btn.pack(fill="x", pady=1)
            self.base_buttons[base] = btn

    def update_base_selection(self, active_base):
        """高亮当前选中的进制按钮"""
        colors = {
            "active": ("#48dbfb", "#0984e3"),
            "inactive": "transparent"
        }
        text_colors = {
            "active": "white",
            "inactive": ("gray20", "gray80")
        }
        for base, btn in self.base_buttons.items():
            if base == active_base:
                btn.configure(fg_color=colors["active"], text_color=text_colors["active"])
            else:
                btn.configure(fg_color=colors["inactive"], text_color=text_colors["inactive"])

    def set_base_frame_visibility(self, visible):
        """控制进制切换区域的显示/隐藏"""
        if visible:
            self.base_frame.pack(fill="x", pady=(5, 0))
        else:
            self.base_frame.pack_forget()

    def update_button_states(self, base):
        """根据当前进制禁用不适用的按钮"""
        hex_chars = "ABCDEF"
        digits = "0123456789"
        
        valid_chars = ""
        if base == "HEX":
            valid_chars = digits + hex_chars
        elif base == "DEC":
            valid_chars = digits
        elif base == "OCT":
            valid_chars = "01234567"
        elif base == "BIN":
            valid_chars = "01"
            
        for char, btn in self.buttons.items():
            if char in hex_chars + digits:
                state = "normal" if char in valid_chars else "disabled"
                btn.configure(state=state)
            
            # 程序员模式通常不支持小数点
            if char == ".":
                btn.configure(state="disabled")

    def setup_standard_buttons(self):
        self.set_base_frame_visibility(False)
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
        self.set_base_frame_visibility(True)
        self.clear_button_frame()
        buttons = [
            ("A", 0, 0, "hex", 1), ("<<", 0, 1, "action"), (">>", 0, 2, "action"),
            ("CLEAR", 0, 3, "danger"), ("Backspace", 0, 4, "action"),
            ("B", 1, 0, "hex", 1), ("(", 1, 1, "normal"), (")", 1, 2, "normal"),
            ("%", 1, 3, "action"), ("÷", 1, 4, "action"),
            ("C", 2, 0, "hex", 1), ("7", 2, 1, "normal"), ("8", 2, 2, "normal"),
            ("9", 2, 3, "normal"), ("×", 2, 4, "action"),
            ("D", 3, 0, "hex", 1), ("4", 3, 1, "normal"), ("5", 3, 2, "normal"),
            ("6", 3, 3, "normal"), ("−", 3, 4, "action"),
            ("E", 4, 0, "hex", 1), ("1", 4, 1, "normal"), ("2", 4, 2, "normal"),
            ("3", 4, 3, "normal"), ("+", 4, 4, "action"),
            ("F", 5, 0, "hex", 1), ("+/-", 5, 1, "action"), ("0", 5, 2, "normal"),
            (".", 5, 3, "normal"), ("=", 5, 4, "success"),
        ]
        self._create_grid(buttons, cols=5)

    def setup_time_buttons(self):
        """设置时间模式按钮"""
        self.set_base_frame_visibility(False)
        self.clear_button_frame()
        buttons = [
            ('CLEAR', 0, 0, "danger"), ('Backspace', 0, 1, "action", 2), ('=', 0, 3, "success"),
            ('1', 1, 0, "normal"), ('2', 1, 1, "normal"), ('3', 1, 2, "normal"), ('h', 1, 3, "time"),
            ('4', 2, 0, "normal"), ('5', 2, 1, "normal"), ('6', 2, 2, "normal"), ('m', 2, 3, "time"),
            ('7', 3, 0, "normal"), ('8', 3, 1, "normal"), ('9', 3, 2, "normal"), ('.', 3, 3, "normal"),
            ('0', 4, 0, "normal", 3)
        ]
        self._create_grid(buttons, cols=4)

    def _create_grid(self, buttons, cols):
        rows = max((btn[1] for btn in buttons), default=-1) + 1
        for i in range(cols):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.button_frame.grid_rowconfigure(i, weight=1)

        for btn_data in buttons:
            text = btn_data[0]
            row = btn_data[1]
            col = btn_data[2]
            style = btn_data[3]
            colspan = btn_data[4] if len(btn_data) > 4 else 1
            state = btn_data[5] if len(btn_data) > 5 else "normal"
            self.create_button(text, row, col, colspan, style, state)

    def create_button(self, text, row, col, colspan, style, state="normal"):
        colors = {
            "danger": ("#FF6B6B", "#EE5253"),
            "action": ("#54a0ff", "#2e86de"),
            "success": ("#1dd1a1", "#10ac84"),
            "normal": ("#576574", "#222f3e"),
            "hex":    ("#a5b1c2", "#4b6584"),
            "time":   ("#f368e0", "#d946ef"),
            "info":   ("#48dbfb", "#0984e3")
        }
        display_text = "C" if text == "CLEAR" else "⌫" if text == "Backspace" else text

        btn = ctk.CTkButton(
            self.button_frame,
            text=display_text,
            corner_radius=8,
            font=("Inter", 18, "bold"),
            fg_color=colors.get(style, colors["normal"]),
            state=state,
            command=lambda t=text: self.controller.handle_button_click(t) if self.controller else None
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=3, pady=3, sticky="nsew")
        self.buttons[text] = btn
