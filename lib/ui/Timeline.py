
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QMessageBox
from PyQt5 import QtGui
from math import ceil

class _Timeline(QWidget):
    pass

    def __init__(self, parent_ui, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.Fixed
        )
        
        self.cuts = list()
        self.duration = 0
        self.parent_ui = parent_ui

        self.colors = dict({"normal": QtGui.QColor(245, 245, 66), 
                            "ready": QtGui.QColor(114, 232, 230), 
                            "done": QtGui.QColor(255, 80, 80), })
        
        
    def mousePressEvent(self, event):

        x = event.pos().x() # col
        width = self.frameGeometry().width() - 1        
        
        if event.button() == Qt.LeftButton:
            pass #TODO: add visualization of the annotation
        elif event.button() == Qt.RightButton:
            self.try_delete_cut(float(x)/width)
        
    def sizeHint(self):
        return QtCore.QSize(40,40)

    def try_delete_cut(self, ratio):

        if len(self.cuts) == 0:
            return
                              
        val = ceil(ratio * self.duration)

        print(f"Frame: {val} of {self.duration}")
        print(f"self.cuts: {self.cuts}")
                    
        for ind in range(len(self.cuts)-1):
            
            if val >= self.cuts[ind][0] and val <= self.cuts[ind+1][0] and self.cuts[ind+1][1] != 0:
                
                print(f"Found val {val} in {self.cuts[ind]} and {self.cuts[ind+1]}")
                
                ret = QMessageBox.question(self,'', "Delete the selected subsequence?", QMessageBox.Yes | QMessageBox.No)
                
                if ret == QMessageBox.Yes:
                
                    if ind < len(self.cuts)-2:
                        
                        to_del = ind+1
                        
                        if self.cuts[ind][1] == 0 and self.cuts[ind][0] != 0:
                            del self.cuts[ind]

                            to_del -= 1
                        
                        if self.cuts[to_del+1][1] == 0:
                            del self.cuts[to_del]

                            to_del -= 1
                            
                    else:
                        
                        if self.cuts[ind][1] == 0 and self.cuts[ind][0] != 0:
                            del self.cuts[ind]

                        self.cuts[-1] = (self.cuts[-1][0], 0)
                    
                    print(f"new self.cuts: {self.cuts}")
                    
                    self.parent_ui.update_current_cuts(self.cuts)
                    self.update()
                    
                break
            

    def update_cuts(self, lst, dur, pos):
        
        self.cuts = lst
        self.duration = dur
        self.curframe = pos
        self.update()
        
        # print(f"update_cuts: self.curframe {self.curframe}, pos {pos}")

    def paintEvent(self, e):
        
        if len(self.cuts) == 0 or self.duration == 0:
            return
        
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.black, 7, Qt.SolidLine))
        brush = QtGui.QBrush()
        brush.setColor(self.colors["normal"])
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width()*((self.duration-1)/self.duration), painter.device().height())
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)        
        painter.drawRect(rect)

        # print(self.cuts)
        
        keys = [c[0] for c in self.cuts]
        
        fractions = [(painter.device().width()/self.duration)*l for l,_ in self.cuts]
        fractions = [0] + fractions
        
        # offset = 0
        used_cuts = self.cuts
        
        if 0 not in keys:
            used_cuts.append((0, 0))
        #     fractions = [0] + fractions
        #     offset = 1
            
        used_cuts = sorted(used_cuts, key=lambda x: x[0])
            
        # print("fractions:", fractions)
        
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)        

        for i in range(len(fractions)-1):
            rect = QtCore.QRect(fractions[i], 0, fractions[i+1]-fractions[i], painter.device().height())
            
            print(used_cuts, i, used_cuts[i][1])
            print()
            
            if len(used_cuts) > 0 and used_cuts[i][1] == 0:
                brush.setColor(self.colors["normal"])
            elif len(used_cuts) > 0 and used_cuts[i][1] == 1:
                brush.setColor(self.colors["ready"])
            else:
                brush.setColor(self.colors["done"])
                
                
            brush.setStyle(Qt.SolidPattern)
            painter.fillRect(rect, brush)
            brush.setColor(QtGui.QColor('black'))
            brush.setStyle(Qt.SolidPattern)        

            painter.drawRect(rect)
            
        # print("self.curframe:", self.curframe)

        painter.setPen(QtGui.QPen(Qt.darkGreen, 2, Qt.SolidLine))
        
        position = painter.device().width()/self.duration * self.curframe     
        rect = QtCore.QRect(position, 0, 2, painter.device().height())

        # print(self.curframe, position)
        
        brush.setColor(QtGui.QColor('brown'))
        brush.setStyle(Qt.SolidPattern)        

        painter.drawRect(rect)

        

class Timeline(QWidget):
    """
    Custom Qt Widget to show a power bar and dial.
    Demonstrating compound and custom-drawn widget.
    """

    def __init__(self, parent_ui, *args, **kwargs):
        super(Timeline, self).__init__(*args, **kwargs)


        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.Fixed
        )

        layout = QVBoxLayout()
        self._bar = _Timeline(parent_ui)
        layout.addWidget(self._bar)

        self.setLayout(layout)
        
    def sizeHint(self):
        return QtCore.QSize(40,50)
        
    def update_cuts(self, lst, duration, position):
        
        self._bar.update_cuts(lst, duration, position)
        
    def redraw(self, position):
        
        self._bar.curframe = position
        self._bar.update()
