from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, \
    comon_parameters_fun
from pymodaq_utils.utils import ThreadCommand, getLineInfo
# object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict
from pymodaq_plugins_pid.hardware.beamsteering import BeamSteeringController

class DAQ_Move_BeamSteering(DAQ_Move_base):
    """
        Wrapper object to access the Mock fonctionnalities, similar wrapper for all controllers.

        =============== ==============
        **Attributes**    **Type**
        *params*          dictionnary
        =============== ==============
    """
    _controller_units = 'millimeter'
    is_multiaxes = True
    stage_names = BeamSteeringController.axis
    _axis_names: Union[List[str], Dict[str, int]] = ['H', 'V']
    _epsilon = 1

    params = comon_parameters_fun(axis_names=_axis_names)

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

    def check_position(self):
        """
            Get the current position from the hardware with scaling conversion.

            Returns
            -------
            float
                The position obtained after scaling conversion.

            See Also
            --------
            DAQ_Move_base.get_position_with_scaling, daq_utils.ThreadCommand
        """
        pos = self.controller.check_position(self.settings.child('multiaxes', 'axis').value())
        # print('Pos from controller is {}'.format(pos))
        # pos=self.get_position_with_scaling(pos)
        self.current_position = pos
        self.emit_status(ThreadCommand('check_position', [pos]))
        return pos

    def close(self):
        """
          not implemented.
        """
        pass

    def commit_settings(self, param):
        """
            | Activate any parameter changes on the PI_GCS2 hardware.
            |
            | Called after a param_tree_changed signal from DAQ_Move_main.

        """

        pass

    def ini_stage(self, controller=None):
        """
            Initialize the controller and stages (axes) with given parameters.

            ============== ================================================ ==========================================================================================
            **Parameters**  **Type**                                         **Description**

            *controller*    instance of the specific controller object       If defined this hardware will use it and will not initialize its own controller instance
            ============== ================================================ ==========================================================================================

            Returns
            -------
            Easydict
                dictionnary containing keys:
                 * *info* : string displaying various info
                 * *controller*: instance of the controller object in order to control other axes without the need to init the same controller twice
                 * *stage*: instance of the stage (axis or whatever) object
                 * *initialized*: boolean indicating if initialization has been done corretly

            See Also
            --------
             daq_utils.ThreadCommand
        """
        try:
            # initialize the stage and its controller status
            # controller is an object that may be passed to other instances of DAQ_Move_Mock in case
            # of one controller controlling multiaxes

            self.status.update(edict(info="", controller=None, initialized=False))

            if self.is_master:
                self.controller = BeamSteeringController()
            else:
                self.controller = controller

            info = "Mock PID stage"
            self.status.info = info
            self.status.controller = self.controller
            self.status.initialized = True
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
            return self.status

    def move_Abs(self, position):
        """
            Make the absolute move from the given position after thread command signal was received in DAQ_Move_main.

            =============== ========= =======================
            **Parameters**  **Type**   **Description**

            *position*       float     The absolute position
            =============== ========= =======================

            See Also
            --------
            DAQ_Move_base.set_position_with_scaling, DAQ_Move_base.poll_moving

        """
        position = self.check_bound(position)
        # position=self.set_position_with_scaling(position)
        # print(position)
        self.target_position = position
        self.controller.move_abs(self.target_position, self.settings.child('multiaxes', 'axis').value())


    def move_Rel(self, position):
        """
            Make the relative move from the given position after thread command signal was received in DAQ_Move_main.

            =============== ========= =======================
            **Parameters**  **Type**   **Description**

            *position*       float     The absolute position
            =============== ========= =======================

            See Also
            --------
            hardware.set_position_with_scaling, DAQ_Move_base.poll_moving

        """
        position = self.check_bound(self.current_position + position) - self.current_position
        self.target_position = position + self.current_position

        self.controller.move_rel(position, self.settings.child('multiaxes', 'axis').value())


    def move_Home(self):
        """
          Send the update status thread command.
            See Also
            --------
            daq_utils.ThreadCommand
        """
        self.emit_status(ThreadCommand('Update_Status', ['Move Home not implemented']))

    def stop_motion(self):
        """
          Call the specific move_done function (depending on the hardware).

          See Also
          --------
          move_done
        """
        self.move_done()
