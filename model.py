import re
import ast
import operator

class CalculatorModel:
    def __init__(self):
        self._operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.BitAnd: operator.and_,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.Invert: lambda x: ~x,
        }

    def evaluate(self, expr: str, mode: str):
        if not expr or expr.isspace():
            return None

        try:
            if mode == "Programmer":
                return self._binary_calc(expr)
            else:
                return self._decimal_calc(expr)
        except ZeroDivisionError:
            raise ZeroDivisionError("Div 0")
        except Exception as e:
            raise ValueError(f"{str(e)}")

    def _binary_calc(self, expr: str):
        """二进制计算 - 返回有符号值"""
        expr = expr.replace(' ', '')
        if not expr:
            return None
        
        try:
            # 规范化表达式
            expr = expr.replace('<<', 'LSHIFT').replace('>>', 'RSHIFT')
            
            # 处理位运算
            ops = ['AND', 'OR', 'XOR', 'LSHIFT', 'RSHIFT', 'NOT']
            for op in ops:
                if op == 'NOT':
                    pattern = fr'NOT([01]+)'
                    while True:
                        match = re.search(pattern, expr)
                        if not match:
                            break
                        expr = expr[:match.start()] + f'NOT({int(match.group(1), 2)})' + expr[match.end():]
                else:
                    pattern = fr'([01]+){op}([01]+)'
                    while True:
                        match = re.search(pattern, expr)
                        if not match:
                            break
                        expr = expr[:match.start()] + f'{op}({int(match.group(1), 2)},{int(match.group(2), 2)})' + expr[match.end():]
            
            # 转换剩余二进制数
            expr = re.sub(r'\b[01]+\b', lambda m: str(int(m.group(), 2)), expr)
            
            # 计算得到有符号结果
            signed_result = self._eval_ast(expr, True)
            if signed_result is None:
                return None
            
            # 转换为整数（直接返回有符号值）
            signed_result = int(signed_result)
            
            # 返回有符号值，而不是二进制字符串
            return signed_result
            
        except Exception as e:
            raise ValueError(f"{str(e)}")

    def _decimal_calc(self, expr: str):
        expr = expr.replace(' ', '')
        if not expr:
            return None
        
        try:
            result = self._eval_ast(expr, False)
            if result is None:
                return None
            
            if isinstance(result, float):
                result = round(result, 10)
                if result.is_integer():
                    return str(int(result))
                result_str = f"{result:.10f}"
                return result_str.rstrip('0').rstrip('.')
            
            return str(result)
            
        except Exception as e:
            raise ValueError(str(e))

    def _eval_ast(self, expr: str, is_binary: bool):
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body, is_binary)
        except (SyntaxError, ValueError):
            raise ValueError("expr err")

    def _eval_node(self, node, is_binary: bool):
        if isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, str):
                val = float(val) if '.' in val else int(val)
            return int(val) if is_binary and isinstance(val, float) else val
        
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, is_binary)
            right = self._eval_node(node.right, is_binary)
            op_type = type(node.op)
            
            if op_type not in self._operators:
                raise ValueError(f"not support: {op_type.__name__}")
            
            if op_type == ast.Div and right == 0:
                raise ZeroDivisionError("div 0")
            
            if op_type == ast.Div and is_binary:
                return left // right
            
            return self._operators[op_type](left, right)
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, is_binary)
            op_type = type(node.op)
            
            if op_type not in self._operators:
                raise ValueError(f"not support: {op_type.__name__}")
            
            return self._operators[op_type](operand)
        
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("invalid syntax")
            
            func_name = node.func.id.upper()
            
            bitwise_funcs = {
                'LSHIFT': operator.lshift,
                'RSHIFT': operator.rshift,
                'AND': operator.and_,
                'OR': operator.or_,
                'XOR': operator.xor,
                'NOT': lambda x: ~x,
            }
            
            if func_name not in bitwise_funcs:
                raise ValueError(f"not support: {func_name}")
            
            args = [int(self._eval_node(arg, True)) for arg in node.args]
            
            if func_name == 'NOT':
                if len(args) != 1:
                    raise ValueError("NOT missing param")
                return bitwise_funcs[func_name](args[0])
            
            if len(args) != 2:
                raise ValueError(f"{func_name}missing param")
            
            return bitwise_funcs[func_name](args[0], args[1])
        
        raise ValueError(f"not support: {type(node).__name__}")

    def convert_binary_preview(self, bin_str: str) -> str:
        """二进制预览"""
        if not bin_str:
            return ""
        try:
            clean_bin = bin_str.replace(' ', '')
            decimal = int(clean_bin, 2)
            return f"DEC: {decimal}"
        except:
            return ""