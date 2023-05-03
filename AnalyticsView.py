from typing import List

from PyQt6 import QtGui
from PyQt6.QtCharts import QBarSet, QBarSeries, QChart, QBarCategoryAxis, QValueAxis, QStackedBarSeries, \
    QHorizontalStackedBarSeries, QLineSeries, QDateTimeAxis
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget

from src.dao.Analytics import MachineGoodbadDistributionPOD
from src.dao.Machine import MachinePOD
from src.dao.MachineStatus import MachineStateType
from src.io import DpLog
from src.io.BackgroundThreads import DatabaseThread
from src.uic.ui_AnalyticsView import Ui_AnalyticsView


class AnalyticsView(Ui_AnalyticsView, QWidget):
    """

    """
    # signal for frequency analysis
        # state distribution
    query_machine_state_distribution = pyqtSignal(int, int)  # add a signal for gfxView_statetime_machine
    query_machine_goodbad_distribution = pyqtSignal(int, int)  # add a signal for gfxView_goodbadprod_machine
    query_machine_stateavgprod_distribution = pyqtSignal(int, int)  # add a signal for gfxView_avgprod_state_machine
    query_machine_stateavgspeed_distribution = pyqtSignal(int, int)  # add a signal for gfxView_avgprod_state_machine
        # alarm
    query_machine_alarm_count = pyqtSignal(int, int, int)  # add a signal for gfxView_alarm_count_machine
    query_machine_alarm_cleartime = pyqtSignal(int, int, int)  # add a signal for gfxView_alarm_cleartime
    query_machine_alarm_avgclear = pyqtSignal(int, int, int)  # add a signal for gfxView_alarm_avgclear

    # signal for time series analysis
        # time
    query_machine_avgspeed_time = pyqtSignal(int, int, int)  # add a signal for gfxview_avgspeed_time
    query_machine_avgprod_time = pyqtSignal(int, int, int)  # add a signal for gfxview_avgprod_time
        # hour
    query_machine_avgspeed_hour = pyqtSignal(int, int, int)  # add a signal for gfxview_avgspeed_hour
    query_machine_avgprod_hour = pyqtSignal(int, int, int)  # add a signal for gfxview_avgprod_hour
    query_machine_goodbadratio_hour = pyqtSignal(int, int, int)  # add a signal for gfxview_goodbadratio_hour

    query_machine_uptime_hour = pyqtSignal(int, int, int)  # add a signal for gfxview_uptime_hour

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        DpLog.log().debug("Initializing AnalyticsView")
        self.setupUi(self)

        # For drop down machine list
        self._machines: List[MachinePOD] = []  # create a copy of list of MachinePOD
        # Only load machine data once, either immediately or from a signal
        if DatabaseThread().machine_data:
            self._set_machines(DatabaseThread().machine_data)
        else:
            DatabaseThread().machine_receiveData.connect(self._set_machines,
                                                         Qt.ConnectionType.SingleShotConnection)
        self.cmbMachine.currentIndexChanged.connect(self._on_machine_selected_change)  # connect signal

        # onModelInit should run only once, after the model was correctly initialized.
        # This could be before or after this JobView is initialized. The modelInitialized
        # signal should only run once so if we miss that, then we have to call onModelInit
        # manually.
        if DatabaseThread().machine_speed_model_is_initialized():
            self.on_mach_speed_model_init()
        else:
            DatabaseThread().machinespeed_tblmodel.model_is_initialized.connect(self.on_mach_speed_model_init)
            DatabaseThread().analytic_view_enable_general_update(True)

        if DatabaseThread().machine_prod_model_is_initialized():
            self.on_mach_prod_model_init()
        else:
