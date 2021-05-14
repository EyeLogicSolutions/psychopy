from psychopy.constants import STARTED, NOT_STARTED, PAUSED, STOPPED, FINISHED
from psychopy.alerts import alert
from copy import copy


class EyetrackerControl:
    def __init__(self, server, tracker=None):
        if tracker is None:
            tracker = server.getDevice('tracker')
        self.server = server
        self.tracker = tracker
        self._status = NOT_STARTED

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        old = self._status
        new = self._status = value
        # Skip if there's no change
        if new == old:
            return
        # Start recording if set to STARTED
        if new in (STARTED,):
            if old in (NOT_STARTED, STOPPED, FINISHED):
                # If was previously at a full stop, clear events before starting again
                self.server.clearEvents()
            # Start recording
            self.tracker.setRecordingState(True)
        # Stop recording if set to any stop constants
        if new in (NOT_STARTED, PAUSED, STOPPED, FINISHED):
            self.tracker.setRecordingState(False)


class EyetrackerCalibration:
    def __init__(self, win,
                 eyetracker, target,
                 units="height", colorSpace="rgb",
                 pacingSpeed="", autoPace=True,
                 targetLayout="NINE_POINTS", randomisePos=True,
                 enableAnimation=False, contractOnly=False, velocity=0.5, expandScale=3, expandDur=0.75
                 ):
        # Store params
        self.win = win
        self.eyetracker = eyetracker
        self.target = target
        self.pacingSpeed = pacingSpeed
        self.autoPace = autoPace
        self.targetLayout = targetLayout
        self.randomisePos = randomisePos
        self.units = units or self.win.units
        self.colorSpace = colorSpace or self.win.colorSpace
        # Animation
        self.enableAnimation = enableAnimation
        self.contractOnly = contractOnly
        self.velocity = velocity
        self.expandScale = expandScale
        self.expandDur = expandDur
        # Attribute to store data from last run
        self.last = None

    def run(self):
        tracker = self.eyetracker.getIOHubDeviceClass(full=True)

        # Minimise PsychoPy window
        self.win.winHandle.set_fullscreen(False)
        self.win.winHandle.minimize()

        # Make sure that target will use the same color space and units as calibration
        if self.target.colorSpace == self.colorSpace and self.target.units == self.units:
            target = self.target
        else:
            target = copy(self.target)
            target.colorSpace = self.colorSpace
            target.units = self.units

        # Run calibration
        if tracker == 'eyetracker.hw.sr_research.eyelink.EyeTracker':
            if self.enableAnimation:
                # Alert user that their animation params aren't used
                alert(code=4520, strFields={"brand": "EyeLink"})
            # Run as eyelink
            self.last = self.eyetracker.runSetupProcedure({
                'target_attributes': dict(target),
                'type': self.targetLayout,
                'auto_pace': self.autoPace,
                'pacing_speed': self.pacingSpeed or 1.5,
                'screen_background_color': getattr(self.win._color, self.colorSpace)
            })

        elif tracker == 'eyetracker.hw.tobii.EyeTracker':
            targetAttrs = dict(target)
            targetAttrs['animate'] = {
                'enable': self.enableAnimation,
                'movement_velocity': self.velocity,
                'expansion_ratio': self.expandScale,
                'expansion_speed': self.expandDur,
                'contract_only': self.contractOnly
            }

            # Run as tobii
            self.last = self.eyetracker.runSetupProcedure({
                'target_attributes': targetAttrs,
                'type': self.targetLayout,
                'randomize': self.randomisePos,
                'auto_pace': self.autoPace,
                'pacing_speed': self.pacingSpeed or 1,
                'unit_type': self.units,
                'color_type': self.colorSpace,
                'screen_background_color': getattr(self.win._color, self.colorSpace),
            })

        elif tracker == 'eyetracker.hw.gazepoint.gp3.EyeTracker':
            if not self.autoPace:
                # As GazePoint doesn't use auto-pace, alert user
                alert(4530, strFields={"brand": "GazePoint"})

            targetAttrs = dict(target)
            targetAttrs['animate'] = {
                'enable': self.enableAnimation,
                'expansion_ratio': self.expandScale,
                'contract_only': self.contractOnly
            }
            # Run as GazePoint
            self.last = self.eyetracker.runSetupProcedure({
                'use_builtin': False,
                'target_delay': self.velocity if self.enableAnimation else 0.5,
                'target_duration': self.pacingSpeed or 1.5,
                'target_attributes': targetAttrs,
                'type': self.targetLayout,
                'randomize': self.randomisePos,
                'unit_type': self.units,
                'color_type': self.colorSpace,
                'screen_background_color': getattr(self.win._color, self.colorSpace),
            })

        elif tracker == 'eyetracker.hw.mouse.EyeTracker':

            targetAttrs = dict(target)
            targetAttrs['animate'] = {
                'enable': self.enableAnimation,
                'expansion_ratio': self.expandScale,
                'contract_only': self.contractOnly
            }
            # Run as MouseGaze
            self.last = self.eyetracker.runSetupProcedure({
                'target_attributes': targetAttrs,
                'type': self.targetLayout,
                'randomize': self.randomisePos,
                'auto_pace': self.autoPace,
                'pacing_speed': self.pacingSpeed or 1,
                'unit_type': self.units,
                'color_type': self.colorSpace,
                'screen_background_color': getattr(self.win._color, self.colorSpace),
            })

        else:
            self.last = self.eyetracker.runSetupProcedure({})

        # Bring back PsychoPy window
        self.win.winHandle.set_fullscreen(True)
        self.win.winHandle.maximize()
        self.win.winHandle.activate()
