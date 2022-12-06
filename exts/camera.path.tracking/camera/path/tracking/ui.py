import omni.ui as ui
from typing import List
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
    "Label:hovered":{"secondary_color": 0xFF3C3C3C},
    "Field": {"margin_width": innerMargin},
    "CheckBox": {"margin_width": innerMargin},
    "Line": {"color":0xFF888888}
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
Label_spec = {
    "Label:hovered":{"secondary_color": 0xFF3C3C3C}
}

# ==========================================================================
# Treeview
# ==========================================================================
class RouteItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
class RouteModel(ui.AbstractItemModel):
    """
    Represents the list of commands registered in Kit.
    It is used to make a single level tree appear like a simple list.
    """

    def __init__(self, routes):
        super().__init__()
        self._route_changed(routes)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self.routes

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel.
        """
        if item and isinstance(item, RouteItem):
            return item.name_model

    def _route_changed(self, routes):
        self.routes = []
        for i in range(1, routes+1):
            RouteName = 'Route 0' + str(i)
            self.routes.append(RouteItem(RouteName))
        self._item_changed(None)

class TargetItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
class TargetModel(ui.AbstractItemModel):
    """
    Represents the list of commands registered in Kit.
    It is used to make a single level tree appear like a simple list.
    """

    def __init__(self, targets):
        super().__init__()
        self._target_changed(targets)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self.routes

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel.
        """
        if item and isinstance(item, RouteItem):
            return item.name_model

    def _target_changed(self, targets):
        self.routes = []
        for i in range(0, targets):
            RouteName = '/World/Target/Cube_' + str(i)
            self.routes.append(RouteItem(RouteName))
        self._item_changed(None)
class ExtensionUI():

    def __init__(self, controller):
        self._controller = controller
        self.base_targetPrimPath = '/World/Target/Cube_'
        self._speed = Attachment_Info.speed
        self._target_selected = ''

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
                        self._route_model = RouteModel(self.get_routeCount())
                        tree_view = ui.TreeView(
                            self._route_model, root_visible=False, header_visible=False,
                            selection_changed_fn = self.on_selection_route_change,
                            style={"TreeView.Item": {"margin": 4, "font_size": 16}}
                        )
                        ui.Line()
                        with ui.HStack(margin=Margin): 
                            ui.Button(
                                "ADD",
                                alignmaent=ui.Alignment.LEFT_CENTER,
                                width=70,
                                height=15,
                                clicked_fn = self._controller._on_click_add_route,
                            )
                            ui.Button(
                                "REMOVE",
                                alignmaent=ui.Alignment.LEFT_CENTER,
                                clicked_fn = self._controller._on_click_rm_route,
                                width=70,
                                height=15
                            )
                        ui.Label("")
                self._target_frame = ui.CollapsableFrame(
                    "Route Targets", collapsed=False,
                    height=Collapse_frame_Height,
                    style=CollapsableControlFrameStyle
                )
                with self._target_frame:
                    with ui.VStack():
                        #ui.Label(self.get_routeName(), height=Basic_Label_Height)
                        self._target_model = TargetModel(len(self.get_route_data()))
                        tree_view = ui.TreeView(
                            self._target_model, root_visible=False, header_visible=False,
                            selection_changed_fn = self.on_selection_target_change,
                            style={"TreeView.Item": {"margin": 4, "font_size": 16}}
                        )
                        ui.Line()
                        with ui.HStack(margin=Margin):                        
                            ui.Button(
                                "ADD",
                                alignmaent=ui.Alignment.LEFT_CENTER,
                                clicked_fn = self._controller._on_click_add_target,
                                width=70,
                                height=15
                            )
                            '''
                            ui.Button(
                                "REMOVE",
                                alignmaent=ui.Alignment.LEFT_CENTER,
                                clicked_fn = self._controller._on_click_add_target,
                                width=70,
                                height=15
                            )
                            '''
                            ui.Label("")
                            ui.Button(
                                "Clear All",
                                alignmaent=ui.Alignment.RIGHT_CENTER,
                                clicked_fn = self._controller._on_click_clear_route,
                                width=70,
                                height=15
                            )
                        ui.Label("")
                            
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

    def on_selection_route_change(self, selected_items):
        for item in selected_items:
            newroute = item.name_model.as_string
            num = newroute.split("0")
            Attachment_Info.changeRoute(int(num[1]))
        self.update_target_info()
    
    def on_selection_target_change(self, selected_item):
        for item in selected_item:
            target_selected = item.name_model.as_string
            self._target_selected = target_selected.split("_")

    # Target data UI
    def _route_data(self):
        self.get_route_data()
        for i in range(0, len(self._routePrim)):
            self._route_target(i, self._routePrim[i])

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
            ui.Label(title, alignmaent=ui.Alignment.LEFT_CENTER, width=150)
            staticrotation = ui.CheckBox(alignmaent=ui.Alignment.LEFT_CENTER)
            ABLE = ui.Label(staticrotation.model.get_value_as_string())
            staticrotation.model.add_value_changed_fn(
                lambda A, B=ABLE:self.change_checkbox(A.get_value_as_string(), ABLE)
            )

    def change_checkbox(self, value, ABLE):
        Attachment_Info.changeRotSetting()
        ABLE.text = value

    # ==========================================================================
    # CallBack
    # ==========================================================================
    def get_routeCount(self):
        count = Attachment_Info.routeCount
        self._routeCount = count
        return count
    
    def get_selectedRoute(self):
        selected = Attachment_Info.selectedRoute
        self.selectedRoute = selected
        return selected
    
    def get_routeName(self):
        count = self.get_selectedRoute()
        name = 'routes_0' + str(count)
        return name
    
    def get_route_data(self):
        routeName = self.get_routeName()
        targets = dataController.get_route_data(routeName, 'Translate')
        self.get_route_Prim(targets)
        return targets
    
    def get_route_Prim(self, targets):
        self._routePrim = []
        for i in range(0, len(targets)):
            path = self.base_targetPrimPath + str(i)
            self._routePrim.append(path)

    # ==========================================================================
    # Playback
    # ==========================================================================
    
    def update_target_info(self):
        routeCount = self.get_routeCount()
        self._route_model._route_changed(routeCount)
        targets = self.get_route_data()
        self._target_model._target_changed(len(targets))

    def teardown(self):
        self._controller = None
        self._controls_frame = None
        self._target_frame = None
        self._setting_frame = None
        self._route_model = None
        self._window = None
