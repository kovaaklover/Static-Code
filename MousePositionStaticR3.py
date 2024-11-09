# NOTE ENTER IN INPUTS AND THEN START CODE
# MOVEMENT FOR FIRST 5 SECONDS NOT TRACKED SO SCENARIO CAN BE STARTED

# IMPORTS
import numpy as np
import pyautogui
import datetime
import csv
import matplotlib.pyplot as plt
import math
from scipy.interpolate import interp1d

# INPUTS
Test_Name = 'test 1'
Total_Run_Time = 70  # How Many Seconds Code Runs For
X_Resolution = 1920  # Monitor Pixels in the X
Y_Resolution = 1080  # Monitor Pixels in the Y
MonitorSize = 24.5  # Inches
Time_Step = 0.01  # SAMPLE RATE (DO NOT CHANGE FROM 0.01)

# FOR BETTER PLOTTING
TimeL = 1  # MAX TIME TO MAKE LONG FLICK
TimeM = 0.8  # MAX TIME TO MAKE MEDIUM FLICK
TimeS = 0.6  # MAX TIME TO MAKE SHORT FLICK

VelocityL = 200  # MAX VELOCITY LONG FLICK
VelocityM = 150  # MAX VELOCITY MEDIUM FLICK
VelocityS = 100  # MAX VELOCITY SHORT FLICK

Show_Micro_Start = "N"  # IF YOU WANT TO SEE A POINT ON THE GRAPH WHERE THE MICRO STARTS "Y" or "N"

# STORAGE LISTS DEFINED
T, X, Y, D, P, kF, Px, Py, Ax, Ay, Clicks, FlickEnd = [], [], [], [0], [], [], [], [], [], [], [], []

# INITIALIZE TIME PARAMETERS
TimeStart = datetime.datetime.now()
Current_Run_Time = datetime.datetime.now() - TimeStart
Sample_Time = Current_Run_Time

# MONITER DIMENTIONS
Factor = ((X_Resolution**2+Y_Resolution**2)**0.5)/MonitorSize
X_Dim = X_Resolution/Factor
Y_Dim = Y_Resolution/Factor

# ITERATE THOUGH TIME
while Current_Run_Time.total_seconds() <= Total_Run_Time:
    Current_Run_Time = datetime.datetime.now() - TimeStart

    # IF CURRENT TIME IS GREATER THAN Sample Time + Time Step, GET MOUSE POSITION AND APPEND DATA TO T X AND Y LISTS
    if Sample_Time.total_seconds() + Time_Step <= Current_Run_Time.total_seconds():
        Position = pyautogui.position()
        Sample_Time = datetime.datetime.now() - TimeStart
        T.append(Sample_Time.total_seconds())
        X.append(Position[0] / X_Resolution * X_Dim)
        Y.append(Y_Dim - Position[1] / Y_Resolution * Y_Dim)

# CALCULATE TOTAL DISTANCE TRAVELED
for i in range(1, len(T)):
    del_D = ((X[i] - X[i - 1]) ** 2 + (Y[i] - Y[i - 1]) ** 2) ** 0.5
    D.append(del_D + D[i - 1])

# VELOCITY AND ACCELERATION CALCULATIONS
V = np.gradient(D, T)
A = np.gradient(V, T)

# ITERATE THROUGH FLICK ARRAY TO DETERMINE IF END OF A FLICK
T_F = []
D_F = []
for i in range(0, len(V)):
    if i > 500:

        # LOTS OF VELOCITY POINTS BELOW 10 MS
        if V[i] <= 10 and V[i-1] <= 10 and V[i-2] <= 10 and V[i-3] <= 10:
            Clicks.append("Y")
        else:
            Clicks.append("N")

            # IF FIRST "N" AFTER A NEW FLICK ITERATE BACK TO FIND POINT WHERE VELOCITY INCREASES
            if Clicks[-2] == "Y":
                for ii in range(i-1, 500, -1):
                    if V[ii-1] > V[ii] or V[ii] <= 0.001:
                        FlickEnd.append(ii)
                        T_F.append(T[ii])
                        D_F.append(D[ii])
                        break

    else:
        Clicks.append("N")

# ITERATE THROUGH THE FLICK END ARRAY
FlickLength, FlickAngle, FlickT, FlickLT = [], [], [], []

