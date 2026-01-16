class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # 应用状态
        self.mode = "Standard" # "Standard" or "Programmer"

    def handle_mode_change(self, new_mode_name):
        """处理模式切换"""
        self.view.update_display("0", "")
        
        if new_mode_name == "标准模式":
            self.mode = "Standard"
            self.view.resize_window(340, 520)
            self.view.setup_standard_buttons()
        else:
            self.mode = "Programmer"
            self.view.resize_window(340, 520)
            self.view.setup_programmer_buttons()

    def handle_button_click(self, char):
        """处理所有按钮点击"""
        current = self.view.entry.get()
        # 错误状态重置
        if "Error" in current or "哈哈哈" in current:
            self.view.update_display("0", "")
            if char in ["=", "CLEAR", "Backspace"]: 
                return

        if char == 'CLEAR':
            self.view.update_display("0", "")
            return
            
        if char == '=':
            expr = self.view.entry.get()
            if not expr or expr == "0":
                return
            
            # 处理 233 彩蛋
            if expr == '233':
                self.view.update_display("哈哈哈", "")
                return
            
            # 处理排序逻辑（检测是否包含逗号）
            if ',' in expr:
                is_binary = (self.mode == "Programmer")
                result_str, sub_label_str = self.model.sort_numbers(expr, is_binary)
                self.view.update_display(result_str, sub_label_str)
                return
            
            # 调用 Model 进行计算
            result_str, sub_label_str = self.model.evaluate(expr, self.mode)
            self.view.update_display(result_str, sub_label_str)
            return
            
        if char == 'Backspace':
            new_text = current[:-1]
            display_text = new_text if new_text else "0"

            # 程序员模式下的退格需要更新预览
            sub_text = ""
            if self.mode == "Programmer" and display_text and display_text != "0":
                sub_text = self.model.convert_binary_preview(display_text)

            self.view.update_display(display_text, sub_text)
            return
            
        # 1. 运算符重复检查
        if char in "+-*/":
            if not current or current == "0": 
                return
            if current[-1] in "+-*/":
                return 
        
        # 2. 程序员模式禁用特定字符
        if self.mode == "Programmer" and char in ["."]:
            return

        if current == "0" and self.mode == "Standard":
            new_text = str(char)
        else:
            new_text = current + str(char)
        
        # 3. 实时预览逻辑
        sub_text = None
        if self.mode == "Programmer" and char not in "+-*/":
            sub_text = self.model.convert_binary_preview(new_text if new_text != "0" else "")

        self.view.update_display(new_text, sub_text)