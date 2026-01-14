class CalculatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # 应用状态
        self.mode = "Standard" # "Standard" or "Programmer"

    def handle_mode_change(self, new_mode_name):
        """处理模式切换"""
        self.view.update_display("0", "")
        
        if new_mode_name == "标准模式":
            self.mode = "Standard"
            self.view.resize_window(340, 520)
            self.view.setup_standard_buttons()
        else:
            self.mode = "Programmer"
            self.view.resize_window(500, 520)
            self.view.setup_programmer_buttons()

    def handle_button_click(self, char):
        """处理所有按钮点击（按 '=' 时读取输入框内容计算）"""
        # 读取当前输入框内容（支持直接键盘输入或按钮输入）
        current = self.view.entry.get()

        # 错误状态重置
        if "Error" in current or "哈哈哈" in current:
            self.view.update_display("0", "")
            if char in ["=", "CLEAR", "Backspace"]:
                return

        if char == 'CLEAR':
            self.view.update_display("0", "")
            return

        if char == '=':
            expr = self.view.entry.get()
            if not expr or expr == "0":
                return
            # 调用 Model 进行计算，直接使用输入框的文本
            result_str, sub_label_str = self.model.evaluate(expr, self.mode)
            self.view.update_display(result_str, sub_label_str)
            return

        if char == 'Backspace':
            new_text = current[:-1]
            display_text = new_text if new_text else "0"

            # 程序员模式下的退格需要更新预览
            sub_text = ""
            if self.mode == "Programmer" and display_text and display_text != "0":
                sub_text = self.model.convert_hex_preview(display_text)

            self.view.update_display(display_text, sub_text)
            return

        # 下面是普通字符（数字/运算符/字母）追加到输入框的逻辑
        # 1. 运算符重复检查
        if char in "+-*/":
            if not current or current == "0":
                return
            if current[-1] in "+-*/":
                return

        # 2. 程序员模式禁用特定字符
        if self.mode == "Programmer" and char in ["."]:
            return

        # 3. 将字符追加到输入框（如果当前为 "0" 则替换）
        if current == "0":
            new_text = str(char)
        else:
            new_text = current + str(char)

        # 实时预览（仅显示十六进制转换提示，不做计算）
        sub_text = None
        if self.mode == "Programmer" and char not in "+-*/":
            sub_text = self.model.convert_hex_preview(new_text if new_text != "0" else "")

        self.view.update_display(new_text, sub_text)