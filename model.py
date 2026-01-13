import re
import ast

class CalculatorModel:
    def __init__(self):
        pass

    def safe_parse_and_compute(self, expression, is_hex=False):
        """使用AST语法树解析计算"""
        try:
            # 预处理：十六进制转换
            if is_hex:
                expression = re.sub(r'[0-9A-Fa-f]+', 
                                lambda m: str(int(m.group(0), 16)), 
                                expression)
            
            # 构建AST语法树
            tree = ast.parse(expression, mode='eval')
            
            # 本地递归函数（不是类方法，只是函数内的局部函数）
            def eval_node(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    
                    if isinstance(node.op, ast.Add):
                        return left + right
                    elif isinstance(node.op, ast.Sub):
                        return left - right
                    elif isinstance(node.op, ast.Mult):
                        return left * right
                    elif isinstance(node.op, ast.Div):
                        if right == 0:
                            raise ZeroDivisionError("除数不能为零")
                        return left // right if is_hex else left / right
                    raise ValueError("不支持的运算符")
                elif isinstance(node, ast.UnaryOp):
                    operand = eval_node(node.operand)
                    if isinstance(node.op, ast.UAdd):
                        return +operand
                    elif isinstance(node.op, ast.USub):
                        return -operand
                    raise ValueError("不支持的运算符")
                raise ValueError("不支持的表达式类型")
            
            return eval_node(tree.body)
            
        except ZeroDivisionError:
            raise
        except Exception as e:
            # 这里的 e 会包含具体错误信息，方便调试（例如 '不支持的表达式类型'）
            raise ValueError(f"表达式解析错误: {str(e)}")

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