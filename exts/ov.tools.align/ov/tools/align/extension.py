__all__ = ["AlignWindowExtension"]
from .window import AlignWindow
from functools import partial
import asyncio

import omni.ext
import omni.ui as ui
from omni import usd as _usd
from pxr import Usd

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AlignWindowExtension(omni.ext.IExt):

    WINDOW_NAME = "Align"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id: str):
        print("[omni.kit.property.align] AlignExtension startup", ext_id)
        self._window = None

        ui.Workspace.set_show_window_fn(AlignWindowExtension.WINDOW_NAME, partial(self.show_window, None))
        ui.Workspace.show_window(AlignWindowExtension.WINDOW_NAME)
        
        # # Put the new menu
        editor_menu = omni.kit.ui.get_editor_menu()
        
        if editor_menu:
            self._menu = editor_menu.add_item(
                AlignWindowExtension.MENU_PATH, self.show_window, toggle=True, value=True
            )

        self._context = _usd.get_context()
        self._subscription = self._context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="Object Selection"
        )
    
    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(AlignWindowExtension.MENU_PATH, value)
# 
    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED) and self._window.frame:
            print('Stage event', event.type)
            self._window.frame.rebuild()

    def on_shutdown(self):
        print("[omni.kit.property.align] AlignExtension shutdown")
        if self._subscription:
            self._subscription = None

        if self._menu:
            self._menu = None

        if self._window:
            self._window.destroy()

        self._window = None
        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(AlignWindowExtension.WINDOW_NAME, None)
            
    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = AlignWindow(AlignWindowExtension.WINDOW_NAME, width=300, height=200)
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        else:
            if self._window:
                self._window.visible = False
