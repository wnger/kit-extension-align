__all__ = ["AlignWindow"]

# from .widget import AARelationshipEditWidget
from .align_model import AlignModel
from typing import List
import omni.ui as ui
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.relationship import RelationshipEditWidget, RelationshipTargetPicker
# from .style import scatter_window_style
# from .utils import get_selection
from .combo_box_model import ComboBoxModel
# from .scatter import scatter
# from .utils import duplicate_prims

from pxr import Usd, UsdShade, Sdf, Vt, Gf, UsdGeom, Trace

import omni.usd
import omni.kit.commands
from functools import partial
import weakref
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
LABEL_WIDTH = 120
SPACING = 4

class AlignWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)
        self.frame.set_build_fn(self._build_fn)
        self._usd_context_name = ''

        stage = self._get_context().get_stage()
        self._align_model = AlignModel(stage)
        self._combo_box_model = ComboBoxModel()
        self._target_prim_model = ui.SimpleStringModel()
        self.collection = ui.RadioCollection()
        self._extension_path = EXTENSION_FOLDER_PATH
        print('Ext path', EXTENSION_FOLDER_PATH)
        self._radioList = ["X","Y","Z","All"]

        # event_stream = omni.usd.get_context().get_stage_event_stream()
        # stage_event_sub = event_stream.create_subscription_to_pop(on_stage_event)
        usd_context = self._get_context()

        # Track selection changes
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Align object selection"
        )

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        # print('myEvent', event.type)
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()
            if len(selectedPrims) == 0:
                self._on_set_selection('')
                return

            if len(selectedPrims) > 1:
                print('Selection detecteds', selectedPrims[-1])
                self._on_set_selection(selectedPrims[-1])

    def destroy(self):
        # It will destroy all the children
        self._stage_event_sub = None
        super().destroy()

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    def _on_set_selection(self, prim):
        """Called when tthe user presses the "Get From Selection" button"""
        # return print('Set target prim', prim)
        self._target_prim_model.as_string = prim


    def _build_target_field(self):
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Target", name="target", width=self.label_width)
                # target_field = ui.StringField()
                ui.StringField(model=self._target_prim_model, read_only=True)

    def _build_button(self):
        
        def _align(weak_self):
            print('Align')
            selectedPrims = AlignModel.get_selection()
            if len(selectedPrims) < 2:
                return print('Not enough prims selected')

            weak_self = weak_self()
            faceVal = self._combo_box_model.get_item_value_model(None, None).as_int
            print('faceVal', faceVal)
            transVal = self.collection.model.as_int
            self._align_model.set_align(faceVal, transVal)
            return
            self._relationships = [stage.GetPrimAtPath(path).GetRelationship(rel_name) for path in prim_paths]
            for relationship in self._relationships:
                if relationship:
                    targets = relationship.GetTargets()
                    if len(targets) > 0:
                        target = targets[0]
                        print('Target', target)
                        oM = ObjectModel(stage, target)
                        oM.set_position()

        with ui.VStack(height=0, spacing=SPACING):
            ui.Button("Align(Window)", clicked_fn=partial(_align, weak_self=weakref.ref(self)))

    def _build_radio_buttons(self):
        style = {
            "": {"background_color": 0x0, "image_url": f"{self._extension_path}/icons/checkbox_off.svg"},
            ":checked": {"image_url": f"{self._extension_path}/icons/checkbox_on.svg"},
        }
        for k, v in enumerate(self._radioList):
            with ui.HStack(style=style):
                ui.RadioButton(radio_collection=self.collection, width=30, height=30)
                ui.Label(f"{v}", name="text")

    def _build_checkboxes(self):
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("X", name="x", width=20)
                checkboxX = ui.CheckBox()
                ui.Label("Y", name="y")
                checkboxY = ui.CheckBox()
                ui.Label("Z", name="z")
                checkboxZ = ui.CheckBox()
                ui.Label("All", name="xall")
                checkboxAll = ui.CheckBox()

    def _build_select(self, rel_name, attr_name, additional_widget_kwargs={}):
        """Build the widgets of the "Source" group"""
        metadata = None
        stage = self._get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print(attr_name, 'Stage', stage, 'paths', prim_paths)

        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Align To Target", name="attribute_name", width=self.label_width)
                # ui.ComboBox(1, "Center", "Top", "Bottom")
                ui.ComboBox(self._combo_box_model)
                # UsdPropertiesWidgetBuilder._create_label("Select Target", metadata, None)
                # AARelationshipEditWidget(stage, rel_name, attr_name, prim_paths, additional_widget_kwargs)
                
                # return RelationshipWidgetBuilder(stage, attr_name, metadata, prim_paths)
                # button = ui.Button(
                #     "Add Target(s)",
                #     width=ui.Pixel(30),
                #     clicked_fn=partial(on_add_target, weak_self=weakref.ref(self)),
                #     # enabled=True
                # )
            # ui.Button("Align(Window)", clicked_fn=partial(_align, weak_self=weakref.ref(self)))



    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        print('Rebuild window')
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_target_field()
                self._build_select('alignObject', 'alignObject')
                self._build_radio_buttons()
                # self._build_checkboxes()
                self._build_button()

                # The Go button
                # ui.Button("Align", clicked_fn=self._align)

    def update_window(self, window: ui.Window):
        self._window = window
        if self._render_view:
            self._render_view.update_window(window)
 