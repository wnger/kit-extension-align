from .window import AlignWindow
from functools import partial
import asyncio
import omni.ext
import omni.ui as ui

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class AlignWindowExtension(omni.ext.IExt):

    ALIGN_WINDOW_NAME = "Align Tool"
    ALIGN_MENU_PATH = f"Window/{ALIGN_WINDOW_NAME}"

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.kit.property.align] AlignExtension startup")

        self._window = ui.Window(AlignWindowExtension.ALIGN_WINDOW_NAME, width=300, height=300)
        ui.Workspace.set_show_window_fn(AlignWindowExtension.ALIGN_WINDOW_NAME, partial(self.show_window, None))
        ui.Workspace.show_window(AlignWindowExtension.ALIGN_WINDOW_NAME)

        # Put the new menu
        editor_menu = omni.kit.ui.get_editor_menu()
        print('myMenu', editor_menu)
        # if editor_menu:
        #     # self._menu = editor_menu.add_item(
        #     #     AlignWindowExtension.ALIGN_MENU_PATH, self.show_window, toggle=True, value=True
        #     # )
        # with self._window.frame:
        #     with ui.VStack():
        #         ui.Label("Some Label")

        #         def on_click():
        #             print("clicked!")

        #         ui.Button("Click Me", clicked_fn=lambda: on_click())
    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(AlignWindowExtension.ALIGN_MENU_PATH, value)

    def on_shutdown(self):
        print("[omni.kit.property.align] AlignExtension shutdown")
        self._menu = None
        if self._window:
            self._window.destroy()
            self._window = None

        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(AlignWindowExtension.ALIGN_WINDOW_NAME, None)

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
            self._window = AlignWindow(AlignWindowExtension.ALIGN_WINDOW_NAME, width=300, height=300)
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False