maxFlickL = 0
for i in range(1, len(FlickEnd)):

    # FLICK LENGTH INCH
    FlickLength.append(D[FlickEnd[i]]-D[FlickEnd[i-1]])

    if FlickLength[-1] > maxFlickL:
        maxFlickL = FlickLength[-1]

    # FLICK ANGLE
    XC = X[FlickEnd[i]]-X[FlickEnd[i-1]]
    YC = Y[FlickEnd[i]]-Y[FlickEnd[i-1]]
    try:
        value = math.degrees(math.atan(XC/YC))
    except:
        value = 0
    if XC > 0 and YC > 0:
        value = 90 - value
    elif XC < 0 and YC > 0:
        value = 90+value*-1
    elif XC < 0 and YC < 0:
        value = 90 + value * -1+180
    elif XC > 0 and YC < 0:
        value = 270 + value*-1
    FlickAngle.append(value)

    # GLOBAL ANGLE
    if value <= 45 or value >= 315:
        FlickT.append("Right")
    elif value <= 135:
        FlickT.append("Up")
    elif value <= 225:
        FlickT.append("Left")
    else:
        FlickT.append("Down")

# SIZE OF FLICK LENGTHS
Count = 0
for i in range(0, len(FlickLength)):

    if FlickLength[i] > 0.7*maxFlickL:
        FlickLT.append("Long")
        Count+=1
    elif FlickLength[i] > 0.4*maxFlickL:
        FlickLT.append("Medium")
        Count += 1
    elif FlickLength[i] > 0.1*maxFlickL:
        FlickLT.append("Short")
        Count += 1
    else:
        FlickLT.append("")

# TOTAL FLICKS
print('Total Flick Like Motions: ' + str(len(FlickLength)))
print('Total Flick Like Motions Valid Size: ' + str(Count))

def normalize_to_fixed_points(data, num_points=20):
    # Original x-coordinates
    original_x = np.linspace(0, 1, len(data))

    # New x-coordinates for 100 points
    new_x = np.linspace(0, 1, num_points)

    # Interpolating the data
    interpolator = interp1d(original_x, data, kind='linear')
    normalized_data = interpolator(new_x)
    return normalized_data


# PLOTTING
fig_Sright = plt.figure(figsize=(12, 25))
fig_Sleft = plt.figure(figsize=(12, 25))
fig_Sup = plt.figure(figsize=(12, 25))
fig_Sdown = plt.figure(figsize=(12, 25))
fig_Mright = plt.figure(figsize=(12, 25))
fig_Mleft = plt.figure(figsize=(12, 25))
fig_Mup = plt.figure(figsize=(12, 25))
fig_Mdown = plt.figure(figsize=(12, 25))
fig_Lright = plt.figure(figsize=(12, 25))
fig_Lleft = plt.figure(figsize=(12, 25))
fig_Lup = plt.figure(figsize=(12, 25))
fig_Ldown = plt.figure(figsize=(12, 25))


