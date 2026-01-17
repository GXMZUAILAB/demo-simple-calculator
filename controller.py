import re
import formatter

class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # 应用状态
        self.mode = "Standard" # "Standard" or "Programmer" or "Time"
        self.current_base = "DEC" # "HEX", "DEC", "OCT", "BIN"
        self.last_expression = None  # 存储上一次的表达式
        self.is_result_displayed = False  # showing result flag
        self.last_operator = None  # last operator for repeat equals
        self.last_operand = None  # last operand for repeat equals


    def handle_mode_change(self, new_mode_name):
        """处理模式切换"""
        self.view.update_display("0", "")
        self.is_result_displayed = False
        self.last_expression = None
        self.last_operator = None
        self.last_operand = None
        
        if new_mode_name == "标准模式":
            self.mode = "Standard"
            self.view.resize_window(340, 520)
            self.view.setup_standard_buttons()
        elif new_mode_name == "程序员":
            self.mode = "Programmer"
            self.current_base = "DEC"
            self.view.resize_window(340, 520)
            self.view.setup_programmer_buttons()
            self.view.update_base_selection(self.current_base)
            self.view.update_button_states(self.current_base)
        else:  # 时间模式
            self.mode = "Time"
            self.view.resize_window(340, 520)
            self.view.setup_time_buttons()

    def handle_base_change(self, new_base):
        """处理进制切换"""
        if self.mode != "Programmer" or self.current_base == new_base:
            return
            
        current_expr = self.view.get_display_text()
        try:
            new_expr = self._convert_expression_base(current_expr, self.current_base, new_base)
            self.current_base = new_base
            self.view.update_display(new_expr, "")
            self.view.update_base_selection(self.current_base)
            self.view.update_button_states(self.current_base)
        except Exception:
            # 如果转换失败，不切换进制或显示错误
            pass

    def handle_button_click(self, char):
        """处理所有按钮点击（按 '=' 时读取输入框内容计算）"""
        # 读取当前输入框内容（支持直接键盘输入或按钮输入）
        current = self.view.get_display_text()
        # 错误状态重置
        if "Error" in current or "哈哈哈" in current:
            self.view.update_display("0", "")
            if char in ["=", "CLEAR", "Backspace"]:
                return

        if char == 'CLEAR':
            self.view.update_display("0", "")
            self.is_result_displayed = False
            self.last_expression = None
            self.last_operator = None
            self.last_operand = None
            return

        if char == '=':
            expr = self.view.get_display_text()
            if not expr or expr == "0":
                return
            
            # 时间模式
            if self.mode == "Time":
                try:
                    converted_value, converted_unit, original_value, original_unit = self.model.convert_time(expr)
                    result_str, sub_label_str = formatter.format_time_conversion(
                        converted_value,
                        converted_unit,
                        original_value,
                        original_unit,
                    )
                except (ValueError, IndexError):
                    result_str, sub_label_str = formatter.format_error("time")

                self.view.update_display(result_str, sub_label_str)
                self.is_result_displayed = False
                self.last_expression = None
                return
            
            # 233 彩蛋
            if expr == '233':
                self.view.update_display("哈哈哈", "")
                return
            
            # 处理排序逻辑（检测是否包含逗号）
            if ',' in expr:
                try:
                    numbers = self.model.sort_numbers(expr)
                    result_str, sub_label_str = formatter.format_sorted_numbers(numbers)
                except Exception:
                    result_str, sub_label_str = formatter.format_error("sort")

                self.view.update_display(result_str, sub_label_str)
                self.is_result_displayed = False
                self.last_expression = None
                return
            
            # 检查是否是重复按"="（已显示结果的情况下再按"="）
            if self.is_result_displayed and self.last_expression:
                # 重复运算：用上一次的结果和操作数进行相同的运算
                if self.last_operator and self.last_operand is not None:
                    try:
                        if self.mode == "Programmer":
                            val_dec = int(current, self._base_to_int(self.current_base))
                            eval_expr = f"{val_dec}{self.last_operator}{self.last_operand}"
                        else:
                            eval_expr = f"{current}{self.last_operator}{self.last_operand}"
                        
                        result = self.model.evaluate(eval_expr, self.mode)
                        
                        if self.mode == "Programmer":
                            result_str = self._to_base_string(int(result), self.current_base)
                            sub_label_str = ""
                        else:
                            result_str, sub_label_str = formatter.format_result(result)
                        
                        self.view.update_display(result_str, sub_label_str)
                        return
                    except Exception:
                        pass
            
            # 调用 Model 进行计算
            try:
                eval_expr = expr
                if self.mode == "Programmer":
                    eval_expr = self._convert_expression_to_dec(expr)
                
                result = self.model.evaluate(eval_expr, self.mode)
                
                if self.mode == "Programmer":
                    result_str = self._to_base_string(int(result), self.current_base)
                    sub_label_str = ""
                else:
                    result_str, sub_label_str = formatter.format_result(result)
            except ZeroDivisionError:
                result_str, sub_label_str = formatter.format_error("div0")
            except Exception:
                result_str, sub_label_str = formatter.format_error("generic")

            self.view.update_display(result_str, sub_label_str)
            
            # 提取表达式中的最后一个运算符和操作数
            self._extract_last_operation(expr)
            
            # 标记已显示结果
            self.is_result_displayed = True
            self.last_expression = expr
            return

        if char == 'Backspace':
            new_text = current[:-1]
            display_text = new_text if new_text else "0"

            # 退格时更新显示
            self.view.update_display(display_text, "")
            self.is_result_displayed = False
            return
            
        op_aliases = {"AND": "&", "OR": "|", "XOR": "^", "NOT": "~", "\u00d7": "*", "\u00f7": "/", "\u2212": "-"}
        if char in op_aliases:
            char = op_aliases[char]

        if char == "+/-":
            new_text = self._toggle_sign(current)
            self.view.update_display(new_text, "")
            self.is_result_displayed = False
            return


        # 下面是普通字符（数字/运算符/字母）追加到输入框的逻辑
        # 1. 运算符重复检查
        if char in "+-*/%&|^":
            if not current or current == "0":
                return
            if current[-1] in "+-*/%&|^":
                return


        # 2. 时间模式禁用特定字符
        if self.mode == "Time" and char in ["+-*/%"]:
            return

        # 3. 将字符追加到输入框（如果当前为 "0" 则替换）
        if current == "0":
            new_text = str(char)
        else:
            new_text = current + str(char)

        # 重置结果显示标记（用户开始输入新内容）
        self.is_result_displayed = False

        # 更新输入显示
        self.view.update_display(new_text, None)

    def _convert_expression_base(self, expr, from_base, to_base):
        """转换表达式中所有数字的进制"""
        pattern_map = {
            "HEX": r'[0-9A-Fa-f]+',
            "DEC": r'[0-9]+',
            "OCT": r'[0-7]+',
            "BIN": r'[0-1]+'
        }
        pattern = pattern_map.get(from_base, r'[0-9]+')
        
        def replace_func(match):
            val_str = match.group(0)
            val = int(val_str, self._base_to_int(from_base))
            return self._to_base_string(val, to_base)
            
        return re.sub(pattern, replace_func, expr)

    def _convert_expression_to_dec(self, expr):
        """将表达式中所有数字转换为 10 进制"""
        return self._convert_expression_base(expr, self.current_base, "DEC")

    def _base_to_int(self, base_name):
        return {"HEX": 16, "DEC": 10, "OCT": 8, "BIN": 2}.get(base_name, 10)

    def _to_base_string(self, val, base_name):
        """将数字转换为对应进制的字符串"""
        if val < 0:
            return "-" + self._to_base_string(abs(val), base_name)
        
        if base_name == "HEX":
            return hex(val)[2:].upper()
        elif base_name == "DEC":
            return str(val)
        elif base_name == "OCT":
            return oct(val)[2:]
        elif base_name == "BIN":
            return bin(val)[2:]
        return str(val)

    def _toggle_sign(self, text: str) -> str:
        """切换当前输入的末尾数值符号。"""
        # 程序员模式支持 A-F
        pattern = r"([0-9A-Fa-f]+)$" if self.mode == "Programmer" else r"(\d+(?:\.\d+)?)$"
        match = re.search(pattern, text)
        if not match:
            return text

        start = match.start()
        if start > 0 and text[start - 1] == "-":
            prev = text[start - 2] if start - 2 >= 0 else ""
            if start == 1 or prev.isspace() or prev in "+-*/%&|^<>()":
                return text[:start - 1] + text[start:]

        return text[:start] + "-" + text[start:]

    def _extract_last_operation(self, expression: str):
        """从表达式中提取最后一个运算符和操作数"""
        # 模式：(数字或字母) (运算符) (数字或字母)
        pattern = r'([0-9A-Fa-f.]+)\s*([+\-*/%&|^])\s*([0-9A-Fa-f.]+)$'
        match = re.search(pattern, expression)
        
        if match:
            last_op_str = match.group(3)
            self.last_operator = match.group(2)
            try:
                if self.mode == "Programmer":
                    self.last_operand = int(last_op_str, self._base_to_int(self.current_base))
                else:
                    self.last_operand = float(last_op_str) if '.' in last_op_str else int(last_op_str)
            except Exception:
                self.last_operand = None
                self.last_operator = None
        else:
            self.last_operand = None
            self.last_operator = None
