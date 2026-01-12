# plus.py

def perform_addition(current_val, next_val):
    """
    接收两个字符串或数字，返回相加后的结果
    """
    try:
        result = float(current_val) + float(next_val)
        
        # 如果是整数，去掉小数点（例如 5.0 -> 5）
        if result.is_integer():
            return str(int(result))
        return str(result)
    except ValueError:
        return "Error"