def plot_flicks(Overflick, rangea, Slicea, Sliceb, Slicec, Sliced, title_prefix, xlim_T, ylim_D, ylim_V, xlim_P, ylim_P):
    plt.subplot(5, 1, 1)
    plt.plot(rangea, Slicea)
    if Show_Micro_Start == "Y":
        if Overflick == 0:
            plt.plot(MicroT, MicroD, color='black', marker='o', linestyle='none')
        else:
            plt.plot(MicroT, MicroD, color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Distance vs Time')
    plt.xlim(0, xlim_T)
    plt.ylim(0, ylim_D)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (in)')

    plt.subplot(5, 1, 2)
    plt.plot(rangea, Sliceb)
    if Show_Micro_Start == "Y":
        if Overflick == 0:
            plt.plot(MicroT, MicroV, color='black', marker='o', linestyle='none')
        else:
            plt.plot(MicroT, MicroV, color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Velocity vs Time')
    plt.xlim(0, xlim_T)
    plt.ylim(0, ylim_V)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (in/s)')

    plt.subplot(5, 1, 3)
    plt.plot(Slicea, Sliceb)
    if Show_Micro_Start == "Y":
        if Overflick == 0:
            plt.plot(MicroD, MicroV, color='black', marker='o', linestyle='none')
        else:
            plt.plot(MicroD, MicroV, color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Velocity vs Distance')
    plt.xlim(0, ylim_D)
    plt.ylim(0, ylim_V)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Distance (in)')
    plt.ylabel('Velocity (in/s)')

    plt.subplot(5, 1, 4)
    plt.plot(Slicec, Sliced)
    plt.title(f'{title_prefix} Position')
    plt.xlim(xlim_P)
    plt.ylim(ylim_P)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('X (in)')
    plt.ylabel('Y (in)')


AverageVA = np.zeros((13, 20))
AverageDA = np.zeros((13, 20))
Flick_Count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
EffA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
OverflickA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
FlickMissA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Flick_T = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Flick_D = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Flick_V = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Micro_T = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Micro_D = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Micro_V = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Total_T = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Total_D = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Total_V = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Average_T = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
D1 = []
D2 = []
D3 = []
D4 = []
V1 = []
V2 = []
V3 = []
V4 = []
DM = []
VM = []


Count = 0
for i in range(1, len(FlickEnd)):

    # TIME SLICE
    Time_Slice = np.array(T[FlickEnd[i - 1]:FlickEnd[i]])
    Time_Slice = Time_Slice - T[FlickEnd[i - 1]]

    # DISTANCE SLICE
    Distance_Slice = np.array(D[FlickEnd[i - 1]:FlickEnd[i]])
    Distance_Slice = Distance_Slice - D[FlickEnd[i - 1]]

    # VELOCITY SLICE
    Velocity_Slice = V[FlickEnd[i - 1]:FlickEnd[i]]

    # X AND Y COORDINATE SLICE
    X_Position_Slice = np.array(X[FlickEnd[i - 1]:FlickEnd[i]])
    X_Position_Slice = X_Position_Slice - X[FlickEnd[i - 1]]
    Y_Position_Slice = np.array(Y[FlickEnd[i - 1]:FlickEnd[i]])
    Y_Position_Slice = Y_Position_Slice - Y[FlickEnd[i - 1]]

    # CALCULATE FLICK EFFICIENCY
    Actual_D = Distance_Slice[-1]
    Ideal_D = ((X_Position_Slice[-1]) ** 2 + (Y_Position_Slice[-1]) ** 2) ** 0.5
    Effy = Ideal_D / Actual_D

    # ITERATE THROUGH RANGE
    Overflick = 0
    Micro_Start = 0
    MicroT = 0
    MicroD = 0
    MicroV = 0
    for ii in range(1, len(Distance_Slice) - 1):

        # OVERFLICK CHECK
        Current_D = ((X_Position_Slice[ii] - X_Position_Slice[0]) ** 2 + (Y_Position_Slice[ii] - Y_Position_Slice[0]) ** 2) ** 0.5
        if Current_D > Ideal_D + Ideal_D*0.01:
            Overflick = 1

        # START OF MICRO
        if Micro_Start == 0 and Velocity_Slice[ii] <= 20 and Velocity_Slice[ii + 1] <= Velocity_Slice[ii] and Distance_Slice[ii] > Distance_Slice[-1]*.5:

            # ITERATE TO FIND REAL START
            for iii in range(ii, len(Distance_Slice) - 1):

                # IF VELOCITY STARTS GOING UP WE KNOW THE MICRO HAS BEGUN
                if Velocity_Slice[iii + 1] >= Velocity_Slice[iii]:
                    Micro_Start = iii
                    MicroT = Time_Slice[iii]
                    MicroD = Distance_Slice[iii]
                    MicroV = Velocity_Slice[iii]
                    break

    # IF FLICK SEEMS VALID
    if FlickLT[i - 1] != "" and Micro_Start > 0:
        Count += 1

        # CREATE NORMALIZED DATA
        normalized_array1 = np.array(normalize_to_fixed_points(Velocity_Slice[0:Micro_Start]))
        normalized_array1 = normalized_array1 / np.max(normalized_array1)
        normalized_array2 = np.array(normalize_to_fixed_points(Distance_Slice[0:Micro_Start]))
        normalized_array2 = normalized_array2 / np.max(normalized_array2)

        # CALCULATE HOW FAR THE FLICK MISSED? ASSUMES THE MICRO CAUSES A HIT
        Missed_D = ((X_Position_Slice[Micro_Start] - X_Position_Slice[-1]) ** 2 + (Y_Position_Slice[Micro_Start] - Y_Position_Slice[-1]) ** 2) ** 0.5

        if FlickLT[i-1] == "Short" and FlickT[i-1] == "Right":
            plt.figure(fig_Sright)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Short Right Flicks',
                        TimeS, maxFlickL * 0.4, VelocityS, (0, 10), (-10, 10))
            Va = 1

        if FlickLT[i-1] == "Short" and FlickT[i-1] == "Left":
            plt.figure(fig_Sleft)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Short Left Flicks',
                        TimeS, maxFlickL * 0.4, VelocityS, (-10, 0), (-10, 10))
            Va = 2

        if FlickLT[i-1] == "Short" and FlickT[i-1] == "Up":
            plt.figure(fig_Sup)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Short Up Flicks',
                        TimeS, maxFlickL * 0.4, VelocityS, (-10, 10), (0, 10))
            AverageVA += normalized_array1
            Va = 3

        if FlickLT[i-1] == "Short" and FlickT[i-1] == "Down":
            plt.figure(fig_Sdown)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Short Down Flicks',
                        TimeS, maxFlickL * 0.4, VelocityS, (-10, 10), (-10, 0))
            Va = 4

        if FlickLT[i-1] == "Medium" and FlickT[i-1] == "Right":
            plt.figure(fig_Mright)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Medium Right Flicks',
                        TimeM, maxFlickL * 0.7, VelocityM, (0, 15), (-15, 15))
            Va = 5

        if FlickLT[i-1] == "Medium" and FlickT[i-1] == "Left":
            plt.figure(fig_Mleft)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Medium Left Flicks',
                        TimeM, maxFlickL * 0.7, VelocityM, (-15, 0), (-15, 15))
            Va = 6

        if FlickLT[i-1] == "Medium" and FlickT[i-1] == "Up":
            plt.figure(fig_Mup)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Medium Up Flicks',
                        TimeM, maxFlickL * 0.7, VelocityM, (-15, 15), (0, 15))
            Va = 7

        if FlickLT[i-1] == "Medium" and FlickT[i-1] == "Down":
            plt.figure(fig_Mdown)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Medium Down Flicks',
                        TimeM, maxFlickL * 0.7, VelocityM, (-15, 15), (-15, 0))
            Va = 8

        if FlickLT[i-1] == "Long" and FlickT[i-1] == "Right":
            plt.figure(fig_Lright)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Long Right Flicks',
                        TimeL, maxFlickL, VelocityL, (0, 25), (-25, 25))
            Va = 9

        if FlickLT[i-1] == "Long" and FlickT[i-1] == "Left":
            plt.figure(fig_Lleft)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Long Left Flicks',
                        TimeL, maxFlickL, VelocityL, (-25, 0), (-25, 25))
            Va = 10

        if FlickLT[i-1] == "Long" and FlickT[i-1] == "Up":
            plt.figure(fig_Lup)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Long Up Flicks',
                        TimeL, maxFlickL, VelocityL, (-25, 25), (0, 25))
            Va = 11

        if FlickLT[i-1] == "Long" and FlickT[i-1] == "Down":
            plt.figure(fig_Ldown)
            plot_flicks(Overflick, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Long Down Flicks',
                        TimeL, maxFlickL, VelocityL, (-25, 25), (-25, 0))
            Va = 12

        # DATA FROM FLICK
        AverageVA[Va][:] += normalized_array1  # Average Flick Velocity
        AverageDA[Va][:] += normalized_array2  # Average Flick Distance
        EffA[Va] += Effy  # Efficiency Fraction
        OverflickA[Va] += Overflick  # Overflick Fraction
        FlickMissA[Va] += Missed_D/Ideal_D   # Missed Fraction

        Flick_T[Va] += Time_Slice[Micro_Start + 1] - Time_Slice[1]
        Flick_D[Va] += Distance_Slice[Micro_Start + 1] - Distance_Slice[1]
        Flick_V[Va] += Flick_D[Va]/Flick_T[Va]

        if Va in [1, 5, 9]:
            D1.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V1.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va in [2, 6, 10]:
            D2.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V2.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va in [3, 7, 11]:
            D3.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V3.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va in [4, 8, 12]:
            D4.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V4.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))


        Micro_T[Va] += Time_Slice[-1] - Time_Slice[Micro_Start]
        Micro_D[Va] += Distance_Slice[-1] - Distance_Slice[Micro_Start]
        Micro_V[Va] += Micro_D[Va]/Micro_T[Va]

        DM.append(Distance_Slice[-1] - Distance_Slice[Micro_Start])
        VM.append((Distance_Slice[-1] - Distance_Slice[Micro_Start])/(Time_Slice[-1] - Time_Slice[Micro_Start]))

        Total_T[Va] += Time_Slice[-1] - Time_Slice[1]
        Total_D[Va] += Distance_Slice[-1] - Distance_Slice[1]
        Total_V[Va] += Total_D[Va]/Total_T[Va]

        Flick_Count[Va] += 1

        Average_T[1] += 1
        Average_T[2] += Effy
        Average_T[3] += Overflick
        Average_T[4] += Missed_D/Ideal_D

        Average_T[5] += Time_Slice[Micro_Start + 1] - Time_Slice[1]
        Average_T[6] += Distance_Slice[Micro_Start + 1] - Distance_Slice[1]
        Average_T[7] += Flick_D[Va]/Flick_T[Va]

        Average_T[8] += Time_Slice[-1] - Time_Slice[Micro_Start]
        Average_T[9] += Distance_Slice[-1] - Distance_Slice[Micro_Start]
        Average_T[10] += Micro_D[Va]/Micro_T[Va]

        Average_T[11] += Time_Slice[-1] - Time_Slice[1]
        Average_T[12] += Distance_Slice[-1] - Distance_Slice[1]
        Average_T[13] += Total_D[Va]/Total_T[Va]

