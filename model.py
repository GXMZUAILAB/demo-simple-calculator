import re
import ast
import operator

class CalculatorModel:
    def __init__(self):
        # AST节点到operator函数的映射
        self._ast_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }
        
        # 位运算函数映射（按长度降序排列，确保先匹配长运算符）
        self._bitwise_operators = {
            'LSHIFT': operator.lshift,
            'RSHIFT': operator.rshift,
            'AND': operator.and_,
            'OR': operator.or_,
            'XOR': operator.xor,
            'NOT': lambda x: ~x,
        }

    def evaluate(self, expr: str, mode: str) -> tuple[str, str]:
        """计算表达式并返回结果"""
        if not expr or expr.isspace():
            return "", ""
        
        try:
            result = self._compute(expr.strip(), mode == "Programmer")
            return self._format_result(result, mode == "Programmer", expr)
        except ZeroDivisionError:
            return "Error: Div 0", ""
        except Exception:
            return "Error", ""

    def convert_binary_preview(self, bin_str: str) -> str:
        """二进制预览"""
        clean = ''.join(c for c in bin_str if c in '01')
        return f"DEC: {int(clean, 2)}" if clean else ""

    # ================= 核心计算逻辑 =================

    def _compute(self, expr: str, is_binary: bool):
        """统一计算入口"""
        expr = expr.replace(' ', '')
        
        if is_binary:
            expr = self._normalize_binary_expression(expr)
        
        return self._eval_ast(expr, is_binary)

    def _normalize_binary_expression(self, expr: str) -> str:
        """规范化二进制表达式"""
        # 1. 处理位移运算符（<< 和 >> 替换为 LSHIFT 和 RSHIFT）
        expr = expr.replace('<<', 'LSHIFT').replace('>>', 'RSHIFT')
        
        # 2. 按顺序处理所有位运算符
        for op in self._bitwise_operators.keys():
            if op == 'NOT':
                # 处理一元NOT运算：NOT1010 → NOT(10)
                pattern = fr'NOT([01]+)'
                while True:
                    match = re.search(pattern, expr)
                    if not match:
                        break
                    decimal_num = str(int(match.group(1), 2))
                    expr = expr[:match.start()] + f'NOT({decimal_num})' + expr[match.end():]
            else:
                # 处理二元位运算：1010AND1100 → AND(10,12)
                pattern = fr'([01]+){op}([01]+)'
                while True:
                    match = re.search(pattern, expr)
                    if not match:
                        break
                    left_dec = str(int(match.group(1), 2))
                    right_dec = str(int(match.group(2), 2))
                    replacement = f'{op}({left_dec},{right_dec})'
                    expr = expr[:match.start()] + replacement + expr[match.end():]
        
        # 3. 转换剩余的二进制数字为十进制
        def convert_binary(match):
            return str(int(match.group(), 2))
        
        return re.sub(r'\b[01]+\b', convert_binary, expr)

    def _eval_ast(self, expr: str, is_binary: bool):
        """AST解析并计算"""
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body, is_binary)
        except (SyntaxError, ValueError):
            raise ValueError("表达式语法错误")

    def _eval_node(self, node, is_binary: bool):
        """递归计算AST节点"""
        # 常数节点
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, str):
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    raise ValueError(f"无法解析数值: '{value}'")
            
            return int(value) if is_binary and isinstance(value, float) else value
        
        # 二元运算节点
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, is_binary)
            right = self._eval_node(node.right, is_binary)
            op_type = type(node.op)
            
            if op_type not in self._ast_operators:
                raise ValueError(f"不支持的运算符: {op_type.__name__}")
            
            if op_type == ast.Div:
                if right == 0:
                    raise ZeroDivisionError("除数不能为零")
                return left // right if is_binary else left / right
            
            result = self._ast_operators[op_type](left, right)
            return int(result) if is_binary else result
        
        # 一元运算节点
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, is_binary)
            op_type = type(node.op)
            
            if op_type not in self._ast_operators:
                raise ValueError(f"不支持的一元运算符: {op_type.__name__}")
            
            result = self._ast_operators[op_type](operand)
            return int(result) if is_binary else result
        
        # 函数调用节点（位运算）
        if isinstance(node, ast.Call):
            return self._eval_function_call(node, is_binary)
        
        raise ValueError(f"不支持的AST节点类型: {type(node).__name__}")

    def _eval_function_call(self, node: ast.Call, is_binary: bool):
        """计算函数调用（位运算）"""
        if not isinstance(node.func, ast.Name):
            raise ValueError("无效的函数调用语法")
        
        func_name = node.func.id.upper()
        
        if func_name not in self._bitwise_operators:
            raise ValueError(f"不支持的位运算: {func_name}")
        
        args = [int(self._eval_node(arg, True)) for arg in node.args]
        
        if func_name == 'NOT':
            if len(args) != 1:
                raise ValueError("NOT运算需要一个参数")
            return self._bitwise_operators[func_name](args[0])
        
        if len(args) != 2:
            raise ValueError(f"{func_name}运算需要两个参数")
        
        return self._bitwise_operators[func_name](args[0], args[1])

    # ================= 结果格式化 =================

    def _format_result(self, result, is_binary: bool, original: str = ""):
        """格式化计算结果"""
        if not is_binary:
            return self._format_decimal(result), ""
        
        return self._format_binary(result, original)

    def _format_decimal(self, result):
        """格式化十进制结果"""
        if isinstance(result, float):
            result = round(result, 10)
            if result.is_integer():
                return str(int(result))
            result_str = f"{result:.10f}"
            return result_str.rstrip('0').rstrip('.')
        return str(result)

    def _format_binary(self, result, original: str):
        """格式化二进制结果"""
        try:
            int_value = int(result)
        except (ValueError, TypeError):
            return "Error", ""
        
        # 计算合适的显示位宽
        bit_width = self._calculate_bit_width(int_value, original)
        
        # 生成二进制字符串
        binary_str = self._int_to_binary(int_value, bit_width)
        
        # 4位分组
        grouped_binary = self._group_binary(binary_str)
        
        return grouped_binary, f"DEC: {int_value}"

    def _calculate_bit_width(self, value: int, original: str):
        """计算二进制显示的位宽"""
        # 从原始表达式获取二进制数字的位数
        binary_numbers = re.findall(r'[01]+', original)
        
        if binary_numbers:
            max_input_bits = max(len(num) for num in binary_numbers)
            value_bits = value.bit_length() if value != 0 else 1
            needed_bits = max(max_input_bits, value_bits)
        else:
            needed_bits = value.bit_length() if value != 0 else 1
        
        # 向上取整到4的倍数
        return ((needed_bits + 3) // 4) * 4

    def _int_to_binary(self, value: int, bits: int):
        """整数转二进制字符串（考虑负数补码）"""
        if value < 0:
            # 负数的补码表示
            mask = (1 << bits) - 1
            return bin(value & mask)[2:].zfill(bits)
        
        return bin(value)[2:].zfill(bits)

    def _group_binary(self, binary_str: str):
        """二进制字符串4位分组"""
        if not binary_str:
            return "0000"
        
        # 确保长度是4的倍数
        remainder = len(binary_str) % 4
        if remainder:
            binary_str = '0' * (4 - remainder) + binary_str
        
        # 分组并连接
        groups = [binary_str[i:i+4] for i in range(0, len(binary_str), 4)]
        return ' '.join(groups)