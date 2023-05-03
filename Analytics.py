from typing import Dict, List

from PyQt6.QtSql import QSqlQuery

from src.dao import MachineStatus, Alarm
from src.dao.Machine import MachinePOD
from src.io import DpLog
from src.io.DatabaseIO import DatabaseIO

# Frequency Analysis
    # state
class MachineStateDistributionPOD:
    """
    Holds state distribution data for a single machine.
    contains the Machine ID, the Machine Name, and a Dict mapping
    the state type to a floating point percentage of the time spent
    in that state, between 0-1.0
    """
    def __init__(self, mach_id: int,
                 mach_name: str,
                 states: Dict[MachineStatus.MachineStateType, float]):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.states = states

class MachineGoodbadDistributionPOD:
    """
    Holds good/bad production distribution data for a single machine.
    contains the Machine ID, the Machine Name, good production and bad production
    """
    def __init__(self, mach_id: int,
                 mach_name: str,
                 mach_goodprod: float,
                 mach_badprod: float):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.mach_goodprod = mach_goodprod
        self.mach_badprod = mach_badprod

class MachineStateavgprodDistributionPOD:
    """
    Holds average production distribution data for a single machine for each state.
    contains the Machine ID, the Machine Name, and a Dict mapping
    the state type to an floating number of the average production in that state, between 0.0-1.0
    """
    def __init__(self, mach_id: int,
                 mach_name: str,
                 states: Dict[MachineStatus.MachineStateType, float]):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.states = states

class MachineStateavgspeedDistributionPOD:
    """
    Holds average speed distribution data for a single machine for each state.
    contains the Machine ID, the Machine Name, and a Dict mapping
    the state type to an floating number of the average production in that state, between 0.0-1.0
    """
    def __init__(self, mach_id: int,
                 mach_name: str,
                 states: Dict[MachineStatus.MachineStateType, float]):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.states = states

    # alarm
class MachineAlarmCountPOD:
    """
    Holds count of each alarm type data for a single machine
    contains the Machine ID, alarm_name and alarm count
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.alarm_counts: Dict[Alarm.AlarmTypePOD, int] = {} # alarm_count is a dictionary where the key is with the type of alarmtypePOD and value is an int

class MachineAlarmCleartimePOD:
    """
    Holds cleartime of each alarm type data for a single machine
    contains the Machine ID, alarm_name and alarm count
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.alarm_cleartime: Dict[Alarm.AlarmTypePOD, float] = {} # alarm_cleartime is a dictionary where the key is with the type of alarmtypePOD and value is a float

class MachineAlarmAvgclearPOD:
    """
    Holds average cleartime of each alarm type data for a single machine
    contains the Machine ID, alarm_name and alarm count
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.alarm_avgclear: Dict[Alarm.AlarmTypePOD, float] = {} # alarm_avgclear is a dictionary where the key is with the type of alarmtypePOD and value is a float


# Time Series Analysis

    # time
class MachineAvgspeedTimePOD:
    """
    Holds average speed data for a single machine.
    contains the Machine ID, the Machine Name, Hour, average speed
    """

    def __init__(self, mach_id: int,
                 mach_name: str,
                 hour: int,
                 average_speed: float):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.hour = hour
        self.average_speed = average_speed

class MachineAvgprodTimePOD:
    """
    Holds average production data for a single machine.
    contains the Machine ID, the Machine Name, Hour, average production
    """

    def __init__(self, mach_id: int,
                 mach_name: str,
                 hour: int,
                 average_prod: float):
        self.mach_id = mach_id
        self.mach_name = mach_name
        self.hour = hour
        self.average_prod = average_prod






    # hour
class MachineAvgspeedHourPOD:
    """
    Holds average speed data for a single machine, hourly in one day.
    contains the Machine ID, the Machine Name, Hour, average speed
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.avg_speed = [0.0] * 24  # create a list of 24 items and each item is a floating number

