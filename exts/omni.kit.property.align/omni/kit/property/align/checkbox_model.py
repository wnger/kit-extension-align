__all__ = ["CheckboxModel"]

from typing import Optional
import omni.ui as ui
from .style import ATTR_LABEL_WIDTH

class CheckboxModel(ui.AbstractItemModel):
    def __init__(self,
                 model: ui.AbstractItemModel = None,
                 default_value: bool = True,
                 **kwargs):
        super().__init__()
        self.existing_model: Optional[ui.AbstractItemModel] = kwargs.pop("model", None)
        self.revert_img = None
        self.__attr_label: Optional[str] = kwargs.pop("label", "")
        self.__frame = ui.Frame()
        self.__default_val = default_value
        self.__bool_image = None
        with self.__frame:
            self._build_fn()

    def destroy(self):
        self.existing_model = None
        self.revert_img = None
        self.__attr_label = None
        self.__frame = None
        self.__bool_image = None

    def __getattr__(self, attr):
        """Pretend it's self.__frame, so we have access to width/height and
        callbacks.
        """
        return getattr(self.__frame, attr)

    def get_item_value_model(self):
        return self.__bool_image.checked

    def _on_value_changed(self):
        """Swap checkbox images and set revert_img to correct state."""
        
        self.__bool_image.checked = not self.__bool_image.checked
        print('Checked', self.__attr_label, self.__bool_image.checked)
        self.__bool_image.name = (
            "checked" if self.__bool_image.checked else "unchecked"
        )
        # self.revert_img.enabled = self.__default_val != self.__bool_image.checked

    def _build_head(self):
        """Build the left-most piece of the widget line (label in this case)"""
        # ui.Spacer()
        ui.Label(
            self.__attr_label,
            name="attribute_name",
            width=ATTR_LABEL_WIDTH
        )

    def _build_body(self):
        """Build the custom part of the widget. Most custom widgets will
        override this method, as it is where the meat of the custom widget is.
        """
        """Main meat of the widget.  Draw the appropriate checkbox image, and
        set up callback.
        """
        with ui.HStack(style={'alignment':ui.Alignment.RIGHT}):
            
            self.__bool_image = ui.Image(
                name="checked" if self.__default_val else "unchecked",
                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                height=16, width=16, checked=self.__default_val
            )
            ui.Spacer()
            
            # with ui.VStack(style={'alignment':ui.Alignment.RIGHT}):
            #     # Just shift the image down slightly (2 px) so it's aligned the way
            #     # all the other rows are.
            #     ui.Spacer(height=2)
            #     self.__bool_image = ui.Image(
            #         name="checked" if self.__default_val else "unchecked",
            #         fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
            #         height=16, width=16, checked=self.__default_val
            #     )
            # # Let this spacer take up the rest of the Body space.
            # ui.Spacer()

        self.__bool_image.set_mouse_pressed_fn(
            lambda x, y, b, m: self._on_value_changed())

    def _build_tail(self):
        """Build the right-most piece of the widget line. In this case,
        we have a Revert Arrow button at the end of each widget line.
        """
        with ui.HStack(width=0):
            ui.Spacer(width=5)
            with ui.VStack(height=0):
                ui.Spacer(height=3)
                # self.revert_img = ui.Image(
                #     name="revert_arrow",
                #     fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                #     width=12,
                #     height=13,
                #     enabled=False,
                # )
            ui.Spacer(width=5)

        # call back for revert_img click, to restore the default value
        # self.revert_img.set_mouse_pressed_fn(
        #     lambda x, y, b, m: self._restore_default())

    def _build_fn(self):
        """Puts the 3 pieces together."""
        with ui.HStack(style={'alignment':ui.Alignment.RIGHT}):
            self._build_head()
            self._build_body()
            # self._build_tail()
