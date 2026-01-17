import re

class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # 应用状态
        self.mode = "Standard" # "Standard" or "Programmer" or "Time"
        self.last_expression = None  # 存储上一次的表达式
        self.is_result_displayed = False  # 标记是否正在显示结果


    def handle_mode_change(self, new_mode_name):
        """处理模式切换"""
        self.view.update_display("0", "")
        self.is_result_displayed = False
        self.last_expression = None
        
        if new_mode_name == "标准模式":
            self.mode = "Standard"
            self.view.resize_window(340, 520)
            self.view.setup_standard_buttons()
        elif new_mode_name == "程序员":
            self.mode = "Programmer"
            self.view.resize_window(340, 520)
            self.view.setup_programmer_buttons()
        else:  # 时间模式
            self.mode = "Time"
            self.view.resize_window(340, 520)
            self.view.setup_time_buttons()

    def handle_button_click(self, char):
        """处理所有按钮点击（按 '=' 时读取输入框内容计算）"""
        # 读取当前输入框内容（支持直接键盘输入或按钮输入）
        current = self.view.entry.get()
        # 错误状态重置
        if "Error" in current or "哈哈哈" in current:
            self.view.update_display("0", "")
            if char in ["=", "CLEAR", "Backspace"]:
                return

        if char == 'CLEAR':
            self.view.update_display("0", "")
            self.is_result_displayed = False
            self.last_expression = None
            return

        if char == '=':
            expr = self.view.entry.get()
            if not expr or expr == "0":
                return
            
            # 处理时间模式
            if self.mode == "Time":
                result_str, sub_label_str = self.model.convert_time(expr)
                self.view.update_display(result_str, sub_label_str)
                self.is_result_displayed = False
                self.last_expression = None
                return
            
            # 处理 233 彩蛋
            if expr == '233':
                self.view.update_display("哈哈哈", "")
                return
            
            # 处理排序逻辑（检测是否包含逗号）
            if ',' in expr:
                is_hex = (self.mode == "Programmer")
                result_str, sub_label_str = self.model.sort_numbers(expr, is_hex)
                self.view.update_display(result_str, sub_label_str)
                self.is_result_displayed = False
                self.last_expression = None
                return
            
            # 检查是否是重复按"="（已显示结果的情况下再按"="）
            if self.is_result_displayed and self.last_expression:
                # 重复运算：用上一次的结果和操作数进行相同的运算
                if self.model.last_operator and self.model.last_operand is not None:
                    # 构造新的表达式：结果 + 运算符 + 操作数
                    new_expr = f"{current}{self.model.last_operator}{self.model.last_operand}"
                    try:
                        raw_result = self.model.evaluate(new_expr, self.mode)
                        result_str, sub_label_str = self.format_result(raw_result, expr)
                        # 确保结果不为空
                        if not result_str or result_str == "":
                            result_str = "Error"
                        self.view.update_display(result_str, sub_label_str)
                    except Exception as e:
                            self.view.update_display(f"err: {str(e)}", "")
                    return
            
            # 调用 Model 进行计算，直接使用输入框的文本
            try:
                raw_result = self.model.evaluate(expr, self.mode)
                result_str, sub_label_str = self.format_result(raw_result, expr)
                # 确保结果不为空
                if not result_str or result_str == "":
                    result_str = "Error"
                self.view.update_display(result_str, sub_label_str)
            except Exception as e:
                    self.view.update_display(f"err: {str(e)}", "")
            
            # 提取表达式中的最后一个运算符和操作数
            self._extract_last_operation(expr)
            
            # 标记已显示结果
            self.is_result_displayed = True
            self.last_expression = expr
            return

        if char == 'Backspace':
            new_text = current[:-1]
            display_text = new_text if new_text else "0"

            # 程序员模式下的退格需要更新预览
            sub_text = ""
            if self.mode == "Programmer" and display_text and display_text != "0":
                sub_text = self.convert_binary_preview(display_text)

            self.view.update_display(display_text, sub_text)
            self.is_result_displayed = False
            return

        # 下面是普通字符（数字/运算符/字母）追加到输入框的逻辑
        # 1. 运算符重复检查
        if char in "+-*/":
            if not current or current == "0":
                return
            if current[-1] in "+-*/":
                return

        # 2. 程序员模式禁用特定字符
        if self.mode == "Programmer" and char in ["."]:
            return

        # 2.5 时间模式禁用特定字符
        if self.mode == "Time" and char in ["+-*/"]:
            return

        # 3. 将字符追加到输入框（如果当前为 "0" 则替换）
        if current == "0":
            new_text = str(char)
        else:
            new_text = current + str(char)

        # 重置结果显示标记（用户开始输入新内容）
        self.is_result_displayed = False

        # 实时预览
        sub_text = None
        if self.mode == "Programmer" and char not in "+-*/":
            sub_text = self.convert_binary_preview(new_text if new_text != "0" else "")

        self.view.update_display(new_text, sub_text)

    def _extract_last_operation(self, expression: str):
        """从表达式中提取最后一个运算符和操作数"""
        
        # 使用正则表达式匹配最后一个运算符和其后的操作数
        # 模式：(数字或小数) (运算符) (数字或小数)
        match = re.search(r'([\d.]+)\s*([+\-*/]|<<|>>)\s*([\d.]+)$', expression)
        
        if match:
            # 提取最后的操作数和运算符
            self.model.last_operand = float(match.group(3)) if '.' in match.group(3) else int(match.group(3))
            self.model.last_operator = match.group(2)
        else:
            # 如果没有找到运算符，重置
            self.model.last_operand = None
            self.model.last_operator = None

    def format_result(self, raw_result, original_expr: str = ""):
        """格式化计算结果"""
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
            # raw_result 现在直接是有符号值（如 -1）
            value = int(raw_result)
            signed_value = value  # 保存原始有符号值用于预览
            
            # 计算需要显示的位数（基于输入表达式）
            binary_nums = re.findall(r'[01]+', original_expr)
            if binary_nums:
                max_bits = max(len(n) for n in binary_nums)
                # 对于负数，需要额外1位符号位
                if value < 0:
                    val_bits = abs(value).bit_length() + 1
                else:
                    val_bits = value.bit_length() if value else 1
                bits = max(max_bits, val_bits)
            else:
                if value < 0:
                    bits = abs(value).bit_length() + 1
                else:
                    bits = value.bit_length() if value else 1
            
            # 向上取整到4的倍数，但不超过32位
            bits = ((bits + 3) // 4) * 4
            bits = min(bits, 32)  # 最大32位
            
            # 关键修改：在format_result中进行 & 0xFFFFFFFF
            if value < 0:
                # 使用32位补码表示负数
                mask = (1 << 32) - 1  # 0xFFFFFFFF
                unsigned_value = value & mask
                bin_str = bin(unsigned_value)[2:].zfill(32)
            else:
                # 正数也限制在32位内
                if value >= (1 << 32):
                    value = value & ((1 << 32) - 1)
                bin_str = bin(value)[2:].zfill(bits)
            
            # 确保长度是4的倍数
            rem = len(bin_str) % 4
            if rem:
                bin_str = '0' * (4 - rem) + bin_str
            
            # 4位分组
            groups = [bin_str[i:i+4] for i in range(0, len(bin_str), 4)]
            
            # 返回：二进制字符串（32位补码），预览显示原始有符号值
            return ' '.join(groups), f"DEC: {signed_value}"
            
        except Exception:
            return "Error", ""
    
    def convert_binary_preview(self, bin_str: str) -> str:
        """二进制预览"""
        clean = ''.join(c for c in bin_str if c in '01')
        return f"DEC: {int(clean, 2)}" if clean else ""