import re
import ast
import operator
import subprocess
import sys

class CalculatorModel:
    def __init__(self):
        self._operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        # 支持的二元运算符映射
        self._bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        # 支持的一元运算符映射
        self._unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.BitAnd: operator.and_,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.Invert: lambda x: ~x,
        }
        # 存储最后一次的运算信息，用于重复运算
        self.last_operand = None  # 最后一个操作数
        self.last_operator = None  # 最后一个运算符
        self.last_result = None  # 最后的结果

    def evaluate(self, expression: str, mode: str) -> tuple[str, str]:
        """
        对外主接口：执行计算并返回 (显示文本, 辅助文本)
        """
        if not expression:
            return "", ""

        is_hex_mode = (mode == "Programmer")

        try:
            # 1. 核心计算
            result = self._compute(expression, is_hex_mode)
            
            # 2. 结果格式化
            return self._format_result(result, is_hex_mode)

        except ZeroDivisionError:
            return "Error: Div 0", ""
        except Exception as e:
            return "Error", ""

    def convert_hex_preview(self, hex_str: str) -> str:
        """程序员模式实时预览"""
        try:
            if hex_str and re.fullmatch(r'[0-9A-Fa-f]+', hex_str):
                return f"DEC: {int(hex_str, 16)}"
        except ValueError:
            pass
        return ""

    def sort_numbers(self, expression: str, is_hex: bool = False) -> tuple[str, str]:
        """处理数值排序逻辑"""
        try:
            # 1. 分割字符串并去除空白
            parts = [p.strip() for p in expression.split(',') if p.strip()]
            
            nums = []

            # 2. 将字符串转换为数字以便正确排序 (防止 "10" 排在 "2" 前面的情况)
            for p in parts:
                if is_hex:
                    nums.append(int(p, 16))  # 16进制转换
                else:
                    # 尝试转为 int，如果是浮点数则转 float
                    try:
                        nums.append(int(p))
                    except ValueError:
                        nums.append(float(p))
            
            # 3. 执行排序
            nums.sort()

            # 4. 重新组合成字符串
            result_parts = []
            for n in nums:
                if is_hex:
                    result_parts.append(f"{n:X}")  # 转回大写HEX
                else:
                    # 处理浮点数显示的 .0 (例如 33.0 -> 33)
                    if isinstance(n, float) and n.is_integer():
                        result_parts.append(str(int(n)))
                    else:
                        result_parts.append(str(n))
            
            return ",".join(result_parts), "Sorted"  # 副标题显示状态

        except Exception:
            # 如果包含非法字符无法排序，返回错误
            return "Error: Sort", ""

    def convert_time(self, expression: str) -> tuple[str, str]:
        """处理时间转换逻辑
        支持格式：
        - "1h" 或 "1H" -> 转换为分钟 (60分钟)
        - "60m" 或 "60M" -> 转换为小时 (1小时)
        """
        try:
            expression = expression.strip()
            
            # 检查是否以 'h' 或 'H' 结尾（小时转分钟）
            if expression.lower().endswith('h'):
                hours_str = expression[:-1].strip()
                hours = float(hours_str)
                minutes = hours * 60
                
                # 格式化输出
                if minutes.is_integer():
                    return f"{int(minutes)}分钟", f"{hours}小时"
                else:
                    return f"{minutes}分钟", f"{hours}小时"
            
            # 检查是否以 'm' 或 'M' 结尾（分钟转小时）
            elif expression.lower().endswith('m'):
                minutes_str = expression[:-1].strip()
                minutes = float(minutes_str)
                hours = minutes / 60
                
                # 格式化输出
                if hours.is_integer():
                    return f"{int(hours)}小时", f"{minutes}分钟"
                else:
                    return f"{hours}小时", f"{minutes}分钟"
            
            else:
                return "Error: Time", ""
        
        except (ValueError, IndexError):
            return "Error: Time", ""

    # ================= 内部逻辑方法 =================

    def _compute(self, expression: str, is_hex: bool):
        """解析字符串并计算数值"""
        if is_hex:
            expression = self._preprocess_hex(expression)

        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            raise ValueError("语法错误")

        return self._eval_node(tree.body, is_hex)

    def _preprocess_hex(self, expression: str) -> str:
        """将十六进制字符串替换为十进制字符串"""
        return re.sub(
            r'\b[0-9A-Fa-f]+\b', 
            lambda m: str(int(m.group(0), 16)), 
            expression
        )

    def _eval_node(self, node, is_hex: bool):
        """递归遍历 AST 节点进行计算"""
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, is_hex)
            right = self._eval_node(node.right, is_hex)
            op_type = type(node.op)

            if op_type in self._bin_ops:
                if op_type == ast.Div:
                    if right == 0: raise ZeroDivisionError
                    return left // right if is_hex else left / right
                return self._bin_ops[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, is_hex)
            op_type = type(node.op)
            if op_type in self._unary_ops:
                return self._unary_ops[op_type](operand)

        raise ValueError(f"不支持的语法节点: {type(node)}")

    def _format_result(self, result, is_hex: bool) -> tuple[str, str]:
        """将数值结果转换为 UI 显示所需的字符串"""
        display_text = ""
        sub_text = ""

        if is_hex:
            int_res = int(result)
            display_text = f"{int_res:X}"
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
