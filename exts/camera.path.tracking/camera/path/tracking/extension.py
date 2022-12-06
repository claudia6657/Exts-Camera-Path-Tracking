import omni.ext
import omni.usd
import omni.kit
import carb
import omni.timeline

import asyncio

from .model import ExtensionModel
from .ui import *
from .data_controller import *

class CameraPathTrackingExtension(omni.ext.IExt):

    def on_startup(self, ext_id):

        if omni.usd.get_context().get_stage() is None:
            # Workaround for running within test environment.
            omni.usd.get_context().new_stage()

        self._stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="Stage Open/Closing Listening"
        )

        self.model = ExtensionModel()

        self._ui = ExtensionUI(self)
        self._ui.build_ui()

    def on_shutdown(self):
        timeline = omni.timeline.get_timeline_interface()
        if timeline.is_playing():
            timeline.stop()

        self._ui.teardown()
        self._ui = None
        self.model = None

    def _on_stage_event(self, event: carb.events.IEvent):
        """Called on USD Context event"""
        if event.type == int(omni.usd.StageEventType.CLOSING):
            self.model.clear_attachments()
            self._update_ui()

    # ==========================================================================
    # Events
    # =========================================================================

    def _on_click_add_route(self):
        add = dataController.add_new_route()
        self._ui.update_target_info()

    def _on_click_rm_route(self):
        rm = dataController.rm_route()
        self._ui.update_target_info()
    
    def _on_click_add_target(self):
        T, R = dataController._get_camera_pos(self.model.camPath, self.model.getCamPrim)
        CamT = T[0], T[1], T[2]
        CamR = R[0], R[1], R[2]

        addTarget = False
        addTarget = dataController.add_new_target(Attachment_Info.routeName(), CamT, CamR)
        self.model.create_prim('Cube', (CamT), (CamR))

        self._ui.update_target_info()
    
    def _on_click_rm_target(self):
        dataController.del_target(Attachment_Info.routeName(), self._ui._target_selected)
        self._ui.update_target_info()

    def _on_click_clear_route(self):
        dataController.clear_target(Attachment_Info.routeName())
        self._ui.update_target_info()
    
    def _on_click_select_route(self, num):
        Attachment_Info.changeRoute(num)

    # ==========================================================================
    # Callbacks
    # ==========================================================================
    
    def _on_click_start_timeline(self):
        async def start_scenario(model):
            timeline = omni.timeline.get_timeline_interface()
            if timeline.is_playing():
                timeline.stop()
                await omni.kit.app.get_app().next_update_async()
            model.set_default_translate()
            Attachment_Info.restart()
            omni.timeline.get_timeline_interface().play()

        run_loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(start_scenario(self.model), loop=run_loop)

    def _on_click_stop_timeline(self):
        async def stop_scenario():
            timeline = omni.timeline.get_timeline_interface()
            if timeline.is_playing():
                timeline.stop()
                await omni.kit.app.get_app().next_update_async()
            omni.timeline.get_timeline_interface().stop()

        run_loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(stop_scenario(), loop=run_loop)