print('Total Valid Flicks: ' + str(Count))

# ADD IN AVERAGE PLOT AND CREATE FIGURES
figuresA = [
    (fig_Sright, 'Short Right Flicks', AverageDA[1][:], AverageVA[1][:]),
    (fig_Sleft, 'Short Left Flicks', AverageDA[2][:], AverageVA[2][:]),
    (fig_Sup, 'Short Up Flicks', AverageDA[3][:], AverageVA[3][:]),
    (fig_Sdown, 'Short Down Flicks', AverageDA[4][:], AverageVA[4][:]),
    (fig_Mright, 'Medium Right Flicks', AverageDA[5][:], AverageVA[5][:]),
    (fig_Mleft, 'Medium Left Flicks', AverageDA[6][:], AverageVA[6][:]),
    (fig_Mup, 'Medium Upper Flicks', AverageDA[7][:], AverageVA[7][:]),
    (fig_Mdown, 'Medium Down Flicks', AverageDA[8][:], AverageVA[8][:]),
    (fig_Lright, 'Long Right Flicks', AverageDA[9][:], AverageVA[9][:]),
    (fig_Lleft, 'Long Left Flicks', AverageDA[10][:], AverageVA[10][:]),
    (fig_Lup, 'Long Up Flicks', AverageDA[11][:], AverageVA[11][:]),
    (fig_Ldown, 'Long Down Flicks', AverageDA[12][:], AverageVA[12][:]),
]

