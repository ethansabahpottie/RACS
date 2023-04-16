import serial
import time
from grbldriver import GrblDriver
import numpy as np 
import matplotlib.pyplot as plt 
import re
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton,QLabel,QHBoxLayout,QMessageBox,QLineEdit
from PyQt5.QtGui import QPainter, QColor,QPen

import codecs
import os
import threading

from serial.tools.list_ports import comports

import MAC_Control
motordict = {
    'yax':{
        'devname':'yax',
        'stepsperrev':20,
        'leadscrewpitch':3.02,
        'microstep':16,
        'direction':1
        },
    'xax':{
        'devname':'xax',
        'stepsperrev':20,
        'leadscrewpitch':0.5,
        'microstep':16,
        'direction':1
        }
}

motordict['xax']['mmperstep'] = motordict['xax']['leadscrewpitch']/motordict['xax']['stepsperrev']/motordict['xax']['microstep']
motordict['yax']['mmperstep'] = motordict['yax']['leadscrewpitch']/motordict['yax']['stepsperrev']/motordict['yax']['microstep']

SERIAL_ADDRESS = 'COM4'


global motors

global ISHOMED
ISHOMED = False

def initialize():
    global motors
    motors = GrblDriver()
    motors.verify_settings()
    



def go_to_mmx(distance,blockuntilcomplete = True):
    """Move x motor to position indicated by distance(mm).
    
    This moves the x stage to the indicated position.
    Make sure to zero the controller out by using the 'L-'
    command string, so that distance=0 is properly calibrated.

    Distance (mm) is calculated based on configuration
    in motordict dictionary.  Calculation makes use of
    'leadscrewpitch', 'stepsperrev', and 'microstep'.

    Args:
        distance: Distance in mm to move the camera to.
    
    
    global ISHOMED
    if not ISHOMED:
        raise RuntimeError('not homed yet')
    """
    steps = distance/motordict['xax']['mmperstep']
    steps = steps*motordict['xax']['direction']
    
    motors.xmove(steps, blocking = blockuntilcomplete)
    widget2.x_pos = distance
    widget2.x_label.setText(f"X Position: {widget2.x_pos}")

def go_to_mmy(distance,blockuntilcomplete = True):

    """Move y motor to position indicated by distance(mm).
    
    
    Make sure to zero the controller out by using the 'L-'
    command string, so that distance=0 is properly calibrated.

    Distance (mm) is calculated based on configuration
    in motordict dictionary.  Calculation makes use of
    'leadscrewpitch', 'stepsperrev', and 'microstep'.

    Args:
        distance: Distance in mm to move the yax to.
   
    
    global ISHOMED
    if not ISHOMED:
        raise RuntimeError('Not Homed yet')
    """
    steps = distance/motordict['yax']['mmperstep']
    steps = steps*motordict['yax']['direction']
    motors.ymove(steps, blocking = blockuntilcomplete)
    widget2.y_pos = distance
    widget2.y_label.setText(f"Y Position: {widget2.y_pos}")

def get_x_position():
    return motors.get_positions()['X']*motordict['xax']['mmperstep']*motordict['xax']['direction']

def get_Y_position():
    return motors.get_positions()['Y']*motordict['yax']['mmperstep']*motordict['yax']['direction']







def zero_pos():
     
     motors._write("G92 X0 Y0")
     
     
     widget2.zero()



