# graphLive.py
# Queries the SQLite Database to graph the TC data for monitoring
# Uses flask to embed the dashboard onto an example webpage


from bokeh.embed import server_document
from bokeh.plotting import figure, curdoc, output_file, save
from bokeh.models import ColumnDataSource
from bokeh.layouts import column, row, layout
from bokeh.models.widgets import Button, Div
import numpy as np
import sqlite3
import utils as ut
from flask import Flask, render_template, request
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from threading import Thread
from multiprocessing import Process

# Set from Flask Fetch - See app route TODO
TEST_ID = "1"
TABLE_NAME_TC = "temperature_table_" + TEST_ID
TABLE_NAME_PARAM = "test_settings_" + TEST_ID

# Changes Live from Database Query
OPAMP_FREQUENCY = .002  # 1/OpAmp Period, .002 for csv
TIMESTAMP_FRQ_CHANGE = '2000-01-01 00:00:00'

# Set from Database Query
DENSITY = 1
SPECIFIC_HEAT = 1
L = .72  # Distance between thermocouples CSV = .72

# Constant
UPDATE_WAIT = 50  # in ms, time between updating plot
TC_TIME_SHIFT = 0.68  # Time difference between TCs (.68)
SAMPLING_RATE = 1 / 0.01  # 1/.01 for csv, 1/0.316745311 for daq (can safely be inaccurate)
PERIODS_TO_VIEW = 2.5  # Determines how many periods of the sine curve will be graphed
MAX_GRAPH_BUFFER = int(PERIODS_TO_VIEW * (1 / OPAMP_FREQUENCY) * SAMPLING_RATE)
DATABASE_NAME = 'server/angstronomers.sqlite3'
TEST_DIR_TABLE_NAME = "test_directory"

app = Flask(__name__)