class MachineAvgprodHourPOD:
    """
    Holds average speed data for a single machine, hourly in one day.
    contains the Machine ID, the Machine Name, Hour, average speed
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.avg_prod = [0.0] * 24  # create a list of 24 items and each item is a floating number

class MachineGoodbadratioHourPOD:
    """
    Holds good/bad ratio data for a single machine, hourly in one day.
    contains the Machine ID, the Machine Name, Hour, good/bad ratio
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.good_bad_ratio = [0.0] * 24  # create a list of 24 items and each item is a floating number

class MachineUptimeHourPOD:
    """
    Holds good/bad ratio data for a single machine, hourly in one day.
    contains the Machine ID, the Machine Name, Hour, uptime percentage
    """
    def __init__(self, mach_id: int):
        self.mach_id = mach_id
        self.uptime_percent = [0.0] * 24  # create a list of 24 items and each item is a floating number

class AnalyticsDAO:

# Frequency Analysis
    # state distribution
    @staticmethod
    def get_machines_state_distribution(t_start: int, t_end: int, machines: List[MachinePOD]) -> List[MachineStateDistributionPOD]:
        """
        Queries a list of the distribution of states of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT 
   	ms2.MACHINE_ID,
    ms2.CURRENT_STATE,
  	COUNT(ms2.STS_ID) / (SELECT 
                         	COUNT(ms1.STS_ID) 
                         FROM MACHINE_STATUS ms1 
                         WHERE ms1.MACHINE_ID=ms2.MACHINE_ID
                         AND ms2.STS_TIME >= :t_start AND ms2.STS_TIME <= :t_end
    ) AS TIME_FRAC
FROM MACHINE_STATUS ms2
WHERE
	ms2.STS_TIME >= :t_start AND ms2.STS_TIME <= :t_end
GROUP BY ms2.MACHINE_ID, ms2.CURRENT_STATE"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine state distribution: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine state distribution", num_sts)

            # start from here
            sts_dist: List[MachineStateDistributionPOD] = []  # create a list with the type of MachineStateDistributionPOD

            for m in machines:  # iterate all instances in machine List
                new_sd = MachineStateDistributionPOD(
                    mach_id=m.get_machine_id(),
                    mach_name=m.get_machine_name(),
                    states={}  # create an empty dictionary
                )  # create an instance of class MachineStateDistributionPOD, three arguments of the __init__ method

                for s in MachineStatus.MachineStateType:  # iterate all instances in MachineStateType enum class under MachineStatus file
                    new_sd.states[s] = 0.0  # mapping the time related to the key of machinestateype in the enum and add to the dictionary new_sd.state, initialize to 0.0

                sts_dist.append(new_sd)  # add new_sd to sts_dist

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                state = MachineStatus.MachineStateType(int(query.value(1)))
                total_time = float(query.value(2))

                for i in range(len(sts_dist)):
                    if sts_dist[i].mach_id == mach_id_query:
                        sts_dist[i].states[state] = total_time
            return sts_dist

    @staticmethod
    def get_machines_goodbad_distribution(t_start: int, t_end: int, machines: List[MachinePOD]) -> List[MachineStateDistributionPOD]:
        """
        Queries a list of the distribution of good and bad production of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT
	MACHINE_ID,
	GOOD_PROD,
    BAD_PROD
