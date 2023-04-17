# RACS
Repository of code for Automation of Raman Activated Cell Sorting Final Year Project

This Document serves as a user manual for the scripts in the repository

Integrated.py is the main program however this will not run unless you are connected to an arduino via serial port 

IntegratedGUI.py simulates the GUI so tests can be carried out without having to be in lab

grbldriver.py serves as a driver to convert commands into g-code to the control movmement of the secondary stage

Mac_Control.py serves as a driver o control the movement of the BioPrecision XY (primary) stage 

The Test Button on the integratedGUI will cycle through all wells 
The reset button sets all the statuses of the wells back to empty and the position of the droppper is returned to (0,0)
