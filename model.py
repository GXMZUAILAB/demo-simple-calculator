import re

class CalculatorModel:
    def __init__(self):
        pass

    def safe_parse_and_compute(self, expression, is_hex=False):
        """核心计算逻辑，支持浮点和十六进制"""
        if is_hex:
            tokens_raw = re.findall(r'[0-9A-Fa-f]+|[-+*/]', expression)
        else:
            tokens_raw = re.findall(r'\d+\.?\d*|[-+*/]', expression)
        
        tokens = []
        for t in tokens_raw:
            if t in "+-*/":
                tokens.append(t)
            else:
                if is_hex:
                    tokens.append(int(t, 16))
                else:
                    tokens.append(float(t))

        if not tokens: return 0

        # 处理乘除
        stack = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '*' or token == '/':
                if not stack: raise ValueError
                prev_val = stack.pop()
                if i + 1 >= len(tokens): raise ValueError # 防止溢出
                next_val = tokens[i+1]
                
                if token == '*':
                    res = prev_val * next_val
                else:
                    if next_val == 0: raise ZeroDivisionError
                    res = prev_val // next_val if is_hex else prev_val / next_val
                
                stack.append(res)
                i += 2
            else:
                stack.append(token)
                i += 1

        # 处理加减
        if not stack: return 0
        result = stack[0]
        i = 1
        while i < len(stack):
            op = stack[i]
            val = stack[i+1]
            if op == '+': result += val
            elif op == '-': result -= val
            i += 2
            
        return result

    def evaluate(self, expression, mode):
        """对外暴露的计算接口，处理彩蛋和格式化"""
        if expression == '233':
            return "哈哈哈", ""

        if not expression:
            return "", ""

        try:
            is_hex_mode = (mode == "Programmer")
            result = self.safe_parse_and_compute(expression, is_hex=is_hex_mode)
            
            sub_text = ""
            display_text = ""

            if is_hex_mode:
                int_res = int(result)
                hex_res = hex(int_res).upper().replace("0X", "")
                display_text = hex_res
                sub_text = f"DEC: {int_res}"
            else:
                if isinstance(result, float):
                    result = round(result, 10)
                    if result.is_integer():
                        display_text = str(int(result))
                    else:
                        display_text = str(result)
                else:
                    display_text = str(result)
            
            return display_text, sub_text

        except ZeroDivisionError:
            return "Error: Div 0", ""
        except Exception:
            return "Error", ""

    def convert_hex_preview(self, hex_str):
        """程序员模式下的实时预览转换"""
        try:
            if re.fullmatch(r'[0-9A-Fa-f]+', hex_str):
                val = int(hex_str, 16)
                return f"DEC: {val}"
        except:
            pass
        return ""