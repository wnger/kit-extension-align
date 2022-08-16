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
        self.checkboxes = {
            'X': None,
            'Y': None,
            'Z': None
        }
        # self.Y = None
        # self.Z = None
        print('Kwarfs', self.__attr_label, kwargs)
        self._style = {}
        
        
        if bool(kwargs):
            self._style = kwargs['style']
            self._tabVal = kwargs['tabVal']
            
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

    def setCheckbox(self, checkboxes):
        '''Turn on the model and turn off two checkboxes'''
        for c in checkboxes:
            self.checkboxes[c.__attr_label] = c

    def get_item_value_model(self):
        return self.__bool_image.checked

    def _on_value_changed(self):
        print('Checkbox val change', self.__attr_label)
        print('checked', self.__bool_image.checked)
        """Swap checkbox images and set revert_img to correct state."""


        if self._tabVal == 'Scale' and self.__bool_image.checked:
            return

        self.__bool_image.checked = not self.__bool_image.checked
        
        name = "checked" if self.__bool_image.checked else "unchecked"
        name += '-'+self.__attr_label
        self.__bool_image.name = (
            name
        )

        if self._tabVal == 'Scale' and self.__bool_image.checked:
            for c in self.checkboxes:
                if c != self.__attr_label:
                    self.checkboxes[c].__bool_image.checked = False
                    self.checkboxes[c].__bool_image.name = 'unchecked-'+self.checkboxes[c].__attr_label

    def _build_head(self):
        """Build the left-most piece of the widget line (label in this case)"""
        # ui.Spacer()
        ui.Label(
            self.__attr_label,
            name="attribute_name",
            width=ATTR_LABEL_WIDTH,
            style=self._style
        )

    def _build_body(self):
        """Build the custom part of the widget. Most custom widgets will
        override this method, as it is where the meat of the custom widget is.
        """
        """Main meat of the widget.  Draw the appropriate checkbox image, and
        set up callback.
        """
        with ui.HStack(style={'alignment':ui.Alignment.RIGHT, 'margin_height': 0, 'margin_width': 1}):
            name = "checked" if self.__default_val else "unchecked"
            name += '-'+self.__attr_label
            self.__bool_image = ui.Image(
                name = name,
                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                height=20, width=20, checked=self.__default_val
            )
            ui.Spacer()
            
        self.__bool_image.set_mouse_pressed_fn(
            lambda x, y, b, m: self._on_value_changed())

    def _build_fn(self):
        """Puts the 3 pieces together."""
        with ui.HStack(style={'alignment':ui.Alignment.RIGHT}):
            self._build_head()
            self._build_body()
