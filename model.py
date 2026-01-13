import re
import ast

class CalculatorModel:
    def __init__(self):
        pass

    def safe_parse_and_compute(self, expression, is_hex=False):
        """使用AST语法树解析计算，支持浮点和十六进制"""
        try:
            # 预处理：十六进制转换
            if is_hex:
                # 将十六进制字符串转换为十进制整数
                def hex_to_decimal(match):
                    hex_str = match.group(0)
                    return str(int(hex_str, 16))
                
                # 替换所有十六进制数为十进制数
                expression = re.sub(r'[0-9A-Fa-f]+', hex_to_decimal, expression)
            
            # 构建AST语法树
            tree = ast.parse(expression, mode='eval')
            
            # 自定义访问器类
            class SafeEvaluator(ast.NodeVisitor):
                def __init__(self):
                    self.result = None
                
                def visit_Expression(self, node):
                    self.result = self.visit(node.body)
                
                # --- 关键修复：兼容 Python 3.8+ ---
                def visit_Constant(self, node):
                    return node.value

                # 兼容旧版本 Python (3.7及以下)
                def visit_Num(self, node):
                    return node.n
                
                def visit_BinOp(self, node):
                    left = self.visit(node.left)
                    right = self.visit(node.right)
                    
                    if isinstance(node.op, ast.Add):
                        return left + right
                    elif isinstance(node.op, ast.Sub):
                        return left - right
                    elif isinstance(node.op, ast.Mult):
                        return left * right
                    elif isinstance(node.op, ast.Div):
                        if right == 0:
                            raise ZeroDivisionError("除数不能为零")
                        # 十六进制模式下使用整数除，普通模式使用浮点除
                        if is_hex:
                            return left // right
                        else:
                            return left / right
                    else:
                        raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
                
                def visit_UnaryOp(self, node):
                    operand = self.visit(node.operand)
                    if isinstance(node.op, ast.UAdd):
                        return +operand
                    elif isinstance(node.op, ast.USub):
                        return -operand
                    else:
                        raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
                
                def generic_visit(self, node):
                    raise ValueError(f"不支持的表达式类型: {type(node).__name__}")
            
            # 执行计算
            evaluator = SafeEvaluator()
            evaluator.visit(tree)
            
            return evaluator.result
            
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