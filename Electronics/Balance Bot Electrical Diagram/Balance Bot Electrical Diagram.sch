EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Raspberry_Pi_2_3 J?
U 1 1 5FC33708
P 9600 3200
F 0 "J?" H 9600 4681 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 9600 4590 50  0000 C CNN
F 2 "" H 9600 3200 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 9600 3200 50  0001 C CNN
	1    9600 3200
	1    0    0    -1  
$EndComp
$Comp
L Regulator_Switching:LM2596T-ADJ U?
U 1 1 5FC4150C
P 7900 1150
F 0 "U?" H 7900 1517 50  0000 C CNN
F 1 "LM2596T-ADJ" H 7900 1426 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical" H 7950 900 50  0001 L CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm2596.pdf" H 7900 1150 50  0001 C CNN
	1    7900 1150
	1    0    0    -1  
$EndComp
$Comp
L Regulator_Switching:LM2596T-ADJ U?
U 1 1 5FC4B0E2
P 6450 1150
F 0 "U?" H 6450 1517 50  0000 C CNN
F 1 "LM2596T-ADJ" H 6450 1426 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical" H 6500 900 50  0001 L CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm2596.pdf" H 6450 1150 50  0001 C CNN
	1    6450 1150
	1    0    0    -1  
$EndComp
$Comp
L Device:Battery BT?
U 1 1 5FC4BA6F
P 10450 1000
F 0 "BT?" H 10558 1046 50  0000 L CNN
F 1 "Battery" H 10558 955 50  0000 L CNN
F 2 "" V 10450 1060 50  0001 C CNN
F 3 "~" V 10450 1060 50  0001 C CNN
	1    10450 1000
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_DPST_x2 SW?
U 1 1 5FC54469
P 9850 950
F 0 "SW?" H 9850 1185 50  0000 C CNN
F 1 "SW_DPST_x2" H 9850 1094 50  0000 C CNN
F 2 "" H 9850 950 50  0001 C CNN
F 3 "~" H 9850 950 50  0001 C CNN
	1    9850 950 
	1    0    0    -1  
$EndComp
Wire Wire Line
	10450 800  10050 800 
Wire Wire Line
	10050 800  10050 950 
Wire Wire Line
	10400 3900 10400 3700
Wire Wire Line
	10400 1250 8400 1250
Connection ~ 10400 2300
Wire Wire Line
	10400 2300 10400 1250
Connection ~ 10400 2400
Wire Wire Line
	10400 2400 10400 2300
Connection ~ 10400 2600
Wire Wire Line
	10400 2600 10400 2400
Connection ~ 10400 2700
Wire Wire Line
	10400 2700 10400 2600
Connection ~ 10400 2900
Wire Wire Line
	10400 2900 10400 2700
Connection ~ 10400 3000
Wire Wire Line
	10400 3000 10400 2900
Connection ~ 10400 3100
Wire Wire Line
	10400 3100 10400 3000
Connection ~ 10400 3300
Wire Wire Line
	10400 3300 10400 3100
Connection ~ 10400 3400
Wire Wire Line
	10400 3400 10400 3300
Connection ~ 10400 3500
Wire Wire Line
	10400 3500 10400 3400
Connection ~ 10400 3600
Wire Wire Line
	10400 3600 10400 3500
Connection ~ 10400 3700
Wire Wire Line
	10400 3700 10400 3600
Connection ~ 8400 1250
Wire Wire Line
	8400 1250 7400 1250
$EndSCHEMATC
