import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton,QLabel,QHBoxLayout,QMessageBox,QLineEdit
from PyQt5.QtGui import QPainter, QColor,QPen

class CircleWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Wells Status')
        self.setGeometry(100, 100, 300, 300)
        self.status_list = [False] * 32 # Initialize list of statuses as all False (empty)
        self.current_status= [False] *32

        row_label = QLabel(self)
        row_label.setText("Select a row:")
        row_label.move(30, 220)

        col_label = QLabel(self)
        col_label.setText("Select a column:")
        col_label.move(150, 220)

        # Add row and column selectors
        self.row_selector = QComboBox(self)
        self.row_selector.addItems(['1', '2', '3', '4'])
        self.row_selector.move(30, 250)
        self.col_selector = QComboBox(self)
        self.col_selector.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
        self.col_selector.move(150, 250)

        # Add confirm button
        self.confirm_button = QPushButton('Update', self)
        self.confirm_button.move(30, 300)
        self.confirm_button.clicked.connect(self.confirm_update)

        self.next_button = QPushButton('Next Well', self)
        self.next_button.move(300, 250)
        self.next_button.clicked.connect(self.next_update)


        reset_button = QPushButton("Reset", self)
        reset_button.move(300, 300)
        reset_button.clicked.connect(self.reset_circles)


        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle('Wells Status')
        self.show()

        self.current_row = int(0)
        self.current_col = int(0)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_circles(qp)
        qp.end()

    def draw_circles(self, qp):
        brush = QColor(0, 0, 0)
        pen = QColor(0, 0, 0)
        size = self.size()

        # Set up grid of circles
        radius = 30
        spacing = 40
        margin = 30
        rows = 4
        cols = 8

        # Draw circles and status indicators
        for i in range(rows):
            for j in range(cols):
                x = j * spacing + margin
                y = i * spacing + margin
                if i == 1 or i == 3:
                    x += int(spacing/2)


                if self.status_list[i*cols + j]:
                    brush = QColor(0, 255, 0) # Set color to red for full circle
                else:
                    brush = QColor(183, 184, 185) # Set color to black for empty circle


                if self.current_status[i*cols + j]:
                    pen = QPen(QColor("#34495E"), 3)
                    
                    
                else:
                    pen = QPen(QColor("#34495E"), 1)
                qp.setBrush(brush)
                qp.setPen(pen)
                qp.drawEllipse(x, y, radius, radius)
    

    def confirm_update(self):
        self.current_status = [False] *32
        self.update()
        row = int(self.row_selector.currentText()) - 1
        col = int(self.col_selector.currentText()) - 1
        index = row * 8 + col
        self.status_list[index] = not self.status_list[index]
        self.current_status[index] = not self.current_status[index]
        self.update()
        
        index += 1 
        self.current_col = index%8
        self.current_row = index//8

    def next_update(self):
            row = int(self.current_row) 
            col = int(self.current_col)
            index = row * 8 + col
            if (index < 32):
                self.status_list[index] = not self.status_list[index]
                if(index >0):
                    self.current_status[index] = not self.current_status[index]
                    
                    self.update()
                    self.current_status[index-1] = not self.current_status[index]
                    
                else:
                    self.current_status[index] = not self.current_status[index]
                    
                    self.update()
                index += 1 
                self.current_col = index%8
                self.current_row = index//8
            
            
                

    def reset_circles(self):

                self.status_list = [False] *32
                self.current_status = [False] *32
                self.update()
                self.current_col = 0
                self.current_row = 0  
    
                              


class DirectionalKeypad(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Controller GUI")
        self.resize(600,400)
        # Create the buttons
        up_button = QPushButton("Up", self)
        down_button = QPushButton("Down", self)
        left_button = QPushButton("Left", self)
        right_button = QPushButton("Right", self)
        close_button = QPushButton("Close", self)
        stop_button = QPushButton("Stop", self)
        zero_button = QPushButton("Zero", self)
        reset_button = QPushButton("Reset", self)
        
        confirm_button = QPushButton("Confirm",self)
        

        up_button.resize(50, 30)
        down_button.resize(50, 30)
        left_button.resize(50, 30)
        right_button.resize(50, 30)

        up_button.move(95, 150)
        down_button.move(95, 220)
        left_button.move(40, 185)
        right_button.move(150, 185)

        zero_button.move(370, 140)
        close_button.move(370, 180)
        stop_button.move(370, 220)
        reset_button.move(370, 260)

        self.x_input = QLineEdit(self)
        self.y_input = QLineEdit(self)


        self.x_sel_label = QLabel("Choose X position: ", self)
        self.y_sel_label = QLabel("Choose Y Position: ", self)

        self.x_input.resize(40,20)
        self.y_input.resize(40,20)
        self.x_input.move(350,30)
        self.y_input.move(350,70)

        self.x_sel_label.move(220,30)
        self.y_sel_label.move(220,70)

        confirm_button.resize(70,60)
        confirm_button.move(400,30)

        # Create labels to display the current x and y position
        self.x_pos = 0
        self.y_pos = 0
        self.x_label = QLabel("X Position: 0", self)
        self.y_label = QLabel("Y Position: 0", self)

        # Set the position and size of each label
        self.x_label.move(30, 30)
        self.x_label.resize(100, 20)
        self.y_label.move(30, 60)
        self.y_label.resize(100, 20)
        
        
        up_button.clicked.connect(lambda: go_to_mmy(1))
        down_button.clicked.connect(lambda: go_to_mmy(-1))
        left_button.clicked.connect(lambda: go_to_mmx(-1))
        right_button.clicked.connect(lambda: go_to_mmx(1))
        #close_button.clicked.connect(lambda: close)
        #stop_button.clicked.connect(lambda: stop)
        zero_button.clicked.connect(lambda: zero_pos())
        #reset_button.clicked.connect(lambda:reset)
        confirm_button.clicked.connect(lambda:self.confirm())
        

        # Set the layout for the window
       

        # Show the window
        self.show()
    def zero(self):
         self.x_pos = 0
         self.y_pos = 0
         widget2.y_label.setText(f"Y Position: {self.y_pos}")
         widget2.x_label.setText(f"X Position: {self.x_pos}")
    
    def confirm(self):
         try:
             x = int(self.x_input.text())
             y = int(self.y_input.text())
             self.x_pos = x
             self.y_pos = y
             self.x_label.setText(f"X Position: {self.x_pos}")
             self.y_label.setText(f"Y Position: {self.x_pos}")
         except ValueError:
              QMessageBox.warning(self, "Co-ordinates have to be integer values")
 
         
         

def go_to_mmy(dist):
            
            widget2.y_pos += dist
            widget2.y_label.setText(f"Y Position: {widget2.y_pos}")


def go_to_mmx(dist):
            
            widget2.x_pos += dist
            widget2.x_label.setText(f"X Position: {widget2.x_pos}")




def zero_pos():
     '''
     motors._write("G92 X0 Y0")
     
     '''
     widget2.zero()
     

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = CircleWidget()
    widget.show()
    widget2 = DirectionalKeypad()
    widget2.show()
    sys.exit(app.exec_())