FROM	
	(
	SELECT
    	MACHINE_ID,
    	SUM(CASE
            	WHEN CURRENT_STATE=5
            	THEN COUNT_PROD
            	ELSE 0
        	END) AS GOOD_PROD,
    	SUM(CASE
            	WHEN CURRENT_STATE=5
            	THEN 0
            	ELSE COUNT_PROD
        	END) AS BAD_PROD
	FROM
    	MACHINE_STATUS
    WHERE
        STS_TIME>=:t_start and STS_TIME<=:t_end
	GROUP BY
    	MACHINE_ID
    ) AS SUBQ"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine good/bad production distribution: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine good/bad production distribution", num_sts)

            # start from here
            mach_goodbad_dist: List[MachineGoodbadDistributionPOD] = []  # create a list with the type of MachineGoodbadDistributionPOD

            for m in machines:  # iterate all instances in machine List
                new_sd = MachineGoodbadDistributionPOD(
                    mach_id=m.get_machine_id(),
                    mach_name=m.get_machine_name(),
                    mach_goodprod=0.0,
                    mach_badprod=0.0
                )  # create an instance of class MachineGoodbadDistributionPOD, four arguments of the __init__ method

                mach_goodbad_dist.append(new_sd)  # add new_sd to mach_goodbad_dist

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                good_prod_query = int(query.value(1))
                bad_prod_query = int(query.value(2))


                for i in range(len(mach_goodbad_dist)):
                    if mach_goodbad_dist[i].mach_id == mach_id_query:
                        mach_goodbad_dist[i].mach_goodprod = good_prod_query
                        mach_goodbad_dist[i].mach_badprod = bad_prod_query
            return mach_goodbad_dist

    @staticmethod
    def get_machines_stateavgprod_distribution(t_start: int, t_end: int, machines: List[MachinePOD]) -> List[MachineStateavgprodDistributionPOD]:
        """
        Queries a list of the distribution of average production each states of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT
	MACHINE_ID,
	CURRENT_STATE,
	AVG(COUNT_PROD) AS AVERAGE_PRODUCTION
FROM
	MACHINE_STATUS
WHERE
    STS_TIME>=:t_start and STS_TIME<=:t_end
GROUP BY
	MACHINE_ID,
	CURRENT_STATE"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine average production for each state distribution: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine average production for each state distribution", num_sts)

            # start from here
            machine_avgprod_dist: List[MachineStateavgprodDistributionPOD] = []  # create a list with the type of MachineStateavgprodDistributionPOD

            for m in machines:  # iterate all instances in machine List
                new_sd = MachineStateavgprodDistributionPOD(
                    mach_id=m.get_machine_id(),
                    mach_name=m.get_machine_name(),
                    states={}  # create an empty dictionary
                )  # create an instance of class MachineStateDistributionPOD, three arguments of the __init__ method

                for s in MachineStatus.MachineStateType:  # iterate all instances in MachineStateType enum class under MachineStatus file
                    new_sd.states[s] = 0.0  # mapping the time related to the key of machinestateype in the enum and add to the dictionary new_sd.state, initialize to 0.0

                machine_avgprod_dist.append(new_sd)  # add new_sd to  machine_avgprod_dist

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                state = MachineStatus.MachineStateType(int(query.value(1)))
                average_production = float(query.value(2))

                for i in range(len(machine_avgprod_dist)):
                    if machine_avgprod_dist[i].mach_id == mach_id_query:
                        machine_avgprod_dist[i].states[state] = average_production
            return machine_avgprod_dist

    @staticmethod
    def get_machines_stateavgspeed_distribution(t_start: int, t_end: int, machines: List[MachinePOD]) -> List[MachineStateavgspeedDistributionPOD]:
        """
        Queries a list of the distribution of average speed each states of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT
	MACHINE_ID,
	CURRENT_STATE,
	720*AVG(CURRENT_SPEED) AS AVERAGE_SPEED
FROM
	MACHINE_STATUS
WHERE
    STS_TIME>=:t_start and STS_TIME<=:t_end
