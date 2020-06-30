from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

DOCKER_NAME = 'CoolBox'
DOCKER_ID = 'pyKrita_CoolBox'

backColor = QColor(49, 49, 49)
highlightColor = QColor(86, 128, 194)

class Tool:

    def __init__(self, name, icon, action):
        self.name = name
        self.icon = icon
        self.subTools = []
        self.isActivated = False
        self.action = action
        self.highlighted = False
        self.toolRect = QRect()
        pass

    def addSubTool(self, tool):
        self.subTools.append(tool)

    def swapTool(self, index):
        if len(self.subTools) <= 0 :
            return
        self.name, self.subTools[index].name = self.subTools[index].name, self.name
        self.icon, self.subTools[index].icon = self.subTools[index].icon, self.icon
        self.action, self.subTools[index].action = self.subTools[index].action, self.action
        ac = Application.action(self.action)
        if ac:
            ac.trigger()
        
    def paint(self, painter, rect):
        self.toolRect = rect
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 3, 3)
        color = highlightColor if self.isActivated or self.highlighted else backColor 
        painter.fillPath(path, color)
        newRect = rect.adjusted(10, 10, -10, -10)
        icon = Application.icon(self.icon)
        painter.drawPixmap(newRect, icon.pixmap(newRect.size()))

        if len(self.subTools) > 0 :
            triangle = QPainterPath()
            triangle.moveTo(rect.bottomRight())
            triangle.lineTo(rect.bottomRight() + QPoint(0, -5))
            triangle.lineTo(rect.bottomRight() + QPoint(-5, 0))
            painter.fillPath(triangle, Qt.white)

    def activate(self, clicked):
        self.isActivated = clicked
        self.highlighted = False

        if not clicked:
            return

        ac = Application.action(self.action)
        if ac:
            ac.trigger()
    
    def contains(self, pos):
        return self.toolRect.contains(pos)
    
    def setHighlighted(self, highlight):
        self.highlighted = highlight

class Popup(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.tool = Tool("", "", "")
    
    def setTool(self, tool):
        self.tool = tool
        if len(self.tool.subTools) <= 0:
            return
        self.setFixedSize(45, 40 * len(self.tool.subTools))
    
    def paintEvent(self, event):
        if len(self.tool.subTools) <= 0:
            return
        
        painter = QPainter()
        painter.begin(self)
        
        # draw the triangle
        triangle = QPainterPath()
        startPoint = event.rect().topLeft() + QPoint(0, 20)
        triangle.moveTo(startPoint)
        triangle.lineTo(startPoint + QPoint(5, 5))
        triangle.lineTo(startPoint + QPoint(5, -5))
        painter.fillPath(triangle, backColor)

        # draw the subtools
        topLeft = event.rect().topLeft() + QPoint(5, 0)
        size = QSize(40, 40)
        drawRect = QRect(topLeft, size)
        for tool in self.tool.subTools:
            drawRect = QRect(topLeft, size)
            tool.paint(painter, drawRect)
            topLeft += QPoint(0, 40)
        painter.end()
    
    def mouseMoveEvent(self, event):
        for tool in self.tool.subTools:
            tool.setHighlighted(tool.contains(event.pos()))
        self.update()

    def mouseReleaseEvent(self, event):
        i = 0
        for tool in self.tool.subTools:
            if tool.contains(event.pos()):
                self.tool.swapTool(i)
            i += 1

        self.close()
        pass

    def show(self):
        self.grabMouse()
        super().show()
    
    def close(self):
        self.releaseMouse()
        super().close()


class ToolBox(QWidget):

    def __init__(self):
        super().__init__()
        self.tools = []
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.longPressed)
        self.popup = Popup()
        self.setMouseTracking(True)
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
            if tool.contains(event.pos()) :
                self.resetAllTools()
                tool.activate(True)
                self.update()
                self.timer.start()
                self.currentTool = tool
                self.popup.move(self.mapTo(Application.activeWindow().qwindow(), tool.toolRect.topRight()))
                break

    def mouseReleaseEvent(self, event):
        self.timer.stop()

    def mouseMoveEvent(self, event):
        for tool in self.tools:
            tool.setHighlighted(tool.contains(event.pos()))
        self.update()
    
    def leaveEvent(self, event):
        for tool in self.tools:
            tool.setHighlighted(False)
        self.update()
    
    def longPressed(self):
        self.popup.setTool(self.currentTool)
        self.popup.show()
        pass
    
    def resetAllTools(self):
        for tool in self.tools:
            tool.activate(False)

