# graphFull.py
# Queries the SQLite Database to fully graph the TC data for post-test analysis
# Uses flask to embed the dashboard onto an example webpage


from bokeh.embed import server_document
from bokeh.plotting import figure, curdoc, output_file, save
from bokeh.models import ColumnDataSource, TextInput, DataTable, TableColumn, Checkbox, BoxAnnotation
from bokeh.layouts import column, row
from bokeh.models.widgets import Div, Button
import numpy as np
import sqlite3
import utils as ut
import csv
from flask import Flask, render_template
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from threading import Thread
from datetime import datetime
import signal
import os

# Set from Flask Fetch - See app route
TEST_ID = "1"
TABLE_NAME_TC = "temperature_table_" + TEST_ID
TABLE_NAME_PARAM = "test_settings_" + TEST_ID

# Set from Database Query into Table / user input
OPAMP_FREQUENCY = 0.000797  # 1/OpAmp Period, .002 for csv

# Set from Database Query, Constants
DENSITY = 1
SPECIFIC_HEAT = 1
L = 26  # Distance between thermocouples, in mm

# Constant
TC_TIME_SHIFT = 0.68  # Time difference between TCs (.68)
SAMPLING_RATE = 0.3959535  # amount of time between points, .01 for csv (maybe changed, must reinvestigate)
DATABASE_NAME = 'server/angstronomers.sqlite3'
TEST_DIR_TABLE_NAME = "test_directory"
FIT_MY_DATA = True

app = Flask(__name__)


def modify_doc(doc):
    # Create plot for full data
    source = ColumnDataSource(data={'times1': [], 'times2': [],
                                    'temps1': [], 'temps2': []})
    plot = figure(title='Full Data', width=600, height=350)
    plot.line('times1', 'temps1', source=source, line_color='blue', legend_label='TC1')
    plot.line('times2', 'temps2', source=source, line_color='red', legend_label='TC2')
    sel_bound = BoxAnnotation(fill_alpha = 0)
    plot.add_layout(sel_bound)
    plot.legend.location = "top_left"

    # Create plot for fit data in bounds
    source2 = ColumnDataSource(data={'times1': [], 'times2': [],
                                     'temps1': [], 'temps2': [],
                                     'temps1fit': [], 'temps2fit': []})
    plot2 = figure(title='Fitted Data in Range', width=600, height=350)
    plot2.line('times1', 'temps1', source=source2, line_color='blue', legend_label='TC1')
    plot2.line('times1', 'temps1fit', source=source2, line_color='green', legend_label='TC1FIT')
    plot2.line('times2', 'temps2', source=source2, line_color='red', legend_label='TC2')
    plot2.line('times2', 'temps2fit', source=source2, line_color='brown', legend_label='TC2FIT')
    plot2.legend.location = "top_left"

    # Create text to display Diffusivity, Conductivity, R^2 Values
    textL = Div(text="Length (mm): ", width=150, height=50)
    textDT = Div(text="Delta Time: ", width=150, height=50)
    textM = Div(text="M: ", width=150, height=50)
    textN = Div(text="N: ", width=150, height=50)
    textD = Div(text="Diffusivity (mm^2/s): ", width=150, height=50)
    textC = Div(text="Conductivity (W/mK): ", width=150, height=50)
    textR1 = Div(text="TC1 R^2: ", width=150, height=50)
    textR2 = Div(text="TC2 R^2: ", width=150, height=50)

    # Create table to display changing test parameters
    dataP = dict(
        timestamp=[],
        relTime=[],
        frq=[]
    )
    sourceP = ColumnDataSource(data=dataP)
    columns = [
        TableColumn(field='timestamp', title='Timestamp'),
        TableColumn(field='relTime', title='Graphed Time'),
        TableColumn(field='frq', title='Frequency')
    ]
    param_table = DataTable(source=sourceP, columns=columns, width=400, height=500)

    # Connect to the database, create a cursor
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Get TC Data
    cursor.execute(f'''SELECT relTime, temp1, temp2
                      FROM {TABLE_NAME_TC}
                      ORDER BY relTime ASC''')
    results = cursor.fetchall()
    
    # Get First Frequency Used
    cursor.execute(f'''SELECT frequency
                       FROM {TABLE_NAME_PARAM}
                       ORDER BY datetime ASC
                       LIMIT 1''')
    resultsF1 = cursor.fetchall()
    if resultsF1:
        sourceP.data['frq'] = [resultsF1[0][0]]
        sourceP.data['timestamp'] = ["0"]
        sourceP.data['relTime'] = ["0"]

    # Get Parameters Data - Timing + Frequency
    cursor.execute(f'''SELECT {TABLE_NAME_TC}.relTime,
                              {TABLE_NAME_PARAM}.datetime,
                              {TABLE_NAME_PARAM}.frequency
                       FROM {TABLE_NAME_PARAM}
                       JOIN {TABLE_NAME_TC} ON strftime('%Y-%m-%d %H:%M:%S', {TABLE_NAME_TC}.datetime) 
                                             = strftime('%Y-%m-%d %H:%M:%S', {TABLE_NAME_PARAM}.datetime)
                       GROUP BY {TABLE_NAME_PARAM}.datetime''')
    resultsP = cursor.fetchall()
    if resultsP:
        relTime, timestamp, frq = zip(*resultsP)
        sourceP.data['relTime'] += list(relTime)
        sourceP.data['timestamp'] += list(timestamp)
        sourceP.data['frq'] += list(frq)

    # Get Parameters Data - Constants TODO check if works
    cursor.execute(f'''SELECT density, specificHeatCapacity, tcDistance
                       FROM {TEST_DIR_TABLE_NAME}
                       WHERE testId = {TEST_ID}
                       LIMIT 1''')
    resultsC = cursor.fetchall()
    DENSITY = resultsC[0][0]
    SPECIFIC_HEAT = resultsC[0][1]
    L = resultsC[0][2]

    # Store results, close cursor
    times1 = [x[0] for x in results]
    temps1 = [x[1] for x in results]
    temps2 = [x[2] for x in results]
    times2 = [x+TC_TIME_SHIFT for x in times1]  # Fix timing for temps2

    cursor.close()
    conn.close()
    
    # Calculate sampling rate
    if len(times1) < 2:
        raise ValueError("List must contain at least two values for calculating differences.")
    # Calculate the sum of differences
    diff_sum = sum(abs(times1[i] - times1[i - 1]) for i in range(1, len(times1)))
    # Calculate the average difference
    global SAMPLING_RATE
    SAMPLING_RATE = diff_sum / (len(times1) - 1)
    
    source.data = {'times1': times1, 'times2': times2,
                   'temps1': temps1, 'temps2': temps2}

    def update_plot(attrname, old, new):
        # exceptions for boundary inputs
        try:
            lower_bound = float(lb_input.value)
        except ValueError:
            bound_warn.text = "Lower Bound Invalid Input"
            print("Invalid input. Please enter a number.")
            return
        try:
            upper_bound = float(ub_input.value)
        except ValueError:
            bound_warn.text = "Upper Bound Invalid Input"
            print("Invalid input. Please enter a number.")
            return
        if lower_bound >= upper_bound:
            bound_warn.text = "Lower bound must be smaller than upper"
            print("Lower Bound must be smaller.")
            return
        if upper_bound > len(times1):
            bound_warn.text = f"Upper bound is too high"
            print("Upper Bound too high.")
            return
            
        #Figure out which frequncy value to use based on user input
        relT = [float(i) for i in sourceP.data["relTime"]]
        freq_ops = [float(i) for i in sourceP.data["frq"]]

        for new_setting_start in relT:
            if new_setting_start>lower_bound and new_setting_start<upper_bound:
                bound_warn.text = "Selected range includes test setting switch"
                print("Range includes a test setting change")
                return
            
        bound_warn.text = "" #If bound is valid, clear the message
        #Find the frequency from the test setting that the selected bound resides in
        min_diff = [10000000000, -1]
        for i , new_setting_start in enumerate(relT):
            if new_setting_start<lower_bound and min_diff[0] > lower_bound-new_setting_start:
                min_diff = [lower_bound-new_setting_start, i]

        using_frequency = float(freq_ops[min_diff[1]])
        freq.text = f"Frequency: {using_frequency} Hz"
        sel_bound.left = lower_bound
        sel_bound.right = upper_bound
        sel_bound.fill_alpha = 0.2
        sel_bound.fill_color = "gray"
        
        global OPAMP_FREQUENCY
        OPAMP_FREQUENCY = using_frequency
        
        if FIT_MY_DATA:
            temps1_pr = ut.process_data(temps1, SAMPLING_RATE, OPAMP_FREQUENCY)
            temps2_pr = ut.process_data(temps2, SAMPLING_RATE, OPAMP_FREQUENCY)
        else:
            temps1_pr = temps1
            temps2_pr = temps2
            
        # return index of value closest to lower or upper bound
        lb_index = min(range(len(times1)), key=lambda i: abs(times1[i] - lower_bound))
        ub_index = min(range(len(times1)), key=lambda i: abs(times1[i] - upper_bound))

        times1_plot = times1[lb_index:ub_index]
        times2_plot = times2[lb_index:ub_index]
        temps1_plot_pr = temps1_pr[lb_index:ub_index]
        temps2_plot_pr = temps2_pr[lb_index:ub_index]

        params1, adjusted_r_squared1 = ut.fit_data(temps1_plot_pr, times1_plot, OPAMP_FREQUENCY)
        params2, adjusted_r_squared2 = ut.fit_data(temps2_plot_pr, times2_plot, OPAMP_FREQUENCY)
        phaseShifts = [params1[2], params2[2]]

        # Continue with the remaining calculations
        M = 2 * params1[1]
        N = 2 * params2[1]
        period = 1 / OPAMP_FREQUENCY

        if M < 0:
            phaseShifts[0] = phaseShifts[0] + period / 2
            M = -M

        if N < 0:
            phaseShifts[1] = phaseShifts[1] + period / 2
            N = -N

        # --- Commented Out ---
        # # Reduce first phase shift to the very first multiple to the right of t=0
        # if phaseShifts[0] > 0:
        #     while phaseShifts[0] > 0:
        #         phaseShifts[0] = phaseShifts[0] - period
        # else:
        #     while phaseShifts[0] < -period:
        #         phaseShifts[0] = phaseShifts[0] + period

        # # Reduce 2nd phase shift to the very first multiple to the right of t=0
        # if phaseShifts[1] > 0:
        #     while phaseShifts[1] > 0:
        #         phaseShifts[1] = phaseShifts[1] - period
        # else:
        #     while phaseShifts[1] < -period:
        #         phaseShifts[1] = phaseShifts[1] + period

        # # Add a phase to ensure 2 is after 1 in time
        # if phaseShifts[1] > phaseShifts[0]:
        #     phaseShifts[1] = phaseShifts[1] - period

        phaseDifference = abs(phaseShifts[1] - phaseShifts[0])  # From wave mechanics -
        # same frequency but different additive constants
        # so the phase difference is just the difference of the individual phase shifts
        phaseDifference = phaseDifference % period
        delta_time = phaseDifference
        
        diffusivity = L ** 2 / (2 * delta_time * np.log(M / N))  # in mm^2/s
        diffusivity_for_calc = diffusivity * 0.000001  # in m^2/s
        density_for_calc = DENSITY * 1000  # in kg/m^3
        # Specific Heat in J/kgC (or Kelvin, its the same)
        conductivity = diffusivity_for_calc * density_for_calc * SPECIFIC_HEAT  # in W/m·K

        a1, b1, c1 = params1
        y_fitted1 = a1 + b1 * np.sin(2 * np.pi * OPAMP_FREQUENCY * (times1_plot + c1))

        a2, b2, c2 = params2
        y_fitted2 = a2 + b2 * np.sin(2 * np.pi * OPAMP_FREQUENCY * (times2_plot + c2))

        # Update the ColumnDataSource data for both lines
        source2.data = {'times1': times1_plot, 'times2': times2_plot,
                        'temps1': temps1_plot_pr, 'temps2': temps2_plot_pr,
                        'temps1fit': y_fitted1, 'temps2fit': y_fitted2}
        textL.text = f"L: {L}"
        textDT.text = f"Delta Time: {delta_time}"
        textM.text = f"M: {M}"
        textN.text = f"N: {N}"
        textD.text = f"Diffusivity (mm^2/s): {diffusivity}"
        textC.text = f"Conductivity (W/mK): {conductivity}"
        textR1.text = f"TC1 R^2: {adjusted_r_squared1}"
        textR2.text = f"TC1 R^2: {adjusted_r_squared2}"

    # Create input fields for upper and lower bounds
    lb_input = TextInput(value="1000", title="Enter Lower Bound:")
    ub_input = TextInput(value="2000", title="Enter Upper Bound")
    lb_input.on_change("value", update_plot)
    ub_input.on_change("value", update_plot)

    #Create field for valid input of lower and upper bound
    bound_warn = Div(text="", styles={'color': 'red'})
    freq = Div(text="",styles={'color': 'black'})
    
    # Create input field for frequency
    # frq_input = TextInput(value=".005", title="Enter Frequency (Hz):")
    # frq_input.on_change("value", update_plot)
    
    def save_to_csv():
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        #fetch all data from the TC table - TODO Save other tables
        cursor.execute(f"SELECT * FROM {TABLE_NAME_TC}")
        rows = cursor.fetchall()
        # Define the CSV file path
        csv_file_path_TC = 'TC_DATA_' + TEST_ID + str(datetime.now()) + '.csv'
        # Write the data to a CSV file
        with open(csv_file_path_TC, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            header = [description[0] for description in cursor.description]
            csv_writer.writerow(header)
            # Write the rows
            csv_writer.writerows(rows)

        print(f"Data exported to {csv_file_path_TC}")
        cursor.close()
        conn.close()
        
    # Create save button
    save_button = Button(label='Save to CSV', button_type='success')
    save_button.on_click(save_to_csv)
    
    # switch graphing modes
    def switch_fitting_graph(attr, old_value, new_value):
        global FIT_MY_DATA
        FIT_MY_DATA = not FIT_MY_DATA
    
    checkbox = Checkbox(label="Remove Rolling Average", active=FIT_MY_DATA)
    checkbox.on_change('active', switch_fitting_graph)
    checkbox.on_change('active', update_plot)
    
    doc.add_root(row(column(checkbox, param_table),
                     column(plot, plot2),
                     column(save_button, lb_input, ub_input, bound_warn, freq,
                            textL, textDT, textM, textN,
                            textD, textC, textR1, textR2)))


@app.route('/<test_id>', methods=['GET'])
def bkapp_page(test_id):
    global TEST_ID, TABLE_NAME_PARAM, TABLE_NAME_TC
    if test_id != "favicon.ico":
        TEST_ID = test_id
        TABLE_NAME_TC = "temperature_table_" + TEST_ID
        TABLE_NAME_PARAM = "test_settings_" + TEST_ID
    script = server_document('http://localhost:5006/bkapp')
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(),
                    allow_websocket_origin=["localhost:8124", "127.0.0.1:8124"])
    server.start()
    server.io_loop.start()

Thread(target=bk_worker).start()

def gracefulExit(*args):
    """force the script to close because I think bokeh/flask changes normal exit behavior
    """
    print("Entered Graceful Exit")
    os._exit(1)


if __name__ == '__main__':
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        signal.signal(s, gracefulExit)

    app.run(port=8124)
