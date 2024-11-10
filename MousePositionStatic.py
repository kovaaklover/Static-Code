# NOTE ENTER IN INPUTS AND THEN START CODE
# MOVEMENT FOR FIRST 5 SECONDS NOT TRACKED SO SCENARIO CAN BE STARTED

# IMPORTS
import numpy as np
import pyautogui
import datetime
import csv
import matplotlib.pyplot as plt
import math

# INPUTS
Test_Name = 'test 1'
Total_Run_Time = 70  # How Many Seconds Code Runs For
X_Resolution = 1920  # Monitor Pixels in the X
Y_Resolution = 1080  # Monitor Pixels in the Y
MonitorSize = 24.5  # Inches

# FOR BETTER PLOTTING
Time_Max = 1  # MAX TIME ON PLOT
Distance_Max = 20  # MAX DISTANCE ON PLOT
Velocity_Max = 200  # MAX VELOCITY ON PLOT

# TABLE STEP SIZE
Distance_Step = 5

Show_Micro_Start = "N"  # IF YOU WANT TO SEE A POINT ON THE GRAPH WHERE THE MICRO STARTS "Y" or "N"

# STORAGE LISTS DEFINED
T, X, Y, D, P, kF, Px, Py, Ax, Ay, Clicks, FlickEnd = [], [], [], [0], [], [], [], [], [], [], [], []

# INITIALIZE TIME PARAMETERS
Time_Step = 0.01  # SAMPLE RATE (DO NOT CHANGE FROM 0.01)
TimeStart = datetime.datetime.now()
Current_Run_Time = datetime.datetime.now() - TimeStart
Sample_Time = Current_Run_Time

# MONITOR DIMENSION CALCULATIONS
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

# VELOCITY FROM DISTANCE AND TIME
V = np.gradient(D, T)

# ITERATE THROUGH FLICK ARRAY TO DETERMINE IF END OF A FLICK + MICRO
T_F = []
D_F = []
for i in range(0, len(V)):

    # IGNORE ANYTHING BEFORE 5 SECONDS
    if i > 500:

        # IF CONSECUTIVE VELOCITY POINTS BELOW 10 in/s
        if V[i] <= 10 and V[i-1] <= 10 and V[i-2] <= 10 and V[i-3] <= 10:
            Clicks.append("Y")
        else:
            Clicks.append("N")

            # IF FIRST "N" AFTER A NEW FLICK + MICRO ITERATE BACKWARDS TO FIND POINT WHERE VELOCITY INCREASES (REAL END)
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
FlickLength, FlickT, FlickLT = [], [], []
maxFlickL = 0
for i in range(1, len(FlickEnd)):

    # FLICK LENGTH INCH
    FlickLength.append(D[FlickEnd[i]]-D[FlickEnd[i-1]])

    # IF GREATER THAN PRIOR MAX FLICK LENGTH SET NEW MAX
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

    # GLOBAL ANGLE
    if value <= 45 or value >= 315:
        FlickT.append("Right")
    elif value <= 135:
        FlickT.append("Up")
    elif value <= 225:
        FlickT.append("Left")
    else:
        FlickT.append("Down")

# WHAT IS THE SIZE OF THE FLICK
Count = 0
for i in range(0, len(FlickLength)):

    if FlickLength[i] > 0.1*maxFlickL:
        FlickLT.append("Long")
        Count += 1
    else:
        FlickLT.append("")

# TOTAL FLICKS
print('Total Flick Like Motions: ' + str(len(FlickLength)))
print('Total Flick Like Motions Valid Size: ' + str(Count))

# PLOTTING
fig_right = plt.figure(figsize=(12, 25))
fig_left = plt.figure(figsize=(12, 25))
fig_up = plt.figure(figsize=(12, 25))
fig_down = plt.figure(figsize=(12, 25))