# ITERATE THROUGH FIGURES
Count=0
for fig, title, data1, data2 in figuresA:
    Count += 1
    plt.figure(fig)
    plt.subplot(5, 1, 5)
    if Flick_Count[Count] > 0:
        plt.plot(data1 / Flick_Count[Count], data2 / Flick_Count[Count], color='black')
    plt.title(f"{Test_Name} Average Profile for {title}")
    plt.xlim(0, None)
    plt.ylim(0, None)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Distance (Scaled)')
    plt.ylabel('Velocity (Scaled)')

    fig.savefig(f"{Test_Name} {title}.png")  # Save figure to file

# ADDITIONAL PLOTTING
fig_F = plt.figure(figsize=(100, 5))
plt.figure(fig_F)
plt.plot(T, V, color='black')
plt.plot(T_F, np.zeros_like(T_F), color='blue', marker='*', linestyle='none')
plt.title('Velocity vs Time')
plt.xlim(0, None)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (in/s)')
fig_F.savefig(Test_Name + " Velocity vs Time.png")

fig_G = plt.figure(figsize=(100, 5))
plt.figure(fig_G)
plt.plot(D, V, color='black')
plt.plot(D_F, np.zeros_like(D_F), color='blue', marker='*', linestyle='none')
plt.title('Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.grid(True, linestyle='--', color='gray', alpha=0.6)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')
fig_G.savefig(Test_Name + " Velocity vs Distance.png")

fig_H = plt.figure(figsize=(12, 31))
plt.subplot(5, 1, 1)
plt.plot(D1, V1, color='black', marker='*', linestyle='none')
slope, intercept = np.polyfit(np.array(D1), np.array(V1), 1)
y_trend = slope * np.array(D1) + intercept
plt.plot(D1, y_trend, color="red", label=f"Trend Line: y = {slope:.2f}x + {intercept:.2f}")
plt.legend()
plt.title('Right Flick Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')

plt.subplot(5, 1, 2)
plt.plot(D2, V2, color='black', marker='*', linestyle='none')
slope, intercept = np.polyfit(np.array(D2), np.array(V2), 1)
y_trend = slope * np.array(D2) + intercept
plt.plot(D2, y_trend, color="red", label=f"Trend Line: y = {slope:.2f}x + {intercept:.2f}")
plt.legend()
plt.title('Left Flick Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')

