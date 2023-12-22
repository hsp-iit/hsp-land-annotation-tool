

# from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage, QColor, QPainter, QRegion
# from PyQt5.QtCore import Qt, QSize, QPoint
# from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QComboBox, QSizePolicy, QLabel, QMenuBar, QInputDialog, QMenu, QAbstractItemView, QTreeView, QMessageBox, QFileDialog, QDialog, QStackedWidget, QListView, QLineEdit

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import * 

import os
import sys
import numpy as np
import cv2
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from ExperimentInfo import ExperimentInfo
from EntityInfo import EntityInfo
from Refinement import Refinement
from Timeline import Timeline

# TODO: move these two constants to a configuration file
FONT_SIZE_CONTROLS = 8 
FONT_SIZE_LABELS = 9

class DataRefinement(QWidget):

    def __init__(self, parent=None):
        super(DataRefinement, self).__init__(parent)
        
        btnSize = QSize(16, 16)
        
        self.entities = dict()
        self.current_entity = None
        self.current_method = None
        self.current_secondary = None
        self.data = None
        self.pickle_files_folder = None
        self.current_mask = None
        
        self.data_is_loaded = False
        
        self.setAcceptDrops(True)

        openButton = QPushButton("Open Video")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))

        prevButton = QPushButton(" < Prev ")   
        prevButton.setFixedHeight(24)
        prevButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        prevButton.clicked.connect(self.prev_frame)

        nextButton = QPushButton(" Next > ")   
        nextButton.setFixedHeight(24)
        nextButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        nextButton.clicked.connect(self.next_frame)

        self.load_stylesheet(prevButton, os.path.join("assets", "stylesheets", "buttons.stylesheet"))
        self.load_stylesheet(nextButton, os.path.join("assets", "stylesheets", "buttons.stylesheet"))

        self.installEventFilter(self)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(prevButton)
        controlLayout.addWidget(nextButton)
        controlLayout.addStretch()

        imagesLayout = QHBoxLayout()
        self.lblImage1 = QLabel()
        self.lblImage2 = QLabel()

        self.pixmap1 = QPixmap(os.path.join("lib","ui","placeholder.png"))
        self.pixmap2 = QPixmap(os.path.join("lib","ui","placeholder.png"))
        current_pixmap1 = self.pixmap1.scaled(self.lblImage1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        current_pixmap2 = self.pixmap2.scaled(self.lblImage1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.lblImage1.setPixmap(current_pixmap1)
        self.lblImage2.setPixmap(current_pixmap2)
        
        self.lblImage1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.lblImage1.setMinimumSize(20, 20) 
        self.lblImage1.setMaximumSize(1500, 1500) 

        self.lblImage2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.lblImage2.setMinimumSize(20, 20) 
        self.lblImage2.setMaximumSize(1500, 1500) 
        
        self.lblImage1.setAlignment(Qt.AlignCenter)
        self.lblImage2.setAlignment(Qt.AlignCenter)
        
        imagesLayout.addWidget(self.lblImage1)
        imagesLayout.addWidget(self.lblImage2)
        
        self.lblImage2.mousePressEvent = self.click_mouse
        
        topLayout = QHBoxLayout()
        topLayout.setContentsMargins(0, 0, 0, 0)

        self.firstButton = QPushButton("Add Item")   
        self.firstButton.setFixedHeight(24)
        self.firstButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        self.firstButton.clicked.connect(self.add_item)

        self.editButton = QPushButton("Edit Item")   
        self.editButton.setFixedHeight(24)
        self.editButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        self.editButton.clicked.connect(self.edit_item)

        self.secondButton = QPushButton(" x1.00 ")   
        self.secondButton.setFixedHeight(24)
        self.secondButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))

        self.load_stylesheet(self.firstButton, os.path.join("assets", "stylesheets", "buttons.stylesheet"))
        self.load_stylesheet(self.editButton, os.path.join("assets", "stylesheets", "buttons.stylesheet"))
        
        self.comboItems = QComboBox()
        self.comboMethod = QComboBox()
        self.comboSecondary = QComboBox()

        self.load_stylesheet(self.comboItems, os.path.join("assets", "stylesheets", "comboboxes.stylesheet"))
        self.load_stylesheet(self.comboMethod, os.path.join("assets", "stylesheets", "comboboxes.stylesheet"))
        self.load_stylesheet(self.comboSecondary, os.path.join("assets", "stylesheets", "comboboxes.stylesheet"))

        self.comboItems.currentTextChanged.connect(self.on_cmb_item_changed)
        self.comboMethod.currentTextChanged.connect(self.on_cmb_method_changed)
        self.comboSecondary.currentTextChanged.connect(self.on_cmb_secondary_changed)

        topLayout.addWidget(self.comboItems)
        topLayout.addWidget(self.firstButton)
        topLayout.addWidget(self.editButton)
        topLayout.addStretch()
        topLayout.addWidget(self.comboMethod)
        topLayout.addWidget(self.comboSecondary)

        # selectStartButton = QPushButton(" Select Start Frame ")   
        selectStartButton = QPushButton(" Select Start  ")   
        selectStartButton.setFixedHeight(24)
        selectStartButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        selectStartButton.clicked.connect(self.start_frame)

        # selectEndButton = QPushButton(" Select End Frame ")   
        selectEndButton = QPushButton(" Select End ")   
        selectEndButton.setFixedHeight(24)
        selectEndButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        selectEndButton.clicked.connect(self.end_frame)

        processButton = QPushButton(" Process ")   
        processButton.setFixedHeight(24)
        processButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        processButton.clicked.connect(self.process)

        refineButton = QPushButton(" Save ")   
        refineButton.setFixedHeight(24)
        refineButton.setFont(QFont("Noto Sans", FONT_SIZE_CONTROLS))
        refineButton.clicked.connect(self.save_annotations)
        
        self.statusLabel = QLabel()
        self.statusLabel.setText("")
        self.statusLabel.setFont(QFont("Noto Sans", FONT_SIZE_LABELS))

        self.timelineLabel = QLabel()
        self.timelineLabel.setText("")
        self.timelineLabel.setFont(QFont("Noto Sans", FONT_SIZE_LABELS))

        bottomLayout = QHBoxLayout()
        bottomLayout.setContentsMargins(0, 0, 0, 0)
        
        bottomLayout.addWidget(prevButton)
        bottomLayout.addWidget(nextButton)
        bottomLayout.addWidget(self.statusLabel)
        bottomLayout.addStretch()
        bottomLayout.addWidget(selectStartButton)
        bottomLayout.addWidget(selectEndButton)
        bottomLayout.addWidget(processButton)
        bottomLayout.addWidget(refineButton)
        
        self.bar = Timeline(self)
        
        barLayout = QHBoxLayout()
        barLayout.addWidget(self.timelineLabel)
        barLayout.addWidget(self.bar)
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(topLayout)
        self.layout.addLayout(imagesLayout)
        self.layout.addLayout(bottomLayout)
        self.layout.addLayout(barLayout)
        
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("File")
        
        self.menuBar.addMenu(self.fileMenu)
        self.fileMenu.addAction("Open", self.open_folders)
        self.layout.setMenuBar(self.menuBar)

        for btn in [selectStartButton, selectEndButton, processButton, refineButton]:
            self.load_stylesheet(btn, os.path.join("assets", "stylesheets", "buttons.stylesheet"))

        self.setLayout(self.layout)        
        self.parent_ui = None
        self.setStyleSheet("background-color: rgb(255, 255, 255);")        
        
        self.saved_items = list()
        self.setting = False
        
        self.cuts = list()
                
        
    def on_cmb_item_changed(self, value):
        
        if self.setting:
            return
        
        if len(self.entities.keys()) == 0:
            return
        
        if len(value.strip()) == 0:
            return
        
        self.current_entity = self.entities[value]    
        self.bar.update_cuts(self.current_entity.cuts, self.infos.get_actual_images_number(), self.current_index)        
        
        print(f"[INT] Set Current Entity to {value}")

    def on_cmb_method_changed(self, value):
        
        print("METHOD CHANGE")
        print(value)
        
        if len(value.strip()) == 0:
            return
        
        if value != self.current_method:
            
            self.current_method = value
            
            print(f"self.current_method: {self.current_method}")
            
            if value in ["clipseg", "seem"]:
                
                self.comboSecondary.clear()
                self.comboSecondary.addItems(self.infos.prompts)
                self.comboSecondary.setCurrentIndex(0)
                
            self.load_images(self.current_index, self.current_method)

    def on_cmb_secondary_changed(self, value):

        print("SEC CHANGE")
        print(value)

        if len(value.strip()) == 0:
            return

        if value != self.current_secondary:
            
            self.current_secondary = value        
            
            if self.current_method in ["clipseg", "seem"]:
                
                self.load_images(self.current_index, self.current_method)

    def save_annotations(self, visualize=False):
        
        base_output_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        for ann_id, ann in enumerate(self.current_entity.annotations):
            
            entity_output_folder = os.path.join(base_output_folder, self.current_entity.name)
            
            os.makedirs(entity_output_folder, exist_ok=True)
            
            if visualize:
            
                window_name = f"Annotation {ann_id+1}"
                
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)        
                
                for (frame_id, (rgb,bw)) in ann:
                                                        
                    cv2.imshow(window_name, rgb)
                    cv2.waitKey(0)
                    
                cv2.destroyWindow(window_name)

            for (frame_id, (rgb,bw)) in ann:
                
                outname = os.path.splitext(os.path.basename(frame_id))[0]
                target_filename = os.path.join(entity_output_folder, f"{outname}.png")
                cv2.imwrite(target_filename, bw)
                    
    def wheelEvent(self, event):
        
        if event.angleDelta().y() > 0:
            self.prev_frame()
        else:
            self.next_frame()

        event.accept() 
        
    def update_current_cuts(self, cuts):
        
        self.current_entity.cuts = cuts    
        
    def show_message_box(self, msg):
        
        message_window = QMessageBox()
        message_window.setIcon(QMessageBox.Warning)
        message_window.setText(msg)
        message_window.setWindowTitle("Message")
        message_window.setStandardButtons(QMessageBox.Ok)
        message_window.exec_()

    def open_folders(self):
        
        def contains_pickle_files(folder):
            target = os.path.join(folder, os.listdir(folder)[0])
            return any([f.endswith(".pkl") for f in os.listdir(target)])
        
        folders = self.get_dirs_from_dialog(directory=".")
        
        for folder in folders[1:]:
            
            print(f"!!!!!! FOLDER: {folder}")
            
            if contains_pickle_files(folder):

                self.pickle_files_folder = folder
        
            else:
                    
                self.infos = ExperimentInfo(folder)
                self.current_index = 0
                
                self.comboMethod.clear()
                self.comboMethod.addItems(self.infos.methods)
                self.comboSecondary.setCurrentIndex(0)
                
                self.load_images(self.current_index, self.current_method)
        
        if self.pickle_files_folder is not None and self.infos is not None:
            self.infos.set_pickle_folder(self.pickle_files_folder)
            self.infos.load_all_data()
            self.timelineLabel.setText("Timeline  ")
            self.data_is_loaded = True
     
    # from https://stackoverflow.com/questions/64336575/select-a-file-or-a-folder-in-qfiledialog-pyqt5
    def get_dirs_from_dialog(self, parent=None, caption='', directory='', 
                            filter='', initialFilter='', options=None):
        def updateText():
            # update the contents of the line edit widget with the selected files
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append('"{}"'.format(index.data()))
            lineEdit.setText(' '.join(selected))

        dialog = QFileDialog(parent, windowTitle=caption)
        dialog.setFileMode(dialog.DirectoryOnly)
        if options:
            dialog.setOptions(options)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        if directory:
            dialog.setDirectory(directory)
        if filter:
            dialog.setNameFilter(filter)
            if initialFilter:
                dialog.selectNameFilter(initialFilter)

        dialog.accept = lambda: QDialog.accept(dialog)

        stackedWidget = dialog.findChild(QStackedWidget)
        view = stackedWidget.findChild(QListView)
        view.setSelectionMode(QAbstractItemView.MultiSelection)
        f_tree_view = dialog.findChild(QTreeView)
        f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

        view.selectionModel().selectionChanged.connect(updateText)

        lineEdit = dialog.findChild(QLineEdit)
        
        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))
        dialog.exec_()
        
        return dialog.selectedFiles()

        
    def load_stylesheet(self, obj, filename):
        
        with open(filename,"r") as fh:
            obj.setStyleSheet(fh.read())
            
    def handle_click_clipseg(self, event):
        
        pass

    def compute_similarity_flow(self, flow_val, flow_matrix):
        
        result = np.zeros((flow_matrix.shape[0], flow_matrix.shape[1]))
        magnitude = np.zeros((flow_matrix.shape[0], flow_matrix.shape[1]))
                
        for row in range(flow_matrix.shape[0]):
            for col in range(flow_matrix.shape[1]):
                magnitude[row][col] = np.linalg.norm(flow_matrix[row][col])
        
        THRESHOLD = 1.5
        
        mask = magnitude >= THRESHOLD
        magnitude[mask] = 255
        mask = magnitude < THRESHOLD
        magnitude[mask] = 0
                        
        cv2.imshow("res", magnitude)
                                  
        return magnitude
        
    def handle_click_unimatch(self, event):
        
        pass                       

    def handle_click_mmpose(self, event):
        
        pass

    def handle_click_spiga(self, event):
        
        pass

    def handle_click_mf2(self, event):
        
        x = event.pos().x() # col
        y = event.pos().y() # row
                
        offx = (self.lblImage2.width() - self.lblImage2.pixmap().width()) / 2
        offy = (self.lblImage2.height() - self.lblImage2.pixmap().height()) / 2

        real_x = int(x - offx)
        real_y = int(y - offy)
        
        if real_x > 0 and real_y > 0 and real_x < self.lblImage2.pixmap().width() and real_y < self.lblImage2.pixmap().height():
                        
            ratio_x = float(real_x) / float(self.lblImage2.pixmap().width())
            ratio_y = float(real_y) / float(self.lblImage2.pixmap().height())
            
            coords_x = int(ratio_x*self.data["masks"].shape[1])
            coords_y = int(ratio_y*self.data["masks"].shape[0])
            
            index = self.data["masks"][coords_y, coords_x]
                      
            if index == 0:
                return
            
            mask = self.data["masks"] == index
            
            zeros = np.zeros(mask.shape)
            red = np.zeros(mask.shape)
            
            red[mask] = 255
           
            self.current_mask = red
            
            red=np.expand_dims(red,axis=2)
            y=np.expand_dims(zeros,axis=2)
            newmask=np.concatenate((red,y,y),axis=2)

            newmask = newmask.astype(np.uint8)

            height, width, channel = newmask.shape
            bytesPerLine = 3 * width
            qImg = QImage(newmask.data, width, height, bytesPerLine, QImage.Format_RGB888)

            self.cc = QPixmap.fromImage(qImg).scaled(self.lblImage2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        
            XX =  self.current_pixmap2.copy()
            
            painter = QPainter(XX)

            painter.setOpacity(0.25)
            pmask = self.cc.createMaskFromColor(QColor(255,0,0), Qt.MaskInColor)
            painter.setClipRegion(QRegion(pmask))
            painter.drawImage(QPoint(), QImage(self.cc))
            painter.end()
            
            self.lblImage2.setPixmap(XX)
            
    def handle_click_seem(self, event):
        
        x = event.pos().x() # col
        y = event.pos().y() # row
                
        offx = (self.lblImage2.width() - self.lblImage2.pixmap().width()) / 2
        offy = (self.lblImage2.height() - self.lblImage2.pixmap().height()) / 2

        real_x = int(x - offx)
        real_y = int(y - offy)
        
        if real_x > 0 and real_y > 0 and real_x < self.lblImage2.pixmap().width() and real_y < self.lblImage2.pixmap().height():
                        
            mask = self.data["mask"] == 1
            
            zeros = np.zeros(mask.shape)
            red = np.zeros(mask.shape)
            
            red[mask] = 255
           
            self.current_mask = red
            
            red=np.expand_dims(red,axis=2)
            y=np.expand_dims(zeros,axis=2)
            newmask=np.concatenate((red,y,y),axis=2)

            newmask = newmask.astype(np.uint8)

            height, width, channel = newmask.shape
            bytesPerLine = 3 * width
            qImg = QImage(newmask.data, width, height, bytesPerLine, QImage.Format_RGB888)

            self.cc = QPixmap.fromImage(qImg).scaled(self.lblImage2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        
            XX =  self.current_pixmap2.copy()
            
            painter = QPainter(XX)

            painter.setOpacity(0.25)
            pmask = self.cc.createMaskFromColor(QColor(255,0,0), Qt.MaskInColor)
            painter.setClipRegion(QRegion(pmask))
            painter.drawImage(QPoint(), QImage(self.cc))
            painter.end()
            
            self.lblImage2.setPixmap(XX)
                        
    def click_mouse(self, event):
        
        if self.data is None:
            return

        func = getattr(self, f'handle_click_{self.current_method}')
        func(event)
        
    def start_frame(self):
        
        if self.current_entity is None:
            self.show_message_box("Current Entity still set to None.")
            return
        
        if self.current_mask is None:
            self.show_message_box("Current mask still set to None.")            
            return
        
        cind = self.infos.get_images().index(self.cur_image)
        self.current_entity.set_start(cind, self.current_mask)

        current_cuts = [c[0] for c in self.current_entity.cuts]

        print("current_cuts:", current_cuts)
        
        if cind in current_cuts:
            return
        
        self.current_entity.previous_cuts.append(list(self.cuts))
    
        self.current_entity.cuts.append((cind, 0))
        self.current_entity.cuts = sorted(self.current_entity.cuts, key=lambda x: x[0])
        self.bar.update_cuts(self.current_entity.cuts, self.infos.get_actual_images_number(), cind)
        
    def end_frame(self):

        if self.current_entity is None:
            self.show_message_box("Current Entity still set to None.")            
            return
        
        cind = self.infos.get_images().index(self.cur_image)
        self.current_entity.set_end(cind, self.current_mask)

        current_cuts = [c[0] for c in self.current_entity.cuts]
        
        if cind in current_cuts and cind != max(current_cuts):
            return
        
        self.current_entity.previous_cuts.append(list(self.cuts))
    
        print(f"cind: {cind}")
        print(f"max(current_cuts: {max(current_cuts)}")
    
        if cind == max(current_cuts):
            self.current_entity.cuts[-1] = (cind,1)
        else:
            self.current_entity.cuts.append((cind, 1))
        
        self.current_entity.cuts = sorted(self.current_entity.cuts, key=lambda x: x[0])
        self.bar.update_cuts(self.current_entity.cuts, self.infos.get_actual_images_number(), cind)

    def process(self):
        
        if self.current_entity is None:
            self.show_message_box("Current Entity still set to None.")
            return
                
        sequences = self.current_entity.get_sequences()
        
        if len(sequences) == 0:
            self.show_message_box("No subsequence to be proccessed.")
            return
            
        refine = Refinement(self.pickle_files_folder)
        
        for seq in sequences:    
        
            print(f"[INT] Processing sequence {seq['start']} - {seq['end']}")
            
            frames = self.infos.get_images(start=seq["start"], end=seq["end"])
            
            refine.set_frames(frames)
            refine.set_starting_mask(seq["mask_1"])
            refine.get_pickle_files(self.current_method, self.current_secondary)
            new_annotation = refine.refine(self.current_method)
                        
            self.current_entity.add_annotation(new_annotation)
            self.current_entity.set_cut_status(seq["end"], 2)
            self.bar.redraw(self.current_index)
            
        print(self.current_entity.cuts)
        
    def load_pickle_files(self, file_path):
        
        self.pickle_files_folder = file_path
        
    def load_pickle_single_file(self, file_path):
           
        if "exp6" in file_path:
            pkl_file = file_path.replace("results_exp6", "results_files_exp6_pickle").replace(".jpg", ".pkl")
        else:
            pkl_file = file_path.replace("results_exp7", "results_files_exp7_pickle").replace(".jpg", ".pkl")
        
        with open(pkl_file, 'rb') as fp:
            self.data = pickle.load(fp)
        
    def load_images(self, index, method):
        
        prompt = None if not self.current_method in ["clipseg", "seem"] else self.current_secondary
        
        path2 = self.infos.get_image_for_method(index, method, prompt)
        
        if path2 is None:
            return False

        path1 = self.infos.get_image_from_result_path(path2)
                                
        self.cur_image = path1        
                
        self.pixmap1 = QPixmap(path1)
        self.pixmap2 = QPixmap(path2)
        
        if self.current_method in ["clipseg", "seem"]:
            self.original_pixmap2_size = self.pixmap2.size()
            self.pixmap2 = self.pixmap2.scaled(self.pixmap1.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                
        self.current_pixmap1 = self.pixmap1.scaled(self.lblImage1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.current_pixmap2 = self.pixmap2.scaled(self.lblImage2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.lblImage1.setPixmap(self.current_pixmap1)
        self.lblImage2.setPixmap(self.current_pixmap2)
        
        self.load_pickle_single_file(path2)
        
        self.statusLabel.setText(f"Frame: {index+1}/{self.infos.get_actual_images_number()}")

        # self.bar.update_cuts(self.cuts, self.infos.get_actual_images_number(), index)
        self.bar.redraw(index)
        
        return True

    def prev_frame(self):
        
        if self.data_is_loaded and self.current_index > 0:
            self.current_index -= 1

            self.load_images(self.current_index, self.current_method)

            self.current_mask = None
        
    def next_frame(self):
        
        if self.data_is_loaded and self.current_index < self.infos.num_images()-1:
            self.current_index += 1

            res = self.load_images(self.current_index, self.current_method)
            
            if not res:
                self.current_index -= 1
            else:
                self.current_mask = None            

    def add_item(self):
        
        if not self.data_is_loaded:
            self.show_message_box("Load some data before creating an item.")            
            return
        
        text, ok = QInputDialog.getText(self, 'Add new Item', 'Enter the new item name:')
        
        self.setting = True
        
        if ok:
            
            text = text.strip()
            
            if text not in self.saved_items:
                self.saved_items.append(text)
                self.comboItems.clear()
                self.comboItems.addItems(self.saved_items)
                self.comboItems.setCurrentIndex(len(self.saved_items)-1)
                
                self.entities[text] = EntityInfo(text)
                self.current_entity = self.entities[text]
                
                self.current_entity.cuts = [(self.infos.get_actual_images_number()-1, 0)]
                self.bar.update_cuts(self.current_entity.cuts, self.infos.get_actual_images_number(), self.current_index)

                
            print(self.entities)
            
        self.setting = False

    def edit_item(self):
        
        if not self.data_is_loaded:
            self.show_message_box("Load some data before editing an item.")                        
            return        

        index = self.comboItems.currentIndex()
        item = self.saved_items[index]
        
        new_text, ok = QInputDialog.getText(self, 'Add new Item', 'Enter the new item name:', text=item)
        
        self.setting = True        
        
        if ok:
        
            new_text = new_text.strip()
            self.saved_items[index] = new_text
            
            self.comboItems.clear()
            self.comboItems.addItems(self.saved_items)
            
            self.comboItems.setCurrentIndex(index)
            self.entities[new_text] = self.entities[item]
            del self.entities[item]
            
            self.current_entity = self.entities[new_text]

        self.setting = False
            
    
    def resizeEvent(self, event):

        self.current_pixmap1 = self.pixmap1.scaled(self.lblImage1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.current_pixmap2 = self.pixmap2.scaled(self.lblImage2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.lblImage1.setPixmap(self.current_pixmap1)
        self.lblImage2.setPixmap(self.current_pixmap2)
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    
    player = DataRefinement()
    player.setWindowTitle("Data Refinement Tool")
    player.show()
    
    sys.exit(app.exec_())