GROUP BY
	MACHINE_ID,
	CURRENT_STATE"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine average speed for each state distribution: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine average speed for each state distribution", num_sts)

            # start from here
            machine_avgspeed_dist: List[MachineStateavgspeedDistributionPOD] = []  # create a list with the type of MachineStateavgspeedDistributionPOD

            for m in machines:  # iterate all instances in machine List
                new_sd = MachineStateavgspeedDistributionPOD(
                    mach_id=m.get_machine_id(),
                    mach_name=m.get_machine_name(),
                    states={}  # create an empty dictionary
                )  # create an instance of class MachineStateDistributionPOD, three arguments of the __init__ method

                for s in MachineStatus.MachineStateType:  # iterate all instances in MachineStateType enum class under MachineStatus file
                    new_sd.states[s] = 0.0  # mapping the time related to the key of machinestateype in the enum and add to the dictionary new_sd.state, initialize to 0.0

                machine_avgspeed_dist.append(new_sd)  # add new_sd to machine_avgspeed_dist

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                state = MachineStatus.MachineStateType(int(query.value(1)))
                average_speed = float(query.value(2))

                for i in range(len(machine_avgspeed_dist)):
                    if machine_avgspeed_dist[i].mach_id == mach_id_query:
                        machine_avgspeed_dist[i].states[state] = average_speed
            return machine_avgspeed_dist


    # alarm
    @staticmethod  # frequency analysis count of alarm type per machine
    def get_machine_alarm_count(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> MachineAlarmCountPOD:
        """
        Queries a list of the count of each type of alarm of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT
	MA.MACHINE_ID,
    MA.ALARM_CODE,
    AT.ALARM_DESC,
	COUNT(MA.ALARM_CODE) AS COUNT_ALARM
FROM	
	MACHINE_ALARM AS MA
LEFT JOIN
	ALARM_TYPE AS AT
ON 
	MA.ALARM_CODE=AT.AT_ID
WHERE
    MA.ALARM_TIME>=:t_start and MA.ALARM_TIME<=:t_end and MA.MACHINE_ID=:mach_id
GROUP BY
	MA.MACHINE_ID,
    MA.ALARM_CODE
ORDER BY
	MA.MACHINE_ID,
    MA.ALARM_CODE"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get count of each type of alarm per machine : %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i count of each type of alarm per machine", num_sts)

            # start from here

            m = MachineAlarmCountPOD(mach_id)  # create an instance of class MachineHourPOD

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                alarm_code_query = int(query.value(1))
                alarm_desc_query = str(query.value(2))
                alarm_counts_query = float(query.value(3))

                ap = Alarm.AlarmTypePOD(alarm_code_query, alarm_desc_query)

                m.alarm_counts[ap] = alarm_counts_query

            return m

    @staticmethod  # frequency analysis count of alarm type per machine
    def get_machine_alarm_cleartime(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> MachineAlarmCleartimePOD:
        """
        Queries a list of the cleartimet of each type of alarm of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT MA.ALARM_CODE,
    MA.MACHINE_ID,
    AT.ALARM_DESC,
    SUM(HOUR(TIMEDIFF(FROM_UNIXTIME(MA.ACK_TIME),FROM_UNIXTIME(MA.ALARM_TIME)))) AS ALARM_CLEAR_TIME
FROM 
 	MACHINE_ALARM MA
LEFT JOIN
 	ALARM_TYPE AS AT
ON
 	MA.ALARM_CODE = AT.AT_ID
WHERE
    ALARM_TIME>=:t_start and ACK_TIME<=:t_end and MACHINE_ID=:mach_id
GROUP BY
    MA.ALARM_CODE,
    MA.MACHINE_ID

"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get cleartime of each type of alarm per machine : %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i cleartime of each type of alarm per machine", num_sts)

            # start from here

            m = MachineAlarmCleartimePOD(mach_id)

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                alarm_code_query = int(query.value(1))
                alarm_desc_query = str(query.value(2))
                alarm_cleartime_query = float(query.value(3))

                ap = Alarm.AlarmTypePOD(alarm_code_query, alarm_desc_query)

                m.alarm_cleartime[ap] = alarm_cleartime_query

            return m

    @staticmethod  # frequency analysis count of alarm type per machine
    def get_machine_alarm_avgclear(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> MachineAlarmAvgclearPOD:
        """
        Queries a list of the average cleartime of each type of alarm of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT MA.ALARM_CODE,
    MA.MACHINE_ID,
    AT.ALARM_DESC,
    AVG(HOUR(TIMEDIFF(FROM_UNIXTIME(MA.ACK_TIME),FROM_UNIXTIME(MA.ALARM_TIME)))) AS ALARM_CLEAR_TIME
FROM 
  MACHINE_ALARM MA
LEFT JOIN
  ALARM_TYPE AS AT
ON
  MA.ALARM_CODE = AT.AT_ID
GROUP BY
    MA.ALARM_CODE,
    MA.MACHINE_ID

"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get average cleartime of each type of alarm per machine : %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i average cleartime of each type of alarm per machine", num_sts)

            # start from here

            m = MachineAlarmAvgclearPOD(mach_id)

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                alarm_code_query = int(query.value(1))
                alarm_desc_query = str(query.value(2))
                alarm_avgclear= float(query.value(3))

                ap = Alarm.AlarmTypePOD(alarm_code_query, alarm_desc_query)

                m.alarm_avgclear[ap] = alarm_avgclear

            return m


# Time Series Analysis
    # time
    @staticmethod
    def get_machine_avgspeed_time(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> List[MachineAvgspeedHourPOD]:
        """
        Queries a list of the average speed of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT HOUR,
    MACHINE_ID,
    AVG(CURRENT_SPEED) AS AVERAGE_SPEED
FROM 
    (
    SELECT
        STS_ID,
        MACHINE_ID,
        COUNT_PROD,
        CURRENT_SPEED,
        FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
        ROUND(STS_TIME/3600, 0) * 3600 AS HOUR
    FROM 
 	    MACHINE_STATUS
 	WHERE
 	    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id and CURRENT_STATE=5
    ) AS SUBQ
GROUP BY
    HOUR,
    MACHINE_ID
ORDER BY
    HOUR ASC
"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine average speed: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine average speed", num_sts)

            # start from here
            mach_avgspeed_time_dist: List[MachineAvgspeedTimePOD] = []

            ids_temp = []
            names_temp = []
            hours_temp = []
            speed_temp = []
            while query.next():  # iterate all the query results
                """mach_id_query = int(query.value(1))
                mach_name_query = ""
                hour_query = int(query.value(0))
                average_speed_query = int(query.value(2))

                m = MachineAvgspeedHourPOD(mach_id_query, mach_name_query, hour_query, average_speed_query)
                mach_avgspeed_hour_dist.append(m)"""
                ids_temp.append(int(query.value(1)))
                names_temp.append("")
                hours_temp.append(int(query.value(0)))
                speed_temp.append(float(query.value(2)))

            average_window_side_hours = 1
            filtered_speed = []
            for row in range(len(ids_temp)):  # rolling average

                # Find the row that's the average window's worth of hours before this row, limiting to row zero
                row_start = row
                while row_start > 0 and hours_temp[row_start] + average_window_side_hours > hours_temp[row]:
                    row_start -= 1

                # Find the row that's the average window's worth of hours after this row, limiting to the last row
                row_end = row
                while row_end < len(hours_temp)-1 and hours_temp[row_end] - average_window_side_hours < hours_temp[row]:
                    row_end += 1

                # average over the range of row_start to row_end. Includes row_end.
                cnt = 0
                tmp_spd = 0.0
                for ar in range(row_start, row_end+1):
                    cnt += 1
                    tmp_spd += speed_temp[ar]

                # Append filtered data to the output list
                m = MachineAvgspeedTimePOD(ids_temp[row],
                                           names_temp[row],
                                           hours_temp[row],
                                           int(tmp_spd / cnt))
                mach_avgspeed_time_dist.append(m)

            return mach_avgspeed_time_dist

    @staticmethod
    def get_machine_avgprod_time(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> List[
        MachineAvgprodTimePOD]:
        """
        Queries a list of the average prod of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT HOUR,
    MACHINE_ID,
    360*AVG(COUNT_PROD) AS AVERAGE_PROD
FROM 
    (
    SELECT
        STS_ID,
        MACHINE_ID,
        COUNT_PROD,
        CURRENT_SPEED,
        FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
        ROUND(STS_TIME/3600, 0) * 3600 AS HOUR
    FROM 
 	    MACHINE_STATUS
 	WHERE
 	    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id
    ) AS SUBQ
GROUP BY
    HOUR,
    MACHINE_ID
ORDER BY
    HOUR ASC
"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine average prod: %s", query.lastError().text())
            return []
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine average prod", num_sts)

            # start from here
            mach_avgprod_time_dist: List[MachineAvgprodTimePOD] = []

            ids_temp = []
            names_temp = []
            hours_temp = []
            prod_temp = []
            while query.next():  # iterate all the query results
                """mach_id_query = int(query.value(1))
                mach_name_query = ""
                hour_query = int(query.value(0))
                average_prod_query = int(query.value(2))

                m = MachineAvgprodHourPOD(mach_id_query, mach_name_query, hour_query, average_prod_query)
                mach_avgprod_hour_dist.append(m)"""
                ids_temp.append(int(query.value(1)))
                names_temp.append("")
                hours_temp.append(int(query.value(0)))
                prod_temp.append(float(query.value(2)))

            average_window_side_hours = 50
            filtered_speed = []
            for row in range(len(ids_temp)):  # rolling average

                # Find the row that's the average window's worth of hours before this row, limiting to row zero
                row_start = row
                while row_start > 0 and hours_temp[row_start] + average_window_side_hours > hours_temp[row]:
                    row_start -= 1

                # Find the row that's the average window's worth of hours after this row, limiting to the last row
                row_end = row
                while row_end < len(hours_temp) - 1 and hours_temp[row_end] - average_window_side_hours < hours_temp[
                    row]:
                    row_end += 1

                # average over the range of row_start to row_end. Includes row_end.
                cnt = 0
                tmp_prod = 0.0
                for ar in range(row_start, row_end + 1):
                    cnt += 1
                    tmp_prod += prod_temp[ar]

                # Append filtered data to the output list
                m = MachineAvgprodTimePOD(ids_temp[row],
                                           names_temp[row],
                                           hours_temp[row],
                                           int(tmp_prod / cnt))
                mach_avgprod_time_dist.append(m)

            return mach_avgprod_time_dist









    # hour
    @staticmethod
    def get_machine_avgspeed_hour(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> List[MachineAvgspeedHourPOD]:
        """
        Queries a list of the average speed per hour of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT HOUR,
    MACHINE_ID,
    AVG(CURRENT_SPEED) AS AVERAGE_SPEED
FROM 
    (
    SELECT
        STS_ID,
        MACHINE_ID,
        COUNT_PROD,
        CURRENT_SPEED,
        FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
        HOUR(FROM_UNIXTIME(STS_TIME)) AS HOUR
    FROM 
 	    MACHINE_STATUS
 	WHERE
 	    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id
    ) AS SUBQ
GROUP BY
    HOUR,
    MACHINE_ID
ORDER BY
    HOUR ASC
"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine avgsoeed per hour: %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine avgspeed per hour", num_sts)

            # start from here

            m = MachineAvgspeedHourPOD(mach_id)  # create an instance of class MachineHourPOD

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(1))
                hour = int(query.value(0))
                avg_speed = float(query.value(2))*100.0

                m.avg_speed[hour] = avg_speed

            return m


    @staticmethod
    def get_machine_avgprod_hour(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> List[
        MachineAvgprodHourPOD]:
        """
        Queries a list of the average prod per hour of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
    DISTINCT HOUR,
    MACHINE_ID,
    AVG(COUNT_PROD) AS AVERAGE_PROD
FROM 
    (
    SELECT
        STS_ID,
        MACHINE_ID,
        COUNT_PROD,
        CURRENT_SPEED,
        FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
        HOUR(FROM_UNIXTIME(STS_TIME)) AS HOUR
    FROM 
 	    MACHINE_STATUS
 	WHERE
 	    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id
    ) AS SUBQ
GROUP BY
    HOUR,
    MACHINE_ID
ORDER BY
    HOUR ASC
"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine avgprod per hour: %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine avgprod per hour", num_sts)

            # start from here

            m = MachineAvgprodHourPOD(mach_id)  # create an instance of class MachineHourPOD

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(1))
                hour = int(query.value(0))
                avg_prod = float(query.value(2))*100.0

                m.avg_prod[hour] = avg_prod

            return m


    @staticmethod  # time series analysis good/bad ratio per hour
    def get_machine_goodbadratio_hour(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> List[
        MachineGoodbadratioHourPOD]:
        """
        Queries a list of the goodbadratio per hour of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """
SELECT 
	DISTINCT HOUR,
   MACHINE_ID,
	IFNULL(SUM(GOOD_PROD)/SUM(BAD_PROD),0) AS GOOD_BAD_RATIO
FROM 
	(
	SELECT
		STS_ID,
		MACHINE_ID,
		CURRENT_STATE,
		CASE WHEN CURRENT_STATE=5 THEN COUNT_PROD ELSE 0 END AS GOOD_PROD,
		CASE WHEN CURRENT_STATE=5 THEN 0 ELSE COUNT_PROD END AS BAD_PROD,
		FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
		HOUR(FROM_UNIXTIME(STS_TIME)) AS HOUR
	FROM 
 		MACHINE_STATUS
 	WHERE
 	    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id
  	) AS SUBQ1
GROUP BY
	HOUR,
   MACHINE_ID
ORDER BY 
 	HOUR,
   MACHINE_ID;
"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine good/bad ratio per hour: %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine good/bad ratio per hour", num_sts)

            # start from here

            m = MachineGoodbadratioHourPOD(mach_id)  # create an instance of class MachineHourPOD

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(1))
                hour = int(query.value(0))
                good_bad_ratio = float(query.value(2))*100.0

                m.good_bad_ratio[hour] = good_bad_ratio

            return m

    @staticmethod  # time series analysis uptime percentage per hour
    def get_machine_uptime_hour(t_start: int, t_end: int, mach_id: int, machines: List[MachinePOD]) -> MachineUptimeHourPOD:
        """
        Queries a list of the uptime percentage per hour of each machine on a certain time range
        :param t_start: start of the range, unix time
        :param t_end: end of the range, unix time
        :param machines: list of all machines, for initializing the data
        :return:
        """

        query_str = """SELECT
	MACHINE_ID,
    HOUR,
    IFNULL(IFNULL(CASE WHEN CURRENT_STATE=5 THEN COUNT(DISTINCT DATE) END,0)/DATEDIFF(MAX(DATE),MIN(DATE)),0) AS UPTIME_PERCENT
FROM
	(
SELECT
	STS_ID,
    MACHINE_ID,
    HOUR(FROM_UNIXTIME(STS_TIME)) AS HOUR,
	CURRENT_STATE,
	FROM_UNIXTIME(STS_TIME) AS ACTUAL_TIME,
    DATE(FROM_UNIXTIME(STS_TIME)) AS DATE
FROM
	MACHINE_STATUS
WHERE
    STS_TIME>=:t_start and STS_TIME<=:t_end and MACHINE_ID=:mach_id
ORDER BY	
	HOUR, ACTUAL_TIME
    ) AS SUBQ
GROUP BY	
	HOUR
ORDER BY	
	HOUR"""

        db = DatabaseIO().get_db()
        query = QSqlQuery(db)

        query.prepare(query_str)
        query.bindValue(":t_start", t_start)
        query.bindValue(":t_end", t_end)
        query.bindValue(":mach_id", mach_id)

        ok = query.exec()

        if not ok:
            DpLog.log().error("Failed to query get machine uptime per hour: %s",
                              query.lastError().text())
            return None
        else:
            num_sts = query.size()
            DpLog.log().debug("Found %i machine uptime per hour", num_sts)

            # start from here

            m = MachineUptimeHourPOD(mach_id)  # create an instance of class MachineHourPOD

            while query.next():  # iterate all the query results
                mach_id_query = int(query.value(0))
                hour = int(query.value(1))
                uptime_percent = float(query.value(2))*100.0

                m.uptime_percent[hour] = uptime_percent

            return m