plt.subplot(5, 1, 3)
plt.plot(D3, V3, color='black', marker='*', linestyle='none')
slope, intercept = np.polyfit(np.array(D3), np.array(V3), 1)
y_trend = slope * np.array(D3) + intercept
plt.plot(D3, y_trend, color="red", label=f"Trend Line: y = {slope:.2f}x + {intercept:.2f}")
plt.legend()
plt.title('Up Flick Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')

plt.subplot(5, 1, 4)
plt.plot(D4, V4, color='black', marker='*', linestyle='none')
slope, intercept = np.polyfit(np.array(D4), np.array(V4), 1)
y_trend = slope * np.array(D4) + intercept
plt.plot(D4, y_trend, color="red", label=f"Trend Line: y = {slope:.2f}x + {intercept:.2f}")
plt.legend()
plt.title('Down Flick Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')

plt.subplot(5, 1, 5)
plt.plot(DM, VM, color='black', marker='*', linestyle='none')
slope, intercept = np.polyfit(np.array(DM), np.array(VM), 1)
y_trend = slope * np.array(DM) + intercept
plt.plot(DM, y_trend, color="red", label=f"Trend Line: y = {slope:.2f}x + {intercept:.2f}")
plt.legend()
plt.title('Micro Velocity vs Distance')
plt.xlim(0, None)
plt.ylim(0, None)
plt.xlabel('Distance (in)')
plt.ylabel('Velocity (in/s)')
fig_H.savefig(Test_Name + " Flick Velocity vs Distance.png")

# RESULT PROCESSING AND PRINTING TO EXCEL FILE
header = ['Direction', 'Count', 'Average Efficiency', 'Overflick Fraction', 'Average Initial Flick Miss Distance Fraction', 'Flick T (s)', 'Flick D (in)', 'Flick V (in/s)', 'Micro T (s)', 'Micro D (in)', 'Micro V (in/s)', 'Total T (s)', 'Total D (in)', 'Total V (in/s)']
direction = ['', 'Short Right', 'Short Left', 'Short Up', 'Short Down', 'Medium Right', 'Medium Left', 'Medium Up', 'Medium Down', 'Long Right', 'Long Left', 'Long Up', 'Long Down']
rows = []
for i in range(1, 13):  # Append data to rows
    if Flick_Count[i] > 0:
        rows.append([direction[i], Flick_Count[i], round(EffA[i] / Flick_Count[i], 3), round(OverflickA[i] / Flick_Count[i], 3), round(FlickMissA[i] / Flick_Count[i], 3),
                     round(Flick_T[i] / Flick_Count[i], 3), round(Flick_D[i] / Flick_Count[i], 3), round(Flick_V[i] / Flick_Count[i], 3),
                     round(Micro_T[i] / Flick_Count[i], 3), round(Micro_D[i] / Flick_Count[i], 3), round(Micro_V[i] / Flick_Count[i], 3),
                     round(Total_T[i] / Flick_Count[i], 3), round(Total_D[i] / Flick_Count[i], 3), round(Total_V[i] / Flick_Count[i], 3)])

rows.append(['Total', Average_T[1], round(Average_T[2] / Average_T[1], 3), round(Average_T[3] / Average_T[1], 3), round(Average_T[4] / Average_T[1], 3),
                     round(Average_T[5] / Average_T[1], 3), round(Average_T[6] / Average_T[1], 3), round(Average_T[7] / Average_T[1], 3),
                     round(Average_T[8] / Average_T[1], 3), round(Average_T[9] / Average_T[1], 3), round(Average_T[10] / Average_T[1], 3),
                     round(Average_T[11] / Average_T[1], 3), round(Average_T[12] / Average_T[1], 3), round(Average_T[13] / Average_T[1], 3)])

with open(Test_Name + ' Data.csv', 'w', newline='') as file:  # Write the header and data to the CSV file
    writer = csv.writer(file)
    writer.writerow(header)  # Writing the header
    writer.writerows(rows)   # Writing the rows

# with open(Test_Name + ' Data.csv', 'w', newline='') as csvfile:
#    csvwriter = csv.writer(csvfile)
#    csvwriter.writerow(["T (sec)", "X (in)", "Y (in)", "D (in)", "V (in/s)"])
#    for i in range(0, len(T)):
#        csvwriter.writerow([T[i], X[i], Y[i], D[i], V[i]])

