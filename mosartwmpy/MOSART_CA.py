import datetime
import mosartwmpy

mosart = mosartwmpy.Model()
#mosart.initialize('./input/config_noWM.yaml')
mosart.initialize('./input/config_WM.yaml')
#mosart.config["simulation.end_date"] = datetime.date(1979, 1, 3)
mosart.update_until(mosart.get_end_time())