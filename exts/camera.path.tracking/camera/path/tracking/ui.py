import omni.ui as ui
import omni.timeline

from .data_controller import *

Basic_BTN_Height = 40
Basic_BTN_Width = 80
Basic_Label_Height = 30
Basic_Label_Width = 60
Margin = 5
innerMargin = 3
Border_radius = 3
Collapse_frame_Height = 40

CollapsableControlFrameStyle = {
    "CollapsableFrame": {
        "background_color": 0xFF333333,
        "secondary_color": 0xFF333333,
        "color": 0xFFCE9600,
        "border_radius": Border_radius,
        "border_color": 0x0,
        "border_width": 0,
        "font_size": 14,
        "padding": Margin * 2,
        "margin_width": Margin,
        "margin_height": 2,
    },
    "CollapsableFrame:hovered": {"secondary_color": 0xFF3C3C3C},
    "CollapsableFrame:pressed": {"secondary_color": 0xFF333333},
    "Button": {"margin_height": 0, "margin_width": Margin, "border_radius": Border_radius},
    "Button:selected": {"background_color": 0xFF666666},
    "Button.Label:disabled": {"color": 0xFF888888},
    "Label::setting":{"margin_height": 0, "width": 100},
    "Slider": {"margin_height": 0, "margin_width": Margin, "border_radius": Border_radius},
    "Slider:disabled": {"color": 0xFF888888},
    "ComboBox": {"margin_height": 0, "margin_width": Margin, "border_radius": Border_radius},
    "Label": {"margin_height": 0, "margin_width": Margin, "width":Basic_Label_Width, "color": 0xFF979797},
    "Label:disabled": {"color": 0xFF888888},
    "Field": {"margin_width": innerMargin},
    "CheckBox": {"margin_width": innerMargin}
}

Button_Styles = {
    "Button::Start_visible":{
        "visible": True,
        "alignment": ui.Alignment.RIGHT
    },
    "Button::Start_invisible":{
        "visible": False
    }
}

Header_Styles = {
    "HStack":{
        "margin_height": 10
    }
}

class ExtensionUI():

    def __init__(self, controller):
        self._controller = controller
        self.base_targetPrimPath = '/World/Target/Cube_'
        self._routeData = self.update_target_info()
        self._speed = Attachment_Info.speed

    def build_ui(self):
        self._window = ui.Window("Camera Controller", width=400, height=250)
        with self._window.frame:
            with ui.VStack():
                with ui.HStack(height=Collapse_frame_Height, style=Header_Styles):
                    ui.Button(
                        "Start",
                        name = "Start_visible",
                        clicked_fn = self._controller._on_click_start_timeline,
                        height = Basic_BTN_Height,
                        width = Basic_BTN_Width
                    )
                    ui.Button(
                        "Stop",
                        clicked_fn = self._controller._on_click_stop_timeline,
                        height = Basic_BTN_Height,
                        width = Basic_BTN_Width
                    )
                self._controls_frame = ui.CollapsableFrame(
                    "Routes", collapsed=False,
                    height=Collapse_frame_Height,
                    style=CollapsableControlFrameStyle
                )
                with self._controls_frame:
                    with ui.VStack():
                        ui.Button(
                            "ADD",
                            clicked_fn = self._controller._on_click_add_camera,
                        )
                self._target_frame = ui.CollapsableFrame(
                    "Targets", collapsed=False,
                    height=Collapse_frame_Height,
                    style=CollapsableControlFrameStyle
                )
                with self._target_frame:
                    with ui.VStack():
                        self._route_data()
                        print("UPDATE!!")
                        ui.Label("")
                        ui.Button(
                            "ADD",
                            alignmaent=ui.Alignment.LEFT_CENTER,
                            clicked_fn = self._controller._on_click_add_target,
                        )
                self._setting_frame = ui.CollapsableFrame(
                    "Setting", collapsed=False,
                    height=Collapse_frame_Height,
                    style=CollapsableControlFrameStyle
                )
                with self._setting_frame:
                    with ui.VStack():
                        self._settingField()
                        self._settingCheckBox('Static Rotation')
        self._window.deferred_dock_in("Property")

    # ==========================================================================
    # UI
    # ==========================================================================

    # Target data UI
    def _route_data(self):
        for i in range(0, len(self._routePrim)):
            self._route_target(i, self._routePrim[i])
            #self._route_target(data, self._routeData[data])

    # target collapse
    def _route_target(self, dataId, dataValue):
        dataname = 'Cube '+ str(dataId)
        with ui.HStack(height=Basic_Label_Height, style={"margin_height":innerMargin}):
            ui.Label(dataname, alignmaent=ui.Alignment.LEFT_CENTER, width=Basic_Label_Width)
            field = ui.StringField(alignmaent=ui.Alignment.LEFT_CENTER)
            field.model.set_value(dataValue)
            ui.Label(' - ',name='delLittle', width=30, alignmaent=ui.Alignment.CENTER)
    
    # Setting
    def _settingField(self):
        with ui.HStack():
            ui.Label('Speed', name="setting", alignmaent=ui.Alignment.LEFT_CENTER, width=150)
            field = ui.FloatField(alignmaent=ui.Alignment.LEFT_CENTER)
            field.model.set_value(self._speed)
            ui.Label(' - ',name='delLittle', width=30, alignmaent=ui.Alignment.CENTER)

    def _settingCheckBox(self, title):
        with ui.HStack():
            ui.Label(title, alignmaent=ui.Alignment.LEFT_CENTER)
            ui.CheckBox(alignmaent=ui.Alignment.RIGHT_CENTER)
    # ==========================================================================
    # Playback
    # ==========================================================================
    
    def update_target_info(self):
        target = dataController.get_route_data('routes_01', 'Translate')
        self._routeData = target
        self._routePrim = []
        for i in range(0, len(target)):
            path = self.base_targetPrimPath + str(i)
            self._routePrim.append(path)
        self._route_data()
        return target

    def teardown(self):
        self._controller = None
        self._controls_frame = None
        self._target_frame = None
        self._window = None
