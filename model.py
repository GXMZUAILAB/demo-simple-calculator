import re
import ast
import operator

class CalculatorModel:
    def __init__(self):
        # 运算符映射表
        self._ops = {
            # 算术运算
            ast.Add: operator.add,
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            
            # 一元运算
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            
            # 位运算函数名映射
            'AND': operator.and_,
            'OR': operator.or_,
            'XOR': operator.xor,
            'LSHIFT': operator.lshift,
            'RSHIFT': operator.rshift,
        }

    def evaluate(self, expr: str, mode: str) -> tuple[str, str]:
        """计算表达式并返回结果"""
        if expr == '233':
            return "哈哈哈", ""
        if not expr:
            return "", ""

        try:
            result = self._compute(expr, mode == "Programmer")
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
        """解析并计算表达式"""
        if not expr:
            return 0
            
        expr = expr.replace(' ', '')
        
        if is_binary:
            # 预处理二进制和位运算
            processed = self._preprocess_expr(expr)
            return self._eval_ast(processed, True)
        return self._eval_ast(expr, False)

    def _preprocess_expr(self, expr: str) -> str:
        """预处理表达式"""
        # 二进制转十进制
        expr = re.sub(r'[01]+', lambda m: str(int(m.group(), 2)), expr)
        
        # 处理位移运算符
        expr = expr.replace('<<', ' LSHIFT ').replace('>>', ' RSHIFT ')
        
        # 标准化位运算格式
        expr = re.sub(r'NOT\s*(\d+)', r'NOT(\1)', expr)
        
        # 处理二元位运算
        for op in ['AND', 'OR', 'XOR', 'LSHIFT', 'RSHIFT']:
            expr = re.sub(fr'(\d+)\s*{op}\s*(\d+)', fr'{op}(\1,\2)', expr)
        
        return expr

    def _eval_ast(self, expr: str, is_binary: bool):
        """AST解析计算"""
        if not expr:
            return 0
            
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body, is_binary)
        except SyntaxError:
            raise ValueError("表达式语法错误")

    def _eval_node(self, node, is_binary: bool):
        """递归计算AST节点"""
        # 处理函数调用（位运算）
        if isinstance(node, ast.Call):
            return self._eval_bitwise_call(node, is_binary)
        
        # 处理常数
        if isinstance(node, ast.Constant):
            return node.value

        # 处理二元算术运算
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, is_binary)
            right = self._eval_node(node.right, is_binary)
            op_type = type(node.op)

            if op_type in self._ops:
                if op_type == ast.Div:
                    if right == 0: 
                        raise ZeroDivisionError("除数不能为零")
                    return left // right if is_binary else left / right
                
                result = self._ops[op_type](left, right)
                return int(result) if is_binary and op_type != ast.Div else result

        # 处理一元运算
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, is_binary)
            op_type = type(node.op)
            
            if op_type in self._ops:
                result = self._ops[op_type](operand)
                return int(result) if is_binary else result

        raise ValueError(f"不支持的语法节点: {type(node)}")

    def _eval_bitwise_call(self, node: ast.Call, is_binary: bool):
        """处理位运算函数调用"""
        if not isinstance(node.func, ast.Name):
            raise ValueError("无效的函数调用")
        
        func_name = node.func.id
        args = [self._eval_node(arg, is_binary) for arg in node.args]
        
        # NOT运算（一元）
        if func_name == 'NOT':
            if len(args) != 1:
                raise ValueError("NOT运算需要一个参数")
            return ~int(args[0])
        
        # 二元位运算
        if func_name in self._ops:
            if len(args) != 2:
                raise ValueError(f"{func_name}运算需要两个参数")
            return self._ops[func_name](int(args[0]), int(args[1]))
        
        raise ValueError(f"不支持的函数: {func_name}")

    # ================= 结果格式化 =================

    def _format_result(self, result, is_binary: bool, original: str = "") -> tuple[str, str]:
        """格式化结果"""
        if not is_binary:
            return self._format_std(result), ""

        int_res = int(result)
        
        # 确定目标显示长度
        lengths = [len(m) for m in re.findall(r'[01]+', original)]
        target = lengths[0] if len(set(lengths)) == 1 and lengths else max(lengths) if lengths else 0
        
        # 生成二进制字符串
        if int_res < 0:
            bin_str = bin(int_res & 0xFFFFFFFF)[2:].zfill(32)
        else:
            bin_str = bin(int_res)[2:]
            if target and len(bin_str) < target:
                bin_str = bin_str.zfill(target)
        
        return bin_str or "0", f"DEC: {int_res}"

    def _format_std(self, result):
        """格式化标准结果"""
        if isinstance(result, float):
            result = round(result, 10)
            if result.is_integer():
                return str(int(result))
        return str(result)