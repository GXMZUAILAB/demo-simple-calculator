class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # 应用状态
        self.current_value = ""
        self.mode = "Standard" # "Standard" or "Programmer"

    def handle_mode_change(self, new_mode_name):
        """处理模式切换"""
        self.current_value = ""
        self.view.update_display("0", "")
        
        if new_mode_name == "标准模式":
            self.mode = "Standard"
            self.view.resize_window(340, 520)
            self.view.setup_standard_buttons()
        else:
            self.mode = "Programmer"
            self.view.resize_window(500, 520)
            self.view.setup_programmer_buttons()

    def handle_button_click(self, char):
        """处理所有按钮点击"""
        
        # 错误状态重置
        if "Error" in self.current_value or "哈哈哈" in self.current_value:
            self.current_value = ""
            self.view.update_display("0")
            if char in ["=", "CLEAR", "Backspace"]: return

        if char == 'CLEAR':
            self.current_value = ""
            self.view.update_display("0", "")
            
        elif char == '=':
            # 调用 Model 进行计算
            result_str, sub_label_str = self.model.evaluate(self.current_value, self.mode)
            self.current_value = result_str
            self.view.update_display(self.current_value, sub_label_str)
            
        elif char == 'Backspace':
            self.current_value = self.current_value[:-1]
            display_text = self.current_value if self.current_value else "0"
            
            # 程序员模式下的退格需要更新预览
            sub_text = ""
            if self.mode == "Programmer" and self.current_value:
                sub_text = self.model.convert_binary_preview(self.current_value)
            
            self.view.update_display(display_text, sub_text)
            
        else:
            # 普通输入处理
            
            # 1. 运算符重复检查
            if char in "+-*/":
                if not self.current_value: return
                if self.current_value[-1] in "+-*/": return 
            
            # 2. 程序员模式禁用特定字符
            if self.mode == "Programmer" and char in ["."]:
                return

            self.current_value += str(char)
            
            # 3. 实时预览逻辑
            sub_text = None
            if self.mode == "Programmer" and char not in "+-*/":
                sub_text = self.model.convert_binary_preview(self.current_value)

            self.view.update_display(self.current_value, sub_text)