#            DatabaseThread().machineprod_tblmodel.model_is_initialized.connect(self.on_mach_prod_model_init)
            DatabaseThread().analytic_view_enable_general_update(True)

        self.pbLoad.pressed.connect(DatabaseThread().analytic_view_general_update,
                                    Qt.ConnectionType.QueuedConnection)
        self.pbLoad.pressed.connect(self.on_load_pressed)

        # Frequency analysis signal
            # state distribution
        self.query_machine_state_distribution.connect(DatabaseThread().analyticView_get_machines_state_distribution,
                                                      Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_goodbad_distribution.connect(DatabaseThread().analyticView_get_machines_goodbad_distribution,
                                                      Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_stateavgprod_distribution.connect(DatabaseThread().analyticView_get_machines_stateavgprod_distribution,
                                                        Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_stateavgspeed_distribution.connect(DatabaseThread().analyticView_get_machines_stateavgspeed_distribution,
                                                        Qt.ConnectionType.BlockingQueuedConnection)
            # alarm
        self.query_machine_alarm_count.connect(DatabaseThread().analyticView_get_machine_alarm_count,
                                                        Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_alarm_cleartime.connect(DatabaseThread().analyticView_get_machine_alarm_cleartime,
                                               Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_alarm_avgclear.connect(DatabaseThread().analyticView_get_machine_alarm_avgclear,
                                               Qt.ConnectionType.BlockingQueuedConnection)

        # Time Series analysis signal
            # time
        self.query_machine_avgspeed_time.connect(DatabaseThread().analyticView_get_machine_avgspeed_time,
                                                 Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_avgprod_time.connect(DatabaseThread().analyticView_get_machine_avgprod_time,
                                                 Qt.ConnectionType.BlockingQueuedConnection)
            # hour
        self.query_machine_avgspeed_hour.connect(DatabaseThread().analyticView_get_machine_avgspeed_hour,
                                                      Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_avgprod_hour.connect(DatabaseThread().analyticView_get_machine_avgprod_hour,
                                                      Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_goodbadratio_hour.connect(DatabaseThread().analyticView_get_machine_goodbadratio_hour,
                                                      Qt.ConnectionType.BlockingQueuedConnection)
        self.query_machine_uptime_hour.connect(DatabaseThread().analyticView_get_machine_uptime_hour,
                                                      Qt.ConnectionType.BlockingQueuedConnection)

    #  function for machine drop down list
    def _set_machines(self, machines: List[MachinePOD]) -> None:
        """
        Make a record of the machine data to use and add the names to
        the machine selector dropdown
        :param machines: The machines to use
        :return: None
        """
        DpLog.log().debug("Setting machine names / info")
        self._machines = machines
        mach_names = [m.get_machine_name() for m in machines]
        self.cmbMachine.clear()
        self.cmbMachine.addItems(mach_names)

    def _on_machine_selected_change(self, index: int) -> None:
        """
        For now just clear the charts data
        :param index:
        :return:
        """
        DpLog.log().debug("Changing to machine '%s', index %i",
                          self._machines[index].get_machine_name(),
                          index)
        # Frequency Analysis
        self.gfxview_alarm_count_machine.chart().removeAllSeries()
        self.gfxview_alarm_cleartime.chart().removeAllSeries()
        self.gfxview_avgclear.chart().removeAllSeries()


        # Time Series Analysis
            # time
        self.gfxview_avgspeed_time.chart().removeAllSeries()
        self.gfxview_avgprod_time.chart().removeAllSeries()

            # hour
        self.gfxview_avgspeed_hour.chart().removeAllSeries()
        self.gfxview_avgprod_hour.chart().removeAllSeries()
        self.gfxview_goodbadratio_hour.chart().removeAllSeries()

        self.gfxview_uptime_hour.chart().removeAllSeries()





    # page 1, machine speed and production table
    def on_mach_speed_model_init(self):
        DpLog.log().debug("Initializing MachineSpeedTableModel...")
        self.tblvMachineSpeed.setModel(DatabaseThread().machinespeed_tblmodel)
    def on_mach_prod_model_init(self):
        DpLog.log().debug("Initializing MachineProdTableModel...")
        self.tblvMachineProd.setModel(DatabaseThread().machineprod_tblmodel)

    # for press button
    def on_load_pressed(self):
    # Frequency Analysis
        # state
        self.initialize_test_bar_chart()
        self.initialize_goodbad_distribution_bar_chart()
        self.initialize_stateavgprod_bar_chart()
        self.initialize_stateavgspeed_bar_chart()
        # alarm
        self.initialize_machinealarmcount_bar_chart()
        self.initialize_machinealarmcleartime_bar_chart()
        self.initialize_machinealarmavgclear_bar_chart()

    # Time Series Analysis
        # time
        self.initialize_machineavgspeed_time_line_chart()
        self.initialize_machineavgprod_time_line_chart()

        # hour
        self.initialize_machineavgspeed_hour_line_chart()
        self.initialize_machineavgprod_hour_line_chart()
        self.initialize_machinegoodbadratio_hour_line_chart()

        self.initialize_machineuptime_hour_bar_chart()

# Frequency Analysis
    # state

    # page 2 test bar chart (machine state time distribution)
    def initialize_test_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()

        self.query_machine_state_distribution.emit(t_start, t_end)
        data = DatabaseThread().analyticView_machine_state_distribution
        DpLog.log().debug("Got %i machines of data", len(data))
        for d in data:
            DpLog.log().debug("Got state data for machine %i: %s", d.mach_id, str(d.states))

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        for s in MachineStateType:  # loop all instances in enum MachineStateType
            bs = QBarSet(s.name)  # create a variable to get the state name
            for machine in data:  # loop machine in dataset 'data'
                bs.append(machine.states[s])  # add time data to bs
            bar_sets.append(bs)  # add bs to bar_set instance

        test_chart = QChart()  # create an instance for class QChart
        test_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        test_chart.setTitle("Total time for each state per machine")
        test_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_statetime_machine.setChart(test_chart)

        # x axis
        bar_categories = []
        for machine in data:
            bar_categories.append(machine.mach_name)

        test_axisX = QBarCategoryAxis()
        test_axisX.append(bar_categories)

        # Set rotation so we can fit many x-axis labels nicely
        test_axisX.setLabelsAngle(90)
        test_axisX.setTruncateLabels(False)

        test_chart.addAxis(test_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(test_axisX)
        # y axis
        test_axisY = QValueAxis()
        # test_axisY.setRange(0,200000)
        test_chart.addAxis(test_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(test_axisY)

    # page 2 machine good/bad distribution bar chart
    def initialize_goodbad_distribution_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()

        self.query_machine_goodbad_distribution.emit(t_start, t_end)
        data = DatabaseThread().analyticView_machine_goodbad_distribution
        DpLog.log().debug("Got %i machines of data", len(data))
        #for d in data:
        #    DpLog.log().debug("Got machine good/bad production data for machine %i: good %s, bad %s", d.mach_id, str(d.mach_goodprod), str(d.mach_badprod))

        # draw chart
        bar_sets = QHorizontalStackedBarSeries()  # crate an instance for QBarSeries class
        bs1 = QBarSet("good production")  # create a variable to get the state name
        bs2 = QBarSet("bad production")  # create a variable to get the state name
        for machine in data:  # loop machine in dataset 'data'
            bs1.append(machine.mach_goodprod)  # add time data to bs
            bs2.append(machine.mach_badprod)  # add time data to bs
        bar_sets.append(bs1)  # add bs to bar_set instance
        bar_sets.append(bs2)


        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("good/bad production for each state per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_goodbadprod_machine.setChart(bar_chart)

        # y axis
        bar_categories = []
        for machine in data:
            bar_categories.append(machine.mach_name)

        bar_axisY = QBarCategoryAxis()
        bar_axisY.append(bar_categories)

        # Set rotation so we can fit many Y-axis labels nicely
        bar_axisY.setLabelsAngle(0)
        bar_axisY.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisY.setLabelsFont(font)

        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

        # X axis
        bar_axisX = QValueAxis()
        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

    # page 2 machine average production per state distribution
    def initialize_stateavgprod_bar_chart(self) -> None:
        """
        Initializes the stateavgprod bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()

        self.query_machine_stateavgprod_distribution.emit(t_start, t_end)
        data = DatabaseThread().analyticView_machine_stateavgprod_distribution
        DpLog.log().debug("Got %i machines of data", len(data))
        #for d in data:
        #    DpLog.log().debug("Got average production per state data for machine %i: %s", d.mach_id, str(d.states))

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        for s in MachineStateType:  # loop all instances in enum MachineStateType
            bs = QBarSet(s.name)  # create a variable to get the state name
            for machine in data:  # loop machine in dataset 'data'
                bs.append(machine.states[s])  # add time data to bs
            bar_sets.append(bs)  # add bs to bar_set instance

        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("Average Production for each state per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_avgprod_state_machine.setChart(bar_chart)

        # x axis
        bar_categories = []
        for machine in data:
            bar_categories.append(machine.mach_name)

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many x-axis labels nicely
        bar_axisX.setLabelsAngle(90)
        bar_axisX.setTruncateLabels(False)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)
        # y axis
        bar_axisY = QValueAxis()
        # test_axisY.setRange(0,200000)
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)


    # page 2 machine average speed per state distribution
    def initialize_stateavgspeed_bar_chart(self) -> None:
        """
        Initializes the stateavgspeed bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()

        self.query_machine_stateavgspeed_distribution.emit(t_start, t_end)
        data = DatabaseThread().analyticView_machine_stateavgspeed_distribution
        DpLog.log().debug("Got %i machines of data", len(data))
        #for d in data:
        #    DpLog.log().debug("Got average speed per state data for machine %i: %s", d.mach_id, str(d.states))

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        for s in MachineStateType:  # loop all instances in enum MachineStateType
            bs = QBarSet(s.name)  # create a variable to get the state name
            for machine in data:  # loop machine in dataset 'data'
                bs.append(machine.states[s])  # add time data to bs
            bar_sets.append(bs)  # add bs to bar_set instance

        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("Average Speed for each state per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_avgspeed_state_machine.setChart(bar_chart)

        # x axis
        bar_categories = []
        for machine in data:
            bar_categories.append(machine.mach_name)

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many x-axis labels nicely
        bar_axisX.setLabelsAngle(90)
        bar_axisX.setTruncateLabels(False)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)
        # y axis
        bar_axisY = QValueAxis()
        # test_axisY.setRange(0,200000)
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

    # alarm

    # page 2 count of each alarm type per machine
    def initialize_machinealarmcount_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_alarm_count.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_alarm_count


        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("alarm count")
        bar_categories = []
        for at,count in data.alarm_counts.items():
            #DpLog.log().debug("Got count of each alarm type per machine %i: alarm type=%s, count=%i", data.mach_id, at.alarm_desc, count)
            bs.append(count)
            bar_categories.append(at.alarm_desc)
        bar_sets.append(bs)


        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("count of each alarm type")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_alarm_count_machine.setChart(bar_chart)

        # x axis


        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

    # page 2 bar chart for alarm time per alarm per machine
    def initialize_machinealarmcleartime_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_alarm_cleartime.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_alarm_cleartime


        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("alarm cleartime")
        bar_categories = []
        for at,cleartime in data.alarm_cleartime.items():
            #DpLog.log().debug("Got cleartime of each alarm type per machine %i: alarm type=%s, cleartime=%i", data.mach_id, at.alarm_desc, cleartime)
            bs.append(cleartime)
            bar_categories.append(at.alarm_desc)
        bar_sets.append(bs)


        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("clear time of each alarm type")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_alarm_cleartime.setChart(bar_chart)

        # x axis
        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)


    # page 2 bar chart for average alarm time per alarm per machine
    def initialize_machinealarmavgclear_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_alarm_avgclear.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_alarm_avgclear


        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("alarm average cleartime")
        bar_categories = []
        for at,avgclear in data.alarm_avgclear.items():
            #DpLog.log().debug("Got average cleartime of each alarm type per machine %i: alarm type=%s, cleartime=%i", data.mach_id, at.alarm_desc, avgclear)
            bs.append(avgclear)
            bar_categories.append(at.alarm_desc)
        bar_sets.append(bs)


        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("clear time of each alarm type")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_avgclear.setChart(bar_chart)

        # x axis
        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)



    # Time Series Analysis
        # time
    def initialize_machineavgspeed_time_line_chart(self) -> None:
        """
        Initializes the avgspeed line chart
        :return:
        """
        DpLog.log().debug("Reading line chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_avgspeed_time.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_avgspeed_time
        DpLog.log().debug("Got %i machines of data", len(data))

        # draw chart
        line_sets = QLineSeries()  # crate an instance for QLineSeries class
        for d in data:
            #DpLog.log().debug("Got average speed for machine %i: hour=%i, spd=%i", d.mach_id, d.hour, d.average_speed)
            line_sets.append(d.hour*1000, d.average_speed)


        line_chart = QChart()  # create an instance for class QChart
        line_chart.addSeries(line_sets)  # implement method addSeries on the instance test_chart
        line_chart.setTitle("Average Speed per machine")
        line_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.gfxview_avgspeed_time.setChart(line_chart)

        # x axis , y axis
        axis_x = QDateTimeAxis() # change the unix time into real time
        axis_x.setFormat("MM.dd.yyyy hh:mm:ss ap")
        # axis_x.setLabelFormat("%d")
        line_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        line_sets.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        line_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        line_sets.attachAxis(axis_y)


    # page 3 machine average prod per hour
    def initialize_machineavgprod_time_line_chart(self) -> None:
        """
        Initializes the avgprod line chart
        :return:
        """
        DpLog.log().debug("Reading line chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_avgprod_time.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_avgprod_time
        DpLog.log().debug("Got %i machines of data", len(data))

        # draw chart
        line_sets = QLineSeries()  # crate an instance for QLineSeries class
        for d in data:
            #DpLog.log().debug("Got average prod for machine %i: hour=%i, prod=%i", d.mach_id, d.hour, d.average_prod)
            line_sets.append(d.hour*1000, d.average_prod)


        line_chart = QChart()  # create an instance for class QChart
        line_chart.addSeries(line_sets)  # implement method addSeries on the instance test_chart
        line_chart.setTitle("Average Prod per machine")
        line_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.gfxview_avgprod_time.setChart(line_chart)

        # x axis , y axis
        axis_x = QDateTimeAxis() # change the unix time into real time
        axis_x.setFormat("MM.dd.yyyy hh:mm:ss ap")
        # axis_x.setLabelFormat("%d")
        line_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        line_sets.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        line_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        line_sets.attachAxis(axis_y)




        # hour
    def initialize_machineavgspeed_hour_line_chart(self) -> None:
        """
        Initializes the hour avgspeed line chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_avgspeed_hour.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_avgspeed_hour

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("average speed")
        for i in range(24):
                        #DpLog.log().debug("Got avgspeed per hour for machine %i: hour=%i, avgspeed percentage=%i", data.mach_id, i, data.avg_speed[i])
                        bs.append(data.avg_speed[i])
        bar_sets.append(bs)

        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("average speed per hour per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_avgspeed_hour.setChart(bar_chart)

        # x axis
        bar_categories = ["12-1AM", "1-2AM", "2-3AM", "3-4AM", "4-5AM", "5-6AM",
                          "6-7AM", "7-8AM", "8-9AM", "9-10AM", "10-11AM", "11-12PM",
                          "12-1PM", "1-2PM", "2-3PM", "3-4PM", "4-5PM", "5-6PM",
                          "6-7PM", "7-8PM", "8-9PM", "9-10PM", "10-11PM", "11-12AM"]

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

    # page 3 machine average prod per hour
    def initialize_machineavgprod_hour_line_chart(self) -> None:
        """
        Initializes the hour avgprod line chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_avgprod_hour.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_avgprod_hour

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("average production")
        for i in range(24):
                        #DpLog.log().debug("Got avgerage prod per hour for machine %i: hour=%i, avgprod=%i", data.mach_id, i, data.avg_prod[i])
                        bs.append(data.avg_prod[i])
        bar_sets.append(bs)

        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("average production per hour per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_avgprod_hour.setChart(bar_chart)

        # x axis
        bar_categories = ["12-1AM", "1-2AM", "2-3AM", "3-4AM", "4-5AM", "5-6AM",
                          "6-7AM", "7-8AM", "8-9AM", "9-10AM", "10-11AM", "11-12PM",
                          "12-1PM", "1-2PM", "2-3PM", "3-4PM", "4-5PM", "5-6PM",
                          "6-7PM", "7-8PM", "8-9PM", "9-10PM", "10-11PM", "11-12AM"]

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

    # page 3 machine good/bad ratio per hour
    def initialize_machinegoodbadratio_hour_line_chart(self) -> None:
        """
        Initializes the good/bad ratio per hour line chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_goodbadratio_hour.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_goodbadratio_hour

        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("good/bad ratio")
        for i in range(24):
                        #DpLog.log().debug("Got good/bad ratio per hour for machine %i: hour=%i, good/bad ratio=%i", data.mach_id, i, data.good_bad_ratio[i])
                        bs.append(data.good_bad_ratio[i])
        bar_sets.append(bs)

        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("good/bad ratio per hour per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_goodbadratio_hour.setChart(bar_chart)

        # x axis
        bar_categories = ["12-1AM", "1-2AM", "2-3AM", "3-4AM", "4-5AM", "5-6AM",
                          "6-7AM", "7-8AM", "8-9AM", "9-10AM", "10-11AM", "11-12PM",
                          "12-1PM", "1-2PM", "2-3PM", "3-4PM", "4-5PM", "5-6PM",
                          "6-7PM", "7-8PM", "8-9PM", "9-10PM", "10-11PM", "11-12AM"]

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)

    # page 3 machine uptime percentage per hour
    def initialize_machineuptime_hour_bar_chart(self) -> None:
        """
        Initializes the testing bar chart
        :return:
        """
        DpLog.log().debug("Reading test bar chart...")
        t_start = self.dteStartTime.dateTime().toSecsSinceEpoch()
        t_end = self.dteEndTime.dateTime().toSecsSinceEpoch()
        mach_id = self._machines[self.cmbMachine.currentIndex()].get_machine_id()

        self.query_machine_uptime_hour.emit(t_start, t_end, mach_id)
        data = DatabaseThread().analyticView_machine_uptime_hour


        # draw chart
        bar_sets = QBarSeries()  # crate an instance for QBarSeries class
        bs = QBarSet("uptime percentage")
        for i in range(24):
#            DpLog.log().debug("Got uptime percentage per hour for machine %i: hour=%i, uptime percentage=%i", data.mach_id, i, data.uptime_percent[i])
            bs.append(data.uptime_percent[i])
        bar_sets.append(bs)


        bar_chart = QChart()  # create an instance for class QChart
        bar_chart.addSeries(bar_sets)  # implement method addSeries on the instance test_chart
        bar_chart.setTitle("uptime percentage per hour per machine")
        bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.gfxview_uptime_hour.setChart(bar_chart)

        # x axis
        bar_categories = ["12-1AM","1-2AM","2-3AM","3-4AM","4-5AM","5-6AM",
                          "6-7AM","7-8AM","8-9AM","9-10AM","10-11AM","11-12PM",
                          "12-1PM","1-2PM","2-3PM","3-4PM","4-5PM","5-6PM",
                          "6-7PM","7-8PM","8-9PM","9-10PM","10-11PM","11-12AM"]

        bar_axisX = QBarCategoryAxis()
        bar_axisX.append(bar_categories)

        # Set rotation so we can fit many X-axis labels nicely
        bar_axisX.setLabelsAngle(0)
        bar_axisX.setTruncateLabels(False)
        font = QFont()
        font.setPointSizeF(7.5)
        bar_axisX.setLabelsFont(font)

        bar_chart.addAxis(bar_axisX, Qt.AlignmentFlag.AlignBottom)
        bar_sets.attachAxis(bar_axisX)

        # Y axis
        bar_axisY = QValueAxis()
        bar_axisY.setRange(0.0, 100.0)
        bar_chart.addAxis(bar_axisY, Qt.AlignmentFlag.AlignLeft)
        bar_sets.attachAxis(bar_axisY)







