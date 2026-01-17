import ast
import operator
from typing import Union

class CalculatorModel:
    def __init__(self):
        # 支持的二元运算符映射
        self._bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.BitAnd: operator.and_,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
        }
        # 支持的一元运算符映射
        self._unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Invert: lambda x: ~x,
        }

    def evaluate(self, expression: str, mode: str) -> Union[int, float]:
        """计算表达式并返回数值结果。"""
        if not expression:
            raise ValueError("Empty expression")

        use_int_div = (mode == "Programmer")
        return self._compute(expression, use_int_div)


    def sort_numbers(self, expression: str) -> list[Union[int, float]]:
        """解析并排序数值，返回排序后的数值列表。"""
        parts = [p.strip() for p in expression.split(',') if p.strip()]
        nums: list[Union[int, float]] = []
        for p in parts:
            try:
                nums.append(int(p))
            except ValueError:
                nums.append(float(p))

        nums.sort()
        return nums


    def convert_time(self, expression: str) -> tuple[float, str, float, str]:
        """将小时/分钟表达式转换为对应的另一单位。"""
        expression = expression.strip()

        if expression.lower().endswith('h'):
            hours_str = expression[:-1].strip()
            hours = float(hours_str)
            minutes = hours * 60
            return minutes, 'm', hours, 'h'

        if expression.lower().endswith('m'):
            minutes_str = expression[:-1].strip()
            minutes = float(minutes_str)
            hours = minutes / 60
            return hours, 'h', minutes, 'm'

        raise ValueError('Invalid time expression')


    # ================= 内部逻辑方法 =================

    def _compute(self, expression: str, use_int_div: bool):
        """解析字符串并计算数值"""

        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            raise ValueError("语法错误")

        return self._eval_node(tree.body, use_int_div)

    def _eval_node(self, node, use_int_div: bool):
        """递归遍历 AST 节点进行计算"""
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, use_int_div)
            right = self._eval_node(node.right, use_int_div)
            op_type = type(node.op)

            if op_type in self._bin_ops:
                if op_type == ast.Div:
                    if right == 0: raise ZeroDivisionError
                    return left // right if use_int_div else left / right
                return self._bin_ops[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, use_int_div)
            op_type = type(node.op)
            if op_type in self._unary_ops:
                return self._unary_ops[op_type](operand)

        raise ValueError(f"不支持的语法节点: {type(node)}")

