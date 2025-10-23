from pymodaq.extensions.pid.utils import PIDModelGeneric, DataToActuatorPID, main
from pymodaq_data.data import DataToExport


class PIDModelBoiler(PIDModelGeneric):

    limits = dict(max=dict(state=False, value=10),
                  min=dict(state=False, value=0), )
    konstants = dict(kp=0.001, ki=0, kd=0.0000)

    actuators_name = ["Heater"]
    detectors_name = ['Thermometer']

    Nsetpoints = 1
    setpoint_ini = [20]
    setpoints_names = ['Temperature']



    def __init__(self, pid_controller):
        super().__init__(pid_controller)

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == '':
            pass

    def ini_model(self):
        super().ini_model()
        self.pid_controller.modules_manager.get_mod_from_name('Thermometer', 'det').\
            settings.child('main_settings', 'wait_time').setValue(0)

    def convert_input(self, measurements):
        """
        Convert the measurements in the units to be fed to the PID (same dimensionality as the setpoint)
        Parameters
        ----------
        measurements: (Ordereddict) Ordereded dict of object from which the model extract a value of the same units as the setpoint

        Returns
        -------
        float: the converted input

        """
        self.curr_input = measurements['Thermometer']['data0D']['Thermometer_Boiler_CH000']['data']

        data = [DataCalculated('pid calculated',
                               data=[np.array([self.curr_input])])]
        return DataToExport('pid inputs', data=daza)

    def convert_output(self, outputs, dt, stab=True):
        """

        """
        return DataToActuatorPID('pid output', mode='abs',
                                 data=[outputs[0] / dt])


if __name__ == '__main__':
    main("Boiler.xml")


