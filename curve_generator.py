import pcbnew
import os
import wx
import math
import numpy as np
from wx.lib.agw.floatspin import FloatSpin
import gettext
class CurveGeneratorDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = "Curve Equations", pos = wx.DefaultPosition, size = wx.Size( 500,500 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
        self.parent = parent
        self.board = pcbnew.GetBoard()
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 方程类型选择
        type_box = wx.StaticBox(panel, label="方程类型")
        type_sizer = wx.StaticBoxSizer(type_box, wx.VERTICAL)
        
        self.eq_types = ["显式函数 y=f(x)", "参数方程 x=f(t), y=g(t)", "极坐标 r=f(θ)"]
        self.eq_type = wx.RadioBox(panel, choices=self.eq_types, majorDimension=1)
        type_sizer.Add(self.eq_type, 0, wx.EXPAND|wx.ALL, 5)
        
        # 方程输入 - 修正了这里的拼写错误
        eq_box = wx.StaticBox(panel, label="方程输入")
        eq_sizer = wx.StaticBoxSizer(eq_box, wx.VERTICAL)
        
        # 第一方程输入
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label="y= "), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        self.eq_input1 = wx.TextCtrl(panel, style=wx.TE_LEFT)
        hbox1.Add(self.eq_input1, 1, wx.EXPAND)
        eq_sizer.Add(hbox1, 0, wx.EXPAND|wx.ALL, 5)
        # 第二方程输入 (初始隐藏)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label="x= "), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        self.eq_input2 = wx.TextCtrl(panel, style=wx.TE_LEFT)
        hbox2.Add(self.eq_input2, 1, wx.EXPAND)
        eq_sizer.Add(hbox2, 0, wx.EXPAND|wx.ALL, 5)
        #self.eq_input2.Hide()
        
        # 参数范围
        param_box = wx.StaticBox(panel, label="参数范围")
        param_sizer = wx.StaticBoxSizer(param_box, wx.HORIZONTAL)
        
        param_sizer.Add(wx.StaticText(panel, label="从: "), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        self.param_start = wx.SpinCtrlDouble(panel, min=-1000, max=1000, inc=0.1)
        self.param_start.SetDigits(3)
        param_sizer.Add(self.param_start, 0, wx.LEFT|wx.RIGHT, 5)
        
        param_sizer.Add(wx.StaticText(panel, label="到: "), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        self.param_end = wx.SpinCtrlDouble(panel, min=-1000, max=1000, inc=0.1)
        self.param_end.SetValue(20)
        self.param_end.SetDigits(3)
        param_sizer.Add(self.param_end, 0, wx.LEFT|wx.RIGHT, 5)
        
        param_sizer.Add(wx.StaticText(panel, label="步长: "), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        self.param_step = wx.SpinCtrlDouble(panel, min=0.001, max=10, inc=0.01)
        self.param_step.SetValue(0.1)
        self.param_step.SetDigits(3)
        param_sizer.Add(self.param_step, 0, wx.LEFT|wx.RIGHT, 5)
        
        # 图形属性
        prop_box = wx.StaticBox(panel, label="图形属性")
        prop_sizer = wx.StaticBoxSizer(prop_box, wx.HORIZONTAL)
        
        prop_sizer.Add(wx.StaticText(panel, label="层: "), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        self.layer_choice = wx.Choice(panel, choices=self.get_layer_names())
        self.layer_choice.SetSelection(0)
        prop_sizer.Add(self.layer_choice, 0, wx.LEFT|wx.RIGHT, 5)
        
        prop_sizer.Add(wx.StaticText(panel, label="线宽(mm): "), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        self.line_width = wx.SpinCtrlDouble(panel, min=0.01, max=10, inc=0.01)
        self.line_width.SetValue(0.2)
        self.line_width.SetDigits(2)
        prop_sizer.Add(self.line_width, 0, wx.LEFT|wx.RIGHT, 5)
        
        # 按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        generate_btn = wx.Button(panel, label="生成")
        cancel_btn = wx.Button(panel, label="取消")
        
        btn_sizer.Add(generate_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        # 布局
        vbox.Add(type_sizer, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(eq_sizer, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(param_sizer, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(prop_sizer, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        panel.SetSizer(vbox)
        self.Centre()
        
        # 事件绑定
        self.eq_type.Bind(wx.EVT_RADIOBOX, self.on_eq_type_change)
        generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
    
    def on_eq_type_change(self, event):
        """方程类型改变事件"""
        selection = self.eq_type.GetSelection()
        if selection == 1:  # 参数方程
            self.eq_input1.SetLabel("(10+1*t)*cos(t)")
            self.eq_input2.SetLabel("(10+1*t)*sin(t)")
            #self.eq_input2.Show()
        else:
            self.eq_input1.SetLabel("(10+1*t)*cos(t)")


            #self.eq_input2.Hide()
        self.Layout()
        
    def get_layer_names(self):
        """获取所有层名称"""
        layer_names = []
        for i in range(pcbnew.PCB_LAYER_ID_COUNT):
            name = self.board.GetLayerName(i)
            if name:
                layer_names.append(name)
        return layer_names
    
    
    def on_generate(self, event):
        """生成曲线"""
        try:
            # 获取参数
            eq_type = self.eq_type.GetSelection()
            start = self.param_start.GetValue()
            end = self.param_end.GetValue()
            step = self.param_step.GetValue()
            layer_idx = self.layer_choice.GetSelection()
            width = self.line_width.GetValue()  # 转换为纳米
            
            # 生成点集
            if eq_type == 0:  # 显式函数
                equation = self.eq_input1.GetValue()
                points = self.generate_explicit(equation, start, end, step)
            elif eq_type == 1:  # 参数方程
                eq_x = self.eq_input1.GetValue()
                eq_y = self.eq_input2.GetValue()
                points = self.generate_parametric(eq_x, eq_y, start, end, step)
            else:  # 极坐标
                equation = self.eq_input1.GetValue()
                points = self.generate_polar(equation, start, end, step)
            
            # 创建图形
            self.create_graphic(points, layer_idx, width)
            
            # 刷新显示
            pcbnew.Refresh()
            wx.MessageBox("曲线生成成功!", "成功", wx.OK|wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"生成曲线时出错: {str(e)}", "错误", wx.OK|wx.ICON_ERROR)
    
    def on_cancel(self, event):
        """取消"""
        self.EndModal(wx.ID_CANCEL)
    
    def generate_explicit(self, equation, start, end, step):
        """生成显式函数点集"""
        points = []
        x = start
        while x <= end:
            try:
                # 使用eval计算y值，注意安全性问题
                y = eval(equation, {'math': math, 'sin': math.sin, 'cos': math.cos, 
                                   'tan': math.tan, 'sqrt': math.sqrt, 'exp': math.exp,
                                   'log': math.log, 'pi': math.pi, 'e': math.e, 'x': x})
                points.append((x * 1e6, y * 1e6))  # 转换为纳米
            except:
                pass
            x += step
        return points
    
    def generate_parametric(self, eq_x, eq_y, start, end, step):
        """生成参数方程点集"""
        points = []
        t = start
        while t <= end:
            try:
                # 使用eval计算x和y值
                x = eval(eq_x, {'math': math, 'sin': math.sin, 'cos': math.cos, 
                               'tan': math.tan, 'sqrt': math.sqrt, 'exp': math.exp,
                               'log': math.log, 'pi': math.pi, 'e': math.e, 't': t})
                y = eval(eq_y, {'math': math, 'sin': math.sin, 'cos': math.cos, 
                               'tan': math.tan, 'sqrt': math.sqrt, 'exp': math.exp,
                               'log': math.log, 'pi': math.pi, 'e': math.e, 't': t})
                points.append((x * 1e6, y * 1e6))  # 转换为纳米
            except:
                pass
            t += step
        return points
    
    def generate_polar(self, equation, start, end, step):
        """生成极坐标点集"""
        points = []
        theta = start
        while theta <= end:
            try:
                # 使用eval计算r值
                r = eval(equation, {'math': math, 'sin': math.sin, 'cos': math.cos, 
                                    'tan': math.tan, 'sqrt': math.sqrt, 'exp': math.exp,
                                    'log': math.log, 'pi': math.pi, 'e': math.e, 'theta': theta})
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                points.append((x * 1e6, y * 1e6))  # 转换为纳米
            except:
                pass
            theta += step
        return points
    
    def create_graphic(self, points, layer_idx, width):
        """在PCB上创建图形"""
        if len(points) < 2:
            raise ValueError("需要至少两个点来创建图形")
        
        # 创建图形线段
        for i in range(len(points)-1):
            start = pcbnew.VECTOR2I(int(points[i][0]), int(points[i][1]))
            end = pcbnew.VECTOR2I(int(points[i+1][0]), int(points[i+1][1]))
            
            track = pcbnew.PCB_TRACK(self.board)
            track.SetStart(start)
            track.SetEnd(end)
            track.SetWidth(pcbnew.FromMM(width))
            track.SetLayer(layer_idx)
            self.board.Add(track)


class CurveGeneratorPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "曲线方程生成器"
        self.category = "设计工具"
        self.description = "根据数学方程生成曲线图形"
        self.show_toolbar_button = True
        try:
            self.icon_file_name = os.path.join(os.path.dirname(__file__), "curve.png")
        except (FileNotFoundError, Exception):
            pass
    def Run(self):
        # 创建并显示对话框
        dialog = CurveGeneratorDialog(None)
        dialog.Show()
        #dialog.Destroy()

# 插件注册
CurveGeneratorPlugin().register()