class DirectionalKeypad(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Controller GUI")
        self.resize(1000,800)
        # Create the buttons
        up_button = QPushButton("Up", self)
        down_button = QPushButton("Down", self)
        left_button = QPushButton("Left", self)
        right_button = QPushButton("Right", self)
        Test_button = QPushButton("Test", self)

        MACconfirm_button = QPushButton("Confirm",self)
        self.MACx_input = QLineEdit(self)
        self.MACy_input = QLineEdit(self)


        self.MACx_sel_label = QLabel("Choose X position: ", self)
        self.MACy_sel_label = QLabel("Choose Y Position: ", self)

        self.MACx_input.resize(40,20)
        self.MACy_input.resize(40,20)
        self.MACx_input.move(850,100)
        self.MACy_input.move(850,140)

        self.MACx_sel_label.move(720,100)
        self.MACy_sel_label.move(720,140)

        MACconfirm_button.resize(70,60)
        MACconfirm_button.move(900,100)

        # Create labels to display the current x and y position
        self.MACx_pos = 0
        self.MACy_pos = 0
        self.MACx_label = QLabel("X Position: 0", self)
        self.MACy_label = QLabel("Y Position: 0", self)

        # Set the position and size of each label
        self.MACx_label.move(500, 100)
        self.MACx_label.resize(200, 20)
        self.MACy_label.move(500, 130)
        self.MACy_label.resize(200, 20)
        
        zero_button = QPushButton("Zero", self)
        
        
        confirm_button = QPushButton("Confirm",self)
        

        up_button.resize(50, 30)
        down_button.resize(50, 30)
        left_button.resize(50, 30)
        right_button.resize(50, 30)

        up_button.move(595, 550)
        down_button.move(595, 620)
        left_button.move(540, 585)
        right_button.move(650, 585)

        zero_button.move(800, 560)
        zero_button.resize(100,50)
        Test_button.move(300, 330)

        self.x_input = QLineEdit(self)
        self.y_input = QLineEdit(self)


        self.x_sel_label = QLabel("Choose X position: ", self)
        self.y_sel_label = QLabel("Choose Y Position: ", self)

        self.x_input.resize(40,20)
        self.y_input.resize(40,20)
        self.x_input.move(850,430)
        self.y_input.move(850,470)


        self.x_sel_label.move(720,430)
        self.y_sel_label.move(720,470)

        self.secondary_label = QLabel("Secondary Stage Controls:",self)
        self.secondary_label.move(600,390)

        self.Primary_label = QLabel("Primary Stage Controls:",self)
        self.Primary_label.move(600,60)

        confirm_button.resize(70,60)
        confirm_button.move(900,430)

        # Create labels to display the current x and y position
        self.x_pos = 0
        self.y_pos = 0
        self.x_label = QLabel("X Position: 0", self)
        self.y_label = QLabel("Y Position: 0", self)

        # Set the position and size of each label
        self.x_label.move(530, 430)
        self.x_label.resize(200, 20)
        self.y_label.move(530, 460)
        self.y_label.resize(200, 20)
        
        
        up_button.clicked.connect(lambda: go_to_mmy(self.y_pos +1))
        down_button.clicked.connect(lambda: go_to_mmy(self.y_pos-1))
        left_button.clicked.connect(lambda: go_to_mmx(self.x_pos-1))
        right_button.clicked.connect(lambda: go_to_mmx(self.x_pos+1))
        Test_button.clicked.connect(lambda: welltest())
        zero_button.clicked.connect(lambda: zero_pos())
        confirm_button.clicked.connect(lambda:self.confirm())
        MACconfirm_button.clicked.connect(lambda:self.MacConfirm())
        
    
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
        self.confirm_button = QPushButton('Go to Well', self)
        self.confirm_button.move(30, 300)
        self.confirm_button.clicked.connect(lambda: self.confirm_update())

        self.next_button = QPushButton('Next Well', self)
        self.next_button.move(300, 230)
        self.next_button.clicked.connect(lambda: self.next_update())


        reset_button = QPushButton("Reset", self)
        reset_button.move(300, 280)
        reset_button.clicked.connect(lambda: self.reset_circles())


        
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
                y = -i * spacing + margin + 120
                if i == 0 or i == 2:
                    x += int(spacing/2)
                else:
                     x = -j * spacing + margin + spacing*7



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



        # Show the window
        self.show()

    def zero(self):
         self.x_pos = 0
         self.y_pos = 0
         widget2.y_label.setText(f"Y Position: {self.y_pos}")
         widget2.x_label.setText(f"X Position: {self.x_pos}")
    
    def confirm(self):
             
             x = float(self.x_input.text())
             y = float(self.y_input.text())
             self.x_pos = x
             self.y_pos = y
             self.x_label.setText(f"X Position: {self.x_pos}")
             self.y_label.setText(f"Y Position: {self.y_pos}")
             go_to_mmy(y)
             go_to_mmx(x)

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
        go_to_mmx(wells[index-1][0])
        go_to_mmy(wells[index-1][1])

    def MacConfirm(self):
        MACx = float(self.MACx_input.text())
        MACy = float(self.MACy_input.text())
        self.MACx_label.setText(f"X Position: {MACx}")
        self.MACy_label.setText(f"Y Position: {MACy}")
        
        MAC_Control.Move_x(MACx)
        MAC_Control.Move_y(MACy)
        


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
                go_to_mmx(wells[index-1][0])
                go_to_mmy(wells[index-1][1])
                
            
            
                

    def reset_circles(self):

                self.status_list = [False] *32
                self.current_status = [False] *32
                self.update()
                self.current_col = 0
                self.current_row = 0 
                go_to_mmx(0) 
                go_to_mmy(0)




initialize()

print(get_x_position())
print(get_Y_position())

wells = np.zeros((32,2))

def calc_dropper_line(startx,row,Invert):
    for i in  range(8):
        if Invert:
            wells[7-i+ 8*row][0] = (startx+ (9*i))
        else:
            wells[i+ 8*row][0] = (startx+ (9*i))
        wells[i+ 8*row][1] = ( row*7) 

calc_dropper_line(4.5,0,False)
calc_dropper_line(0,1,True)
calc_dropper_line(4.5,2,False)
calc_dropper_line(0,3,True)

global end_time
end_time = time.time()

def welltest_timer(end_time):
    for i in  range (len(wells)):
        start_time = end_time
        x = wells[i][0]
        y = wells[i][1]
        go_to_mmx(x)
        go_to_mmy(y)
        end_time = time.time()
        elapsed = end_time-start_time
        widget2.next_update()
        print(elapsed)

def welltest():
     
     widget2.current_row = 0
     widget2.current_col = 0
     
     for i in range(32):
        widget2.next_update()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    widget2 = DirectionalKeypad()
    zero_pos()

    MAC_Control.main(default_port=None, default_baudrate=9600, default_type=None, default_cmd=None, X_distance = 100000,Y_distance=100000)
    MAC_Control.main(default_port=None, default_baudrate=9600, default_type=None, default_cmd=None, X_distance = 0,Y_distance=0)
    
    sys.exit(app.exec_())







