import re

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
            
            try:
                raw_result = self.model.evaluate(expr, self.mode)
                result_str, sub_label_str = self.format_result(raw_result, expr)
                # 确保结果不为空
                if not result_str or result_str == "":
                    result_str = "Error"
                self.view.update_display(result_str, sub_label_str)
            except Exception as e:
                    self.view.update_display(f"err: {str(e)}", "")
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
    
    def format_result(self, raw_result, original_expr: str = ""):
        """完全合并的格式化函数"""
        if raw_result is None:
            return "Error", ""
        
        # 标准模式
        if self.mode == "Standard":
            if isinstance(raw_result, float):
                raw_result = round(raw_result, 10)
                if raw_result.is_integer():
                    return f"{int(raw_result)}", ""
                return f"{raw_result:.10f}".rstrip('0').rstrip('.'), ""
            return f"{raw_result}", ""
        
        # 程序员模式
        try:
            # raw_result可能是字符串（二进制结果）或数字
            if isinstance(raw_result, str):
                # 如果是二进制字符串，先转换为十进制
                value = int(raw_result, 2) if raw_result else 0
            else:
                # 如果是数字，直接使用
                value = int(raw_result)
        except:
            return "Error", ""
        
        # 计算位宽
        binary_nums = re.findall(r'[01]+', original_expr)
        if binary_nums:
            max_bits = max(len(n) for n in binary_nums)
            val_bits = value.bit_length() if value else 1
            bits = max(max_bits, val_bits)
        else:
            bits = value.bit_length() if value else 1
        
        bits = ((bits + 3) // 4) * 4
        
        # 生成二进制
        if value < 0:
            mask = (1 << bits) - 1
            bin_str = bin(value & mask)[2:].zfill(bits)
        else:
            bin_str = bin(value)[2:].zfill(bits)
        
        # 分组
        rem = len(bin_str) % 4
        if rem:
            bin_str = '0' * (4 - rem) + bin_str
        
        groups = [bin_str[i:i+4] for i in range(0, len(bin_str), 4)]
        return ' '.join(groups), f"DEC: {value}"