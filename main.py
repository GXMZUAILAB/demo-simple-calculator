import customtkinter as ctk
from model import CalculatorModel
from view import CalculatorView
from controller import CalculatorController

# 设置全局主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    # 1. 创建模型
    model = CalculatorModel()
    
    # 2. 创建视图
    view = CalculatorView()
    
    # 3. 创建控制器，并将模型和视图绑定
    controller = CalculatorController(model, view)
    
    # 4. 将控制器反向注入视图，以便视图能触发事件
    view.set_controller(controller)
    
    # 5. 启动主循环
    view.mainloop()