def modify_doc(doc):
    # Create plot for curve fit data
    source = ColumnDataSource(data={'times1': [], 'times2': [],
                                    'temps1': [], 'temps2': [],
                                    'temps1fit': [], 'temps2fit': []})
    plot = figure(title='Live Plot Fitted', width=500, height=300)
    plot.toolbar.logo = None
    plot.toolbar_location = None
    plot.line('times1', 'temps1', source=source, line_color='blue', legend_label='TC1')
    plot.line('times1', 'temps1fit', source=source, line_color='green', legend_label='TC1FIT')
    plot.line('times2', 'temps2', source=source, line_color='red', legend_label='TC2')
    plot.line('times2', 'temps2fit', source=source, line_color='yellow', legend_label='TC2FIT')
    plot.legend.nrows=2
    plot.legend.label_text_font_size = "6pt"
    plot.legend.location = "bottom_left"

    # Create plot for temp data as read
    source2 = ColumnDataSource(data={'times1': [], 'times2': [],
                                     'temps1': [], 'temps2': []})
    plot2 = figure(title='Live Plot As Recorded', width=500, height=300)
    plot2.toolbar.logo = None
    plot2.toolbar_location = None
    plot2.line('times1', 'temps1', source=source2, line_color='blue', legend_label='TC1')
    plot2.line('times2', 'temps2', source=source2, line_color='red', legend_label='TC2')
    plot2.legend.label_text_font_size = "6pt"
    plot2.legend.location = "bottom_left"

    # Create text to display Diffusivity, Conductivity, R^2 Values
    textD = Div(text="Diffusivity: ", width=200, height=25)
    textC = Div(text="Conductivity: ", width=200, height=25)
    textR1 = Div(text="TC1 R^2: ", width=200, height=25)
    textR2 = Div(text="TC2 R^2: ", width=200, height=25)
    text3 = Div(text="TC3: ", width=130, height=25)
    text4 = Div(text="TC4: ", width=130, height=25)
    text5 = Div(text="TC5: ", width=130, height=25)
    text6 = Div(text="TC6: ", width=130, height=25)
    text7 = Div(text="TC7: ", width=130, height=25)
    text8 = Div(text="TC8: ", width=130, height=25)

    # Connect to the database, create a cursor
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    callback = None

    def update_data():
        # Get Main TC Data
        global TIMESTAMP_FRQ_CHANGE, OPAMP_FREQUENCY, DENSITY, SPECIFIC_HEAT, L
        cursor.execute(f'''SELECT relTime, temp1, temp2
                          FROM {TABLE_NAME_TC}
                          WHERE datetime > ?
                          ORDER BY relTime DESC
                          LIMIT ?''', (TIMESTAMP_FRQ_CHANGE,MAX_GRAPH_BUFFER,))
        results = cursor.fetchall()

        # Get Other TC Data
        cursor.execute(f'''SELECT temp3, temp4, temp5, temp6, temp7, temp8
                          FROM {TABLE_NAME_TC}
                          WHERE temp3 IS NOT NULL
                          ORDER BY relTime DESC
                          LIMIT 1''')
        results2 = cursor.fetchall()
        
        # Get Parameters Data - Timing + Frequency
        cursor.execute(f'''SELECT frequency, datetime
                        FROM {TABLE_NAME_PARAM}
                        ORDER BY datetime DESC
                        LIMIT 1''')
        resultsP = cursor.fetchall()
        new_frq = resultsP[0][0]
        if new_frq != OPAMP_FREQUENCY:
            OPAMP_FREQUENCY = new_frq
            TIMESTAMP_FRQ_CHANGE = resultsP[1][0]

        # Get Parameters Data - Constants TODO check if works
        cursor.execute(f'''SELECT density, specificHeatCapacity, tcDistance
                        FROM {TEST_DIR_TABLE_NAME}
                        WHERE testId = {TEST_ID}
                        LIMIT 1''')
        resultsC = cursor.fetchall()
        print(resultsC)
        DENSITY = resultsC[0][0]
        SPECIFIC_HEAT = resultsC[1][0]
        L = resultsC[2][0]

        # Add data
        times1 = [row[0] for row in results]
        temps1 = [row[1] for row in results]
        temps2 = [row[2] for row in results]

        # Fix timing for temps2
        times2 = [x+TC_TIME_SHIFT for x in times1]

        # Data pre-processing for noise-reduction, signal smoothing, normalization by removing moving average
        temps1_pr = ut.process_data(temps1, SAMPLING_RATE, OPAMP_FREQUENCY)
        temps2_pr = ut.process_data(temps2, SAMPLING_RATE, OPAMP_FREQUENCY)

        params1, adjusted_r_squared1 = ut.fit_data(temps1_pr, times1, OPAMP_FREQUENCY)
        params2, adjusted_r_squared2 = ut.fit_data(temps2_pr, times2, OPAMP_FREQUENCY)
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
        y_fitted1 = a1 + b1 * np.sin(2 * np.pi * OPAMP_FREQUENCY * (times1 + c1))

        a2, b2, c2 = params2
        y_fitted2 = a2 + b2 * np.sin(2 * np.pi * OPAMP_FREQUENCY * (times2 + c2))

        # Update the ColumnDataSource data for both lines
        source.data = {'times1': times1, 'times2': times2,
                       'temps1': temps1_pr, 'temps2': temps2_pr,
                       'temps1fit': y_fitted1, 'temps2fit': y_fitted2}
        source2.data = {'times1': times1, 'times2': times2,
                        'temps1': temps1, 'temps2': temps2}
        textD.text = f"Diffusivity: {round(diffusivity, 6)}"
        textC.text = f"Conductivity: {round(conductivity, 6)}"
        textR1.text = f"TC1 R^2: {round(adjusted_r_squared1, 6)}"
        textR2.text = f"TC2 R^2: {round(adjusted_r_squared2, 6)}"
        if results2:
            text3.text = f"TC3: {round(results2[0][0],3)}"
            text4.text = f"TC4: {round(results2[0][1],3)}"
            text5.text = f"TC5: {round(results2[0][2],3)}"
            text6.text = f"TC6: {round(results2[0][3],3)}"
            text7.text = f"TC7: {round(results2[0][4],3)}"
            text8.text = f"TC8: {round(results2[0][5],3)}"

    # Function to start periodic updates
    def start_updates():
        # Connect to the database, create a cursor
        global cursor, conn, callback
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Add a periodic callback to update the plot
        callback = curdoc().add_periodic_callback(update_data, UPDATE_WAIT)

    # Function to stop periodic updates
    def stop_updates():
        global cursor, conn, callback
        # Close the cursor and the connection
        cursor.close()
        conn.close()
        # Remove the periodic callback to stop updates
        curdoc().remove_periodic_callback(callback)

    # Create start and stop buttons
    start_button = Button(label='Start Updates', button_type='success')
    start_button.on_click(start_updates)

    stop_button = Button(label='Stop Updates', button_type='danger')
    stop_button.on_click(stop_updates)

    doc.add_root(column(row(start_button, stop_button),
                        row(plot, plot2),
                        row(textD, textC, textR1, textR2),
                        row(text3, text4, text5, text6, text7, text8)))



@app.route('/<test_id>', methods=['GET'])
def bkapp_page(test_id):
    global TEST_ID, TABLE_NAME_PARAM, TABLE_NAME_TC
    if test_id == "favicon.ico":
        return
    TEST_ID = test_id
    TABLE_NAME_TC = "temperature_table_" + TEST_ID
    TABLE_NAME_PARAM = "test_settings_" + TEST_ID
    script = server_document('http://localhost:5006/bkapplive/live')
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    server = Server({'/bkapplive/live': modify_doc}, io_loop=IOLoop(),
                    allow_websocket_origin=["localhost:8123", "127.0.0.1:8123"])
    server.start()
    server.io_loop.start()


Thread(target=bk_worker).start()

if __name__ == '__main__':
    app.run(port=8123)
