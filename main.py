import customtkinter as ctk
from tkinter import messagebox

# 设置全局主题
ctk.set_appearance_mode("dark")  # 开启深色模式
ctk.set_default_color_theme("blue") # 主题色：蓝色

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基础设置 ---
        self.title("简易计算器")
        self.geometry("340x480")
        self.resizable(False, False)

        # 运算状态存储
        self.current_value = ""
        self.formula = ""

        # --- 1. 显示区域 ---
        # 使用 Frame 包裹 Entry 增加边距感
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.pack(padx=20, pady=(30, 10), fill="x")

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

        # --- 2. 按钮区域 ---
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # 按钮配置表 (文字, 行, 列, 颜色类型)
        buttons = [
            ('C', 0, 0, "danger"), ('Backspace', 0, 1, "action",2), ('/', 0, 3, "action"),
            ('7', 1, 0, "normal"), ('8', 1, 1, "normal"), ('9', 1, 2, "normal"), ('*', 1, 3, "action"),
            ('4', 2, 0, "normal"), ('5', 2, 1, "normal"), ('6', 2, 2, "normal"), ('-', 2, 3, "action"),
            ('1', 3, 0, "normal"), ('2', 3, 1, "normal"), ('3', 3, 2, "normal"), ('+', 3, 3, "action"),
            ('0', 4, 0, "normal", 2), ('.', 4, 2, "normal"), ('=', 4, 3, "success")
        ]

        # 配置网格权重，使按钮均匀分布
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.button_frame.grid_rowconfigure(i, weight=1)

        # 循环创建按钮
        for btn_data in buttons:
            text, row, col, style = btn_data[0:4]
            colspan = btn_data[4] if len(btn_data) > 4 else 1
            
            self.create_button(text, row, col, colspan, style)

    def create_button(self, text, row, col, colspan, style):
        # 根据不同风格设置颜色
        colors = {
            "danger": ("#FF6B6B", "#EE5253"),  # 清除键
            "action": ("#54a0ff", "#2e86de"),  # 运算符
            "success": ("#1dd1a1", "#10ac84"), # 等号
            "normal": ("#576574", "#222f3e")   # 数字
        }
        
        btn = ctk.CTkButton(
            self.button_frame,
            text=text,
            corner_radius=8,
            font=("Inter", 18, "bold"),
            fg_color=colors[style],
            command=lambda t=text: self.on_button_click(t)
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="nsew")

    def on_button_click(self, char):
        """处理按钮点击逻辑"""
        if char == 'C':
            self.current_value = ""
            self.update_display("0")
        elif char == '=':
            self.calculate()
        elif char == 'Backspace':
            self.current_value = self.current_value[:-1]
            self.update_display(self.current_value if self.current_value else "0")
        else:
            # 简单的输入限制（防止多个小数点等）
            if char in "+-*/" and (not self.current_value or self.current_value[-1] in "+-*/"):
                return
            self.current_value += str(char)
            self.update_display(self.current_value)

    def update_display(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)

    def calculate(self):
        if not self.current_value:
            return
        
        # 处理数字
        parts = [] # 储存解析内容
        tmp = "" 
        for char in self.current_value:
            if char in "*/":
                if tmp:
                    parts.append(float(tmp)) # 将 * 或 / 前的数字存入parts
                    parts.append(char)
                    tmp = ""
            else:
                tmp += char

        if tmp:
            parts.append(float(tmp)) # 将最后的数字存入
        
        # 防止 1* 或 1/ 之类的情况
        if len(parts) < 3:
            return
        
        # 处理计算
        result = parts[0]
        for index in range(1, len(parts), 2): # 两个两个读取
            operator = parts[index]
            next_num = parts[index + 1]

            # 添加操作
            if operator == "*":
                result *= next_num
            elif operator == "/":
                if next_num == 0:
                    self.update_display("Error")
                    return
                result /= next_num

        if result.is_integer():
            self.current_value = str(int(result))
        else:
            self.current_value = str(result)
            
        # 更新显示
        self.update_display(self.current_value)

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()