def plot_flicks(overflick, micro_start, time_slice, distance_slice, velocity_slice, x_position_slice, y_position_slice, title_prefix, xlim_T, ylim_D, ylim_V, xlim_P, ylim_P):
    plt.subplot(4, 1, 1)
    plt.plot(time_slice, distance_slice)
    if Show_Micro_Start == "Y":
        if overflick == 0:
            plt.plot(time_slice[micro_start], distance_slice[micro_start], color='black', marker='o', linestyle='none')
        else:
            plt.plot(time_slice[micro_start], distance_slice[micro_start], color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Distance vs Time')
    plt.xlim(0, xlim_T)
    plt.ylim(0, ylim_D)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (in)')

    plt.subplot(4, 1, 2)
    plt.plot(time_slice, velocity_slice)
    if Show_Micro_Start == "Y":
        if overflick == 0:
            plt.plot(time_slice[micro_start], velocity_slice[micro_start], color='black', marker='o', linestyle='none')
        else:
            plt.plot(time_slice[micro_start], velocity_slice[micro_start], color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Velocity vs Time')
    plt.xlim(0, xlim_T)
    plt.ylim(0, ylim_V)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (in/s)')

    plt.subplot(4, 1, 3)
    plt.plot(distance_slice, velocity_slice)
    if Show_Micro_Start == "Y":
        if overflick == 0:
            plt.plot(distance_slice[micro_start], velocity_slice[micro_start], color='black', marker='o', linestyle='none')
        else:
            plt.plot(distance_slice[micro_start], velocity_slice[micro_start], color='black', marker='*', linestyle='none')
    plt.title(f'{title_prefix} Velocity vs Distance')
    plt.xlim(0, ylim_D)
    plt.ylim(0, ylim_V)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    plt.xlabel('Distance (in)')
    plt.ylabel('Velocity (in/s)')

    plt.subplot(4, 1, 4)
    plt.plot(x_position_slice, y_position_slice)
    plt.title(f'{title_prefix} Position')
    plt.xlim(xlim_P)
    plt.ylim(ylim_P)
    plt.grid(True, linestyle='--', color='gray', alpha=0.6)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('X (in)')
    plt.ylabel('Y (in)')


Distance_Steps = int(maxFlickL//Distance_Step)+1

Flick_Count = [0] * (Distance_Steps*4 + 1)
EffA = [0] * (Distance_Steps*4 + 1)
OverflickA = [0] * (Distance_Steps*4 + 1)
FlickMissA = [0] * (Distance_Steps*4 + 1)

Flick_T = [0] * (Distance_Steps*4 + 1)
Flick_D = [0] * (Distance_Steps*4 + 1)
Flick_V = [0] * (Distance_Steps*4 + 1)

Micro_T = [0] * (Distance_Steps*4 + 1)
Micro_D = [0] * (Distance_Steps*4 + 1)
Micro_V = [0] * (Distance_Steps*4 + 1)

Total_T = [0] * (Distance_Steps*4 + 1)
Total_D = [0] * (Distance_Steps*4 + 1)
Total_V = [0] * (Distance_Steps*4 + 1)

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
    for ii in range(1, len(Distance_Slice) - 1):

        # OVER FLICK CHECK
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
                    break

    # IF FLICK SEEMS VALID
    if FlickLT[i - 1] != "" and Micro_Start > 0:
        Count += 1

        # CALCULATE HOW FAR THE FLICK MISSED? ASSUMES THE MICRO CAUSES A HIT
        Missed_D = ((X_Position_Slice[Micro_Start] - X_Position_Slice[-1]) ** 2 + (Y_Position_Slice[Micro_Start] - Y_Position_Slice[-1]) ** 2) ** 0.5

        if FlickT[i-1] == "Right":
            plt.figure(fig_right)
            plot_flicks(Overflick, Micro_Start, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Right Flicks',
                        Time_Max, Distance_Max, Velocity_Max, (0, Distance_Max), (-Distance_Max, Distance_Max))
            Va = 1

        if FlickT[i-1] == "Left":
            plt.figure(fig_left)
            plot_flicks(Overflick, Micro_Start, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Left Flicks',
                        Time_Max, Distance_Max, Velocity_Max, (-Distance_Max, 0), (-Distance_Max, Distance_Max))
            Va = 2

        if FlickT[i-1] == "Up":
            plt.figure(fig_up)
            plot_flicks(Overflick, Micro_Start, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Up Flicks',
                        Time_Max, Distance_Max, Velocity_Max, (-Distance_Max, Distance_Max), (0, Distance_Max))
            Va = 3

        if FlickT[i-1] == "Down":
            plt.figure(fig_down)
            plot_flicks(Overflick, Micro_Start, Time_Slice, Distance_Slice, Velocity_Slice, X_Position_Slice, Y_Position_Slice, Test_Name + ' Down Flicks',
                        Time_Max, Distance_Max, Velocity_Max, (-Distance_Max, Distance_Max), (-Distance_Max, 0))
            Va = 4

        # BREAK FLICK VIA IDEAL DISTANCE
        step = 0
        for ii in range(0, round(maxFlickL) + 2, Distance_Step):
            if ii < Ideal_D:
                step = ii/Distance_Step

        Va2 = 0
        Va2 = Va + step*4
        Va2 = int(Va2)

        # DATA FROM FLICK
        EffA[Va2] += Effy  # Efficiency Fraction
        OverflickA[Va2] += Overflick  # Over flick Fraction
        FlickMissA[Va2] += Missed_D/Ideal_D   # Missed Fraction

        Flick_T[Va2] += Time_Slice[Micro_Start + 1] - Time_Slice[1]
        Flick_D[Va2] += Distance_Slice[Micro_Start + 1] - Distance_Slice[1]
        Flick_V[Va2] += Flick_D[Va2]/Flick_T[Va2]

        if Va == 1:
            D1.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V1.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va == 2:
            D2.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V2.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va == 3:
            D3.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V3.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        elif Va == 4:
            D4.append(Distance_Slice[Micro_Start + 1] - Distance_Slice[1])
            V4.append((Distance_Slice[Micro_Start + 1] - Distance_Slice[1])/(Time_Slice[Micro_Start + 1] - Time_Slice[1]))

        Micro_T[Va2] += Time_Slice[-1] - Time_Slice[Micro_Start]
        Micro_D[Va2] += Distance_Slice[-1] - Distance_Slice[Micro_Start]
        Micro_V[Va2] += Micro_D[Va2]/Micro_T[Va2]

        DM.append(Distance_Slice[-1] - Distance_Slice[Micro_Start])
        VM.append((Distance_Slice[-1] - Distance_Slice[Micro_Start])/(Time_Slice[-1] - Time_Slice[Micro_Start]))

        Total_T[Va2] += Time_Slice[-1] - Time_Slice[1]
        Total_D[Va2] += Distance_Slice[-1] - Distance_Slice[1]
        Total_V[Va2] += Total_D[Va2]/Total_T[Va2]

        Flick_Count[Va2] += 1

        Average_T[1] += 1
        Average_T[2] += Effy
        Average_T[3] += Overflick
        Average_T[4] += Missed_D/Ideal_D

        Average_T[5] += Time_Slice[Micro_Start + 1] - Time_Slice[1]
        Average_T[6] += Distance_Slice[Micro_Start + 1] - Distance_Slice[1]
        Average_T[7] += Flick_D[Va2]/Flick_T[Va2]

        Average_T[8] += Time_Slice[-1] - Time_Slice[Micro_Start]
        Average_T[9] += Distance_Slice[-1] - Distance_Slice[Micro_Start]
        Average_T[10] += Micro_D[Va2]/Micro_T[Va2]

        Average_T[11] += Time_Slice[-1] - Time_Slice[1]
        Average_T[12] += Distance_Slice[-1] - Distance_Slice[1]
        Average_T[13] += Total_D[Va2]/Total_T[Va2]

print('Total Valid Flicks: ' + str(Count))

# PRINT FIGURES
figures = [fig_right, fig_left, fig_up, fig_down]
titles = ['Right Flicks', 'Left Flicks', 'Up Flicks', 'Down Flicks']
for fig, title in zip(figures, titles):
    fig.savefig(f"{Test_Name} {title}.png")

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
fig_F.savefig(Test_Name + " Total Velocity vs Time.png")

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
fig_G.savefig(Test_Name + " Total Velocity vs Distance.png")

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
header = ['Distance (in) & Direction ', 'Count', 'Average Efficiency', 'Overflick Fraction', 'Average Initial Flick Miss Distance Fraction', 'Flick T (s)', 'Flick D (in)', 'Flick V (in/s)', 'Micro T (s)', 'Micro D (in)', 'Micro V (in/s)', 'Total T (s)', 'Total D (in)', 'Total V (in/s)']

direction = ['']
for i in range(1, Distance_Steps+1):  # 3 sets of directions (<5, <10, <15)
    for dir in ['Right', 'Left', 'Up', 'Down']:
        direction.append(f"{(i-1)* Distance_Step} to <{i * Distance_Step} {dir}")
rows = []
for i in range(1, Distance_Steps*4+1):  # Append data to rows
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

