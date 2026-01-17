import customtkinter as ctk
from tkinter import messagebox
import re  # 引入正则模块用于分割数字和运算符

# 设置全局主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基础设置 ---
        self.title("简易计算器 (无eval版)")
        self.geometry("340x480")
        self.resizable(False, False)

        # 运算状态存储
        self.current_value = ""

        # --- 1. 显示区域 ---
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

        # 按钮配置表
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
        if "Error" in self.entry.get() or "error" in self.entry.get():
            self.current_value = ""
            self.update_display("0")
            if char in ["=", "C", "Backspace"]:
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
            if char in "+-*/":
                if not self.current_value:
                    return
                if self.current_value[-1] in "+-*/":
                    return 
            
            self.current_value += str(char)
            self.update_display(self.current_value)

    def update_display(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)

    def safe_parse_and_compute(self, expression):
        """
        核心算法逻辑：
        1. 使用正则将字符串拆分为 token (数字和运算符)。
        2. 第一轮扫描：处理高优先级的乘法 (*) 和除法 (/)。
        3. 第二轮扫描：处理低优先级的加法 (+) 和减法 (-)。
        """
        # 正则表达式拆分：匹配 (数字+可选小数点) 或者 (运算符)
        # 例如 "12+3.5*2" -> ['12', '+', '3.5', '*', '2']
        tokens_raw = re.findall(r'\d+\.?\d*|[-+*/]', expression)
        
        # 将数字字符串转为 float，运算符保持字符串
        tokens = []
        for t in tokens_raw:
            if t in "+-*/":
                tokens.append(t)
            else:
                tokens.append(float(t))

        if not tokens:
            return 0.0

        # --- 第一轮：处理乘除 ---
        # 我们创建一个新的列表来存储处理后的结果
        stack = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # 如果当前是乘除，因为我们是顺序读取，所以操作数是 stack的最后一个元素 和 tokens的下一个元素
            if token == '*' or token == '/':
                if not stack: raise ValueError("Operator Error") # 防止 *3 这种情况
                
                prev_val = stack.pop()    # 取出前一个数字
                next_val = tokens[i+1]    # 取出后一个数字
                
                if token == '*':
                    res = prev_val * next_val
                else:
                    if next_val == 0: raise ZeroDivisionError
                    res = prev_val / next_val
                
                stack.append(res) # 将计算结果放回栈中
                i += 2            # 跳过 运算符 和 下一个数字
            else:
                # 如果是数字或加减，暂时先入栈，留给第二轮处理
                stack.append(token)
                i += 1

        # --- 第二轮：处理加减 ---
        # 此时 stack 里只剩下数字和 + -，例如 [1.0, '+', 5.0, '-', 2.0]
        result = stack[0]
        i = 1
        while i < len(stack):
            op = stack[i]
            val = stack[i+1]
            
            if op == '+':
                result += val
            elif op == '-':
                result -= val
            i += 2
            
        return result

    def calculate(self):
        if not self.current_value:
            return
        
        try:
            # 替换 eval，调用自定义的安全计算函数
            result = self.safe_parse_and_compute(self.current_value)
            
            # 结果格式化逻辑
            if isinstance(result, float):
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
        except Exception as e:
            # print(f"Debug Error: {e}") # 调试用
            self.current_value = ""
            self.update_display("Error")

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()