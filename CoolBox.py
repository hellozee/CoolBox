from krita import *
from PyQt5.QtWidgets import *


DOCKER_NAME = 'CoolBox'
DOCKER_ID = 'pyKrita_CoolBox'

backColor = QColor(49, 49, 49)
highlightColor = QColor(86, 128, 194)

class Tool:

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.subTools = []
        self.isActivated = False
        pass

    def addSubTool(self, tool):
        self.subTools.append(tool)

    def swapTool(self, index):
        if len(self.subTools) <= 0 :
            return
        self.name, self.subTools[index].name = self.subTools[index].name, self.name
        self.icon, self.subTools[index].icon = self.subTools[index].icon, self.icon
    
    def paint(self, painter, rect):
        self.toolRect = rect
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 3, 3)
        color = highlightColor if self.isActivated else backColor 
        painter.fillPath(path, color)
        newRect = rect.adjusted(10, 10, -10, -10)
        icon = Application.icon(self.icon)
        painter.drawPixmap(newRect, icon.pixmap(newRect.size()))
        pass

    def activate(self, clicked):
        self.isActivated = clicked
    
    def contains(self, pos):
        return self.toolRect.contains(pos)

class ToolBox(QWidget):

    def __init__(self):
        super().__init__()
        self.tools = []
        pass
    
    def addTool(self, tool):
        self.tools.append(tool)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawTools(painter, event.rect().topLeft() + QPoint(10, 5))
        painter.end()
    
    def drawTools(self, painter, topLeft):
        size = QSize(40, 40)
        drawRect = QRect(topLeft, size)
        for tool in self.tools:
            drawRect = QRect(topLeft, size)
            tool.paint(painter, drawRect)
            topLeft += QPoint(0, 45)
        self.setFixedSize(50, 45 * len(self.tools))
        pass

    def mousePressEvent(self, event):
        if event.button() is not Qt.LeftButton :
            return
        
        for tool in self.tools:
            tool.activate(tool.contains(event.pos()))


class CoolBox(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_NAME)
        toolBox = ToolBox()
        toolBox.addTool(Tool("Transform Tool", "krita_tool_transform"))
        toolBox.addTool(Tool( "Outline Selection", "tool_outline_selection"))
        toolBox.addTool(Tool("Similar Selection", "tool_similar_selection"))
        toolBox.addTool(Tool("Crop Tool", "tool_crop"))
        toolBox.addTool(Tool("Fill Tool", "krita_tool_color_fill"))
        toolBox.addTool(Tool("Freehand Brush", "krita_tool_freehand"))
        toolBox.addTool(Tool("Rectangle Tool", "krita_tool_rectangle"))
        toolBox.addTool(Tool("Text Tool", "draw-text"))
        toolBox.addTool(Tool("Select Shape", "select"))
        toolBox.addTool(Tool("Assistant Tool", "krita_tool_assistant",))
        toolBox.addTool(Tool("Rectangular Selection", "tool_rect_selection"))
        toolBox.addTool(Tool("Zoom", "tool_zoom"))
        self.setWidget(toolBox)

    def canvasChanged(self, canvas):
        pass

instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID, 
                                        DockWidgetFactoryBase.DockRight, 
                                        CoolBox)

instance.addDockWidgetFactory(dock_widget_factory)