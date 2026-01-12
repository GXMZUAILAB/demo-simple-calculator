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
        # self.formula = "" # 移除未使用的变量

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

        # 按钮配置表 (文字, 行, 列, 颜色类型, [跨列数])
        buttons = [
            ('C', 0, 0, "danger"), ('Backspace', 0, 1, "action", 2), ('/', 0, 3, "action"),
            ('7', 1, 0, "normal"), ('8', 1, 1, "normal"), ('9', 1, 2, "normal"), ('*', 1, 3, "action"),
            ('4', 2, 0, "normal"), ('5', 2, 1, "normal"), ('6', 2, 2, "normal"), ('-', 2, 3, "action"),
            ('1', 3, 0, "normal"), ('2', 3, 1, "normal"), ('3', 3, 2, "normal"), ('+', 3, 3, "action"),
            ('0', 4, 0, "normal", 2), ('.', 4, 2, "normal"), ('=', 4, 3, "success")
        ]

        # 配置网格权重
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.button_frame.grid_rowconfigure(i, weight=1)

        # 循环创建按钮
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
            "normal": ("#576574", "#222f3e")
        }
        
        btn = ctk.CTkButton(
            self.button_frame,
            text=text,
            corner_radius=8,
            font=("Inter", 18, "bold"),
            fg_color=colors.get(style, colors["normal"]),
            command=lambda t=text: self.on_button_click(t)
        )
        btn.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="nsew")

    def on_button_click(self, char):
        """处理按钮点击逻辑"""
        # 如果当前显示的是错误信息，点击任何键都先清空
        if "Error" in self.entry.get() or "error" in self.entry.get():
            self.current_value = ""
            self.update_display("0")
            if char in ["=", "C", "Backspace"]: # 如果点的是功能键，直接返回
                return

        if char == 'C':
            self.current_value = ""
            self.update_display("0")
        elif char == '=':
            self.calculate()
        elif char == 'Backspace':
            self.current_value = self.current_value[:-1]
            self.update_display(self.current_value if self.current_value else "0")
        else:
            # 简单的输入限制
            if char in "+-*/":
                # 防止开头就是运算符 (除了负号，但这里简化处理)
                if not self.current_value:
                    return
                # 防止连续输入运算符 (如 1++2)
                if self.current_value[-1] in "+-*/":
                    return # 或者可以替换：self.current_value = self.current_value[:-1] + char
            
            self.current_value += str(char)
            self.update_display(self.current_value)

    def update_display(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)

    def calculate(self):
        """
        修改后的计算函数：
        使用 eval() 自动处理加减乘除和运算优先级。
        """
        if not self.current_value:
            return
        
        try:
            # eval 会自动计算字符串表达式，例如 "1+2*3" -> 7
            # 这里的 logic 会自动支持 + 和 -，不仅仅是 * 和 /
            result = eval(self.current_value)
            
            # 处理结果显示：如果是整数去掉 .0
            if isinstance(result, float):
                # 处理浮点数精度问题（可选，防止 1.0000000002 这种情况）
                result = round(result, 10)
                if result.is_integer():
                    self.current_value = str(int(result))
                else:
                    self.current_value = str(result)
            else:
                self.current_value = str(result)
                
            self.update_display(self.current_value)

        except ZeroDivisionError:
            self.current_value = ""
            self.update_display("Error: Div 0")
        except SyntaxError:
            self.current_value = ""
            self.update_display("Error: Syntax")
        except Exception as e:
            self.current_value = ""
            self.update_display("Error")

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()