class CoolBox(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_NAME)
        toolBox = ToolBox()

        transformTool = Tool("Transform Tool", "krita_tool_transform", "KisToolTransform")
        transformTool.addSubTool(Tool("Move Tool", "krita_tool_move", "KritaTransform/KisToolMove"))
        toolBox.addTool(transformTool)

        outlineSelect = Tool("Outline Selection", "tool_outline_selection", "KisToolSelectOutline")
        outlineSelect.addSubTool(Tool("Polygonal Selection", "tool_polygonal_selection", "KisToolSelectPolygonal"))
        outlineSelect.addSubTool(Tool("Bezier Selection", "tool_path_selection","KisToolSelectPath"))
        outlineSelect.addSubTool(Tool("Magnetic Selection", "tool_magnetic_selection","KisToolSelectMagnetic"))
        toolBox.addTool(outlineSelect)

        rectSelect = Tool("Rectangular Selection", "tool_rect_selection", "KisToolSelectRectangular")
        rectSelect.addSubTool(Tool("Elliptical Selection", "tool_elliptical_selection", "KisToolSelectElliptical"))
        toolBox.addTool(rectSelect)

        similarSelect = Tool("Similar Selection", "tool_similar_selection", "KisToolSelectSimilar")
        similarSelect.addSubTool(Tool("Contiguous Selection", "tool_contiguous_selection", "KisToolSelectContiguous"))
        toolBox.addTool(similarSelect)

        cropTool = Tool("Crop Tool", "tool_crop", "KisToolCrop")
        toolBox.addTool(cropTool)

        fillTool = Tool("Fill Tool", "krita_tool_color_fill", "KritaFill/KisToolFill")
        fillTool.addSubTool(Tool("Color Picker", "krita_tool_color_picker", "KritaSelected/KisToolColorPicker"))
        fillTool.addSubTool(Tool("Smart Patch Tool", "krita_tool_smart_patch", "KritaShape/KisToolSmartPatch"))
        fillTool.addSubTool(Tool("Gradient Tool", "krita_tool_gradient", "KritaFill/KisToolGradient"))
        toolBox.addTool(fillTool)
        
        brushTool = Tool("Freehand Brush", "krita_tool_freehand", "KritaShape/KisToolBrush")
        brushTool.addSubTool(Tool( "Dynamic Brush", "krita_tool_dyna", "KritaShape/KisToolDyna"))
        brushTool.addSubTool(Tool( "Colorize Brush", "krita_tool_lazybrush", "KritaShape/KisToolLazyBrush"))
        brushTool.addSubTool(Tool("Multibrush", "krita_tool_multihand", "KritaShape/KisToolMultiBrush"))
        toolBox.addTool(brushTool)

        rectTool = Tool("Rectangle Tool", "krita_tool_rectangle", "KritaShape/KisToolRectangle")
        rectTool.addSubTool(Tool("Line Tool", "krita_tool_line", "KritaShape/KisToolLine"))
        rectTool.addSubTool(Tool("Ellipse Tool", "krita_tool_ellipse", "KritaShape/KisToolEllipse"))
        rectTool.addSubTool(Tool("Polygon Tool", "krita_tool_polygon", "KisToolPolygon"))
        rectTool.addSubTool(Tool("Polyline Tool", "polyline", "KisToolPolyline"))
        rectTool.addSubTool(Tool("Bezier Tool", "krita_draw_path","KisToolPath"))
        rectTool.addSubTool(Tool("Freehand Path", "krita_tool_freehandvector", "KisToolPencil"))
        toolBox.addTool(rectTool)

        textTool = Tool("Text Tool", "draw-text", "SvgTextTool")
        toolBox.addTool(textTool)

        shapeSelectTool = Tool("Select Shape", "select", "InteractionTool")
        shapeSelectTool.addSubTool(Tool("Edit Shape Tool", "shape_handling", "PathTool"))
        shapeSelectTool.addSubTool(Tool("Calligraphy", "calligraphy", "KarbonCalligraphyTool"))
        toolBox.addTool(shapeSelectTool)

        assitantTool = Tool("Assistant Tool", "krita_tool_assistant", "KisAssistantTool")
        assitantTool.addSubTool(Tool("Reference Image Tool", "krita_tool_reference_images","ToolReferenceImages"))
        assitantTool.addSubTool(Tool("Measure Tool", "krita_tool_measure", "KritaShape/KisToolMeasure"))
        toolBox.addTool(assitantTool)

        zoomTool = Tool("Zoom", "tool_zoom", "ZoomTool")
        zoomTool.addSubTool(Tool("Pan", "tool_pan", "PanTool"))
        toolBox.addTool(zoomTool)

        self.setWidget(toolBox)
        self.setTitleBarWidget(QWidget())
        self.toolBox = toolBox
        self.toolBox.setEnabled(False)
        self.firstTurn = True

    def canvasChanged(self, canvas):
        # hacky workaround but works
        if not self.firstTurn :
            self.toolBox.setEnabled(canvas is not None)
            self.toolBox.popup.setParent(Application.activeWindow().qwindow())
            return
        
        self.firstTurn = False

instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID, 
                                        DockWidgetFactoryBase.DockRight, 
                                        CoolBox)

instance.addDockWidgetFactory(dock_widget_factory)