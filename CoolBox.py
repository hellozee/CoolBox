from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


DOCKER_NAME = 'CoolBox'
DOCKER_ID = 'pyKrita_CoolBox'

backColor = QColor(0, 0, 0, 0)
highlightColor = QColor(50, 50, 50)

class Tool:

    def __init__(self, name, icon, action):
        self.name = name
        self.icon = icon
        self.subTools = []
        self.isActivated = False
        self.action = action
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

        if not clicked:
            return
        
        ac = Application.action(self.action)
        if ac:
            ac.trigger() 
    
    def contains(self, pos):
        return self.toolRect.contains(pos)

class ToolBox(QWidget):

    def __init__(self):
        super().__init__()
        self.tools = []
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.longPressed)
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
        self.setFixedSize(50, 45 * len(self.tools) + 5)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton :
            return

        for tool in self.tools:
            tool.activate(tool.contains(event.pos()))
            self.update()
        self.timer.start()

    def mouseReleaseEvent(self, event):
        self.timer.stop()
    
    def longPressed(self):
        pass

    


class CoolBox(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_NAME)
        toolBox = ToolBox()

        toolBox.addTool(Tool("Transform Tool", "krita_tool_transform", "KisToolTransform"))
        toolBox.addTool(Tool("Outline Selection", "tool_outline_selection", "KisToolSelectOutline"))
        toolBox.addTool(Tool("Rectangular Selection", "tool_rect_selection", "KisToolSelectRectangular"))
        toolBox.addTool(Tool("Similar Selection", "tool_similar_selection", "KisToolSelectSimilar"))
        toolBox.addTool(Tool("Crop Tool", "tool_crop", "KisToolCrop"))
        toolBox.addTool(Tool("Fill Tool", "krita_tool_color_fill", "KritaFill/KisToolFill"))
        toolBox.addTool(Tool("Freehand Brush", "krita_tool_freehand", "KritaShape/KisToolBrush"))
        toolBox.addTool(Tool("Rectangle Tool", "krita_tool_rectangle", "KritaShape/KisToolRectangle"))
        toolBox.addTool(Tool("Text Tool", "draw-text", "SvgTextTool"))
        toolBox.addTool(Tool("Select Shape", "select", "InteractionTool"))
        toolBox.addTool(Tool("Assistant Tool", "krita_tool_assistant", "KisAssistantTool"))
        toolBox.addTool(Tool("Zoom", "tool_zoom", "ZoomTool"))

        self.setWidget(toolBox)

    def canvasChanged(self, canvas):
        pass

instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID, 
                                        DockWidgetFactoryBase.DockRight, 
                                        CoolBox)

instance.addDockWidgetFactory(dock_widget_factory)