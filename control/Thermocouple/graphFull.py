# graphFull.py
# Queries the SQLite Database to fully graph the TC data for post-test analysis
# Uses flask to embed the dashboard onto an example webpage


from bokeh.embed import server_document
from bokeh.plotting import figure, curdoc, output_file, save
from bokeh.models import ColumnDataSource, TextInput, DataTable, TableColumn
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

# Set from Flask Fetch - See app route
TEST_ID = "1"
TABLE_NAME_TC = "temperature_table_" + TEST_ID
TABLE_NAME_PARAM = "test_settings_" + TEST_ID

# Set from Database Query into Table / user input
OPAMP_FREQUENCY = .002  # 1/OpAmp Period, .002 for csv

# Set from Database Query, Constants
DENSITY = 1
SPECIFIC_HEAT = 1
L = .72  # Distance between thermocouples

# Constant
TC_TIME_SHIFT = 0.68  # Time difference between TCs (.68)
SAMPLING_RATE = 1 / 0.01  # 1/.01 for csv, 1/0.316745311 for daq (can safely be inaccurate)
DATABASE_NAME = 'server/angstronomers.sqlite3'
TEST_DIR_TABLE_NAME = "test_directory"

app = Flask(__name__)


def modify_doc(doc):
    # Create plot for full data
    source = ColumnDataSource(data={'times1': [], 'times2': [],
                                    'temps1': [], 'temps2': []})
    plot = figure(title='Full Data', width=600, height=350)
    plot.line('times1', 'temps1', source=source, line_color='blue', legend_label='TC1')
    plot.line('times2', 'temps2', source=source, line_color='red', legend_label='TC2')

    # Create plot for fit data in bounds
    source2 = ColumnDataSource(data={'times1': [], 'times2': [],
                                     'temps1': [], 'temps2': [],
                                     'temps1fit': [], 'temps2fit': []})
    plot2 = figure(title='Fitted Data in Range', width=600, height=350)
    plot2.line('times1', 'temps1', source=source2, line_color='blue', legend_label='TC1')
    plot2.line('times1', 'temps1fit', source=source2, line_color='green', legend_label='TC1FIT')
    plot2.line('times2', 'temps2', source=source2, line_color='red', legend_label='TC2')
    plot2.line('times2', 'temps2fit', source=source2, line_color='brown', legend_label='TC2FIT')

    # Create text to display Diffusivity, Conductivity, R^2 Values
    textL = Div(text="Length: ", width=150, height=50)
    textDT = Div(text="Delta Time: ", width=150, height=50)
    textM = Div(text="M: ", width=150, height=50)
    textN = Div(text="N: ", width=150, height=50)
    textD = Div(text="Diffusivity: ", width=150, height=50)
    textC = Div(text="Conductivity: ", width=150, height=50)
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
    param_table = DataTable(source=sourceP, columns=columns, width=400, height=280)

    # Connect to the database, create a cursor
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Get TC Data
    cursor.execute(f'''SELECT relTime, temp1, temp2
                      FROM {TABLE_NAME_TC}
                      ORDER BY relTime ASC''')
    results = cursor.fetchall()

    # Get Parameters Data - Timing + Frequency
    cursor.execute(f'''SELECT {TABLE_NAME_TC}.relTime,
                              {TABLE_NAME_PARAM}.datetime,
                              {TABLE_NAME_PARAM}.frequency
                       FROM {TABLE_NAME_PARAM}
                       JOIN {TABLE_NAME_TC} ON {TABLE_NAME_TC}.datetime = {TABLE_NAME_PARAM}.datetime
                       GROUP BY {TABLE_NAME_PARAM}.datetime''')
    resultsP = cursor.fetchall()
    sourceP.data['relTime'] = [x[0] for x in resultsP]
    sourceP.data['timestamp'] = [x[1] for x in resultsP]
    sourceP.data['frq'] = [x[2] for x in resultsP]

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

    # Data pre-processing for noise-reduction, signal smoothing, normalization by removing moving average
    # temps1_pr = ut.process_data(temps1, SAMPLING_RATE, OPAMP_FREQUENCY)
    # temps2_pr = ut.process_data(temps2, SAMPLING_RATE, OPAMP_FREQUENCY)

    # source.data = {'times1': times1, 'times2': times2,
    #                'temps1': temps1_pr, 'temps2': temps2_pr}
    
    source.data = {'times1': times1, 'times2': times2,
                   'temps1': temps1, 'temps2': temps2}

    def update_plot(attrname, old, new):
        # exceptions for boundary inputs
        try:
            lower_bound = float(lb_input.value)
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        try:
            upper_bound = float(ub_input.value)
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        if lower_bound >= upper_bound:
            print("Lower Bound must be smaller.")
            return
        if upper_bound > len(times1):
            print("Upper Bound too high.")
            return

        # return index of value closest to lower or upper bound
        lb_index = min(range(len(times1)), key=lambda i: abs(times1[i] - lower_bound))
        ub_index = min(range(len(times1)), key=lambda i: abs(times1[i] - upper_bound))

        times1_plot = times1[lb_index:ub_index]
        times2_plot = times2[lb_index:ub_index]
        temps1_plot = temps1[lb_index:ub_index]
        temps2_plot = temps2[lb_index:ub_index]
        
        # exception for frequency input
        try:
            using_frequency = float(frq_input.value)
        except ValueError:
            print("Invalid frequency input. Please enter a number.")
            return
        if using_frequency == 0:
            print("Frequency must be a non-zero value")
            return
        
        global OPAMP_FREQUENCY
        OPAMP_FREQUENCY = using_frequency
        
        temps1_plot_pr = ut.process_data(temps1_plot, SAMPLING_RATE, OPAMP_FREQUENCY)
        temps2_plot_pr = ut.process_data(temps2_plot, SAMPLING_RATE, OPAMP_FREQUENCY)

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

            # Reduce first phase shift to the very first multiple to the right of t=0
        if phaseShifts[0] > 0:
            while phaseShifts[0] > 0:
                phaseShifts[0] = phaseShifts[0] - period
        else:
            while phaseShifts[0] < -period:
                phaseShifts[0] = phaseShifts[0] + period

        # Reduce 2nd phase shift to the very first multiple to the right of t=0
        if phaseShifts[1] > 0:
            while phaseShifts[1] > 0:
                phaseShifts[1] = phaseShifts[1] - period
        else:
            while phaseShifts[1] < -period:
                phaseShifts[1] = phaseShifts[1] + period

        # Add a phase to ensure 2 is after 1 in time
        if phaseShifts[1] > phaseShifts[0]:
            phaseShifts[1] = phaseShifts[1] - period

        phaseDifference = abs(phaseShifts[1] - phaseShifts[0])  # From wave mechanics -
        # same frequency but different additive constants
        # so the phase difference is just the difference of the individual phase shifts
        phaseDifference = phaseDifference % period
        delta_time = phaseDifference

        diffusivity = L ** 2 / (2 * delta_time * np.log(M / N))
        conductivity = diffusivity * DENSITY * SPECIFIC_HEAT

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
        textD.text = f"Diffusivity: {diffusivity}"
        textC.text = f"Conductivity: {conductivity}"
        textR1.text = f"TC1 R^2: {adjusted_r_squared1}"
        textR2.text = f"TC1 R^2: {adjusted_r_squared2}"

    # Create input fields for upper and lower bounds
    lb_input = TextInput(value="1000.0", title="Enter Lower Bound:")
    ub_input = TextInput(value="2000.0", title="Enter Upper Bound")
    lb_input.on_change("value", update_plot)
    ub_input.on_change("value", update_plot)
    
    # Create input field for frequency
    frq_input = TextInput(value=".01", title="Enter Frequency (Hz):")
    frq_input.on_change("value", update_plot)
    
    def save_to_csv():
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        #fetch all data from the TC table - TODO Save other tables
        cursor.execute(f"SELECT * FROM {TABLE_NAME_TC}")
        rows = cursor.fetchall()
        # Define the CSV file path
        csv_file_path_TC = 'TC_DATA_' + TEST_ID + '.csv'
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

    # doc.add_root(column(row(param_table, plot, column(save_button, lb_input, ub_input, frq_input)),
    #                     row(plot2, column(textL, textDT, textM, textN)),
    #                     row(textD, textC, textR1, textR2)))
    
    doc.add_root(row(param_table,
                     column(plot, plot2),
                     column(save_button, lb_input, ub_input, frq_input,
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

if __name__ == '__main__':
    app.run(port=8124)
