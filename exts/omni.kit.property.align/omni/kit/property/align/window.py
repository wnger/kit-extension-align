__all__ = ["AlignWindow"]

# from .widget import AARelationshipEditWidget
from .align_model import AlignModel
from typing import List
import omni.ui as ui
from omni.ui import scene as sc
# from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
# from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
# from omni.kit.property.usd.relationship import RelationshipEditWidget, RelationshipTargetPicker
# from .style import scatter_window_style
# from .utils import get_selection
from .checkbox_model import CheckboxModel
from .combo_box_model import ComboBoxModel
# from .scatter import scatter
# from .utils import duplicate_prims

from pxr import Usd, UsdShade, Sdf, Vt, Gf, UsdGeom, Trace

import omni.usd
import omni.kit.commands
from functools import partial
import weakref
import pathlib

from .style import align_model_style

DEFAULT_TAB = 'Transform'
REL_NAME = 'alignPrim'
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
        # self._scene_view = sc.SceneView()
        self.frame.style = align_model_style
        self.frame.set_build_fn(self._build_fn)
        

        self._property_sub = None

        stage = self._get_context().get_stage()
        self._align_model = AlignModel(stage)

        self._combo_box_model = ComboBoxModel()
        # self._combo_box_model.add_item_changed_fn(self._on_combo_value_changed)

        self._model_x = ui.AbstractItemModel()
        self._tabList = ['Transform', 'Rotate', 'Scale']
        self._tabVal = self._tabList[0]

        self._target_prim_model = ui.SimpleStringModel()
        self.collection = ui.RadioCollection()
        self._extension_path = EXTENSION_FOLDER_PATH
        print('Ext path', EXTENSION_FOLDER_PATH)
        self._radioList = ["X","Y","Z","All"]
        


    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _on_change_info_path(self, changed_path):
        print('Changed path', changed_path)
        self.frame.rebuild()

    # def _on_new_payload(self, prim_path):
    #     print('onPayload', prim_path)
    #     prim = self._get_context().get_stage().GetPrimAtPath(prim_path)
    #     prim.CreateRelationship(REL_NAME)
    #     self.frame.rebuild()

    def destroy(self):
        # It will destroy all the children
        # self._stage_event_sub = None
        # self._property_sub = None
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

    # def _on_set_selection(self, prim):
    #     """Called when tthe user presses the "Get From Selection" button"""
    #     # return print('Set target prim', prim)
    #     self._target_prim_model.as_string = prim

    def _on_combo_value_changed(self, model, item):
        """Set revert_img to correct state."""
        print('Combo changed', model, item, model.get_item_value_model(None, None).as_int)

    def _get_prims(self):
        prims = omni.usd.get_context().get_selection().get_selected_prim_paths()
        return prims

    def selectTab(self, button):
        print('buttonCLicked', button.text)
        if self._tabVal == button.text:
            return

        self._tabVal = button.text
        self.frame.rebuild()


    def _build_label_message(self):
        self._tabVal = DEFAULT_TAB
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label(self._errorMsg, name="error",  alignment=ui.Alignment.CENTER)

    def _build_target_field(self, prim):
        self._target_prim_model.as_string = prim
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(style={"margin":0}, spacing=SPACING):
                ui.Label("Target", name="target", width=self.label_width)
                # target_field = ui.StringField()
                ui.StringField(model=self._target_prim_model, read_only=True)

    def _build_tabs(self):
        print('Build tabs', self._tabVal)
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(style={"margin":0}, spacing=0):
                
                # tabTransform = ui.Button("Transform", spacing=0)
                # tabRotate = ui.Button("Rotate", spacing=0)
                # tabScale = ui.Button("Scale", spacing=0)
                for tVal in self._tabList:
                    tabStyle = {}
                    if self._tabVal == tVal:
                        tabStyle = {
                            "Button": {
                                "background_color": 0xFF76b900
                            }
                        }
                    tab = ui.Button(tVal, style=tabStyle, spacing=0)
                    tab.set_clicked_fn(
                        lambda t=tab: self.selectTab(t))

                # tabTransform.set_clicked_fn(
                # lambda t=tabTransform: self.selectTab(t))

    def _build_align_select(self):
        if self._tabVal != 'Transform':
            return

        print('Build align select')
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Align To Target", name="align-face", width=self.label_width)
                # ui.ComboBox(1, "Center", "Top", "Bottom")
                # self._combo_box_model.add_item_changed_fn(self._on_combo_value_changed)
                ui.ComboBox(self._combo_box_model)
                
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
        style = {
            "": {"background_color": 0x0, "image_url": f"{self._extension_path}/icons/checkbox_off.svg"},
            ":checked": {"image_url": f"{self._extension_path}/icons/checkbox_on.svg"},
        }
        with ui.VStack(height=0, spacing=SPACING):
                
            with ui.HStack(spacing=SPACING, style=style):
                # self._checkboxX
                
                ui.Label(f"Align {self._tabVal}", width=self.label_width)
                # ui.Spacer(spacing=100)

                # CheckboxModel(label="Y", default_value=True)
                # CheckboxModel(label="Z", default_value=True)
                # checkboxX = ui.CheckBox(label="CheckboxX")
                # ui.Label("Y", name="y")
                # checkboxY = ui.CheckBox()
                # checkboxZ = ui.CheckBox()
                # ui.Label("All", name="xall")
                self._checkboxX = CheckboxModel(label="X", model=self._model_x, default_value=True)
                self._checkboxY = CheckboxModel(label="Y", default_value=True)
                self._checkboxZ = CheckboxModel(label="Z", default_value=True) 
                
    def _build_select(self, rel_name, attr_name, additional_widget_kwargs={}):
        """Build the widgets of the "Source" group"""


        metadata = None
        stage = self._get_context().get_stage()
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print(attr_name, 'Stage', stage, 'paths', prim_paths)

        # self._relationships = [stage.GetPrimAtPath(path).GetRelationship(rel_name) for path in prim_paths]

        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Align To Target", name="attribute_name", width=self.label_width)
                # ui.ComboBox(1, "Center", "Top", "Bottom")
                self._combo_box_model.add_item_changed_fn(self._on_combo_value_changed)
                ui.ComboBox(self._combo_box_model)
            
                # UsdPropertiesWidgetBuilder._create_label("Select Target", metadata, None)
                # AARelationshipEditWidget(stage, rel_name, attr_name, prim_paths, additional_widget_kwargs)
                # print('attrName', attr_name)
                # if self._property_sub is None and len(prim_paths) > 0:
                #     self._property_sub = omni.usd.get_watcher().subscribe_to_change_info_path(f"{prim_paths[0]}.{attr_name}", self._on_change_info_path)
                

    def _build_button(self):
        
        def _align():
            print('Align')
            # self._on_change_info_path('haha')
            # if len(self._selectedPrims) < 1:
            #     return print('Not enough prims selected')



            xVal = self._checkboxX.get_item_value_model()
            yVal = self._checkboxY.get_item_value_model()
            zVal = self._checkboxZ.get_item_value_model()

            transVal = [xVal, yVal, zVal]
            if transVal == [False, False, False]:
                return print('None selected')
                
            # print('tabVal', self._tabVal)
            faceVal = self._combo_box_model.get_item_value_model(None, None).as_int
            # print('faceVal', faceVal)

            self._align_model.set_align(self._tabVal, faceVal, transVal)

            # self._relationships = [stage.GetPrimAtPath(path).GetRelationship(rel_name) for path in prim_paths]
            # for relationship in self._relationships:
            #     if relationship:
            #         targets = relationship.GetTargets()
            #         if len(targets) > 0:
            #             target = targets[0]
            #             print('Target', target)
            #             oM = ObjectModel(stage, target)
            #             oM.set_position()

        with ui.VStack(height=0, spacing=SPACING):
            ui.Button("Apply", clicked_fn=partial(_align))

    def _validate_prims(self):
        if len(self._selectedPrims) < 2:
            self._errorMsg = 'Not enough prims selected'
            return False

        # Get target prim
        targetPrimPath = self._selectedPrims[-1]
        targetPrim = self._get_context().get_stage().GetPrimAtPath(targetPrimPath)
        targetParent = targetPrim.GetParent()
        targetChildren = targetPrim.GetChildren()
        # print('targetPrim', targetPrimPath)
        # print('targetParent', targetParent, targetParent.IsPseudoRoot())
        # print('targetChildren', targetChildren)
        # print('children', prim.GetChildren())
        for primPath in self._selectedPrims:

            prim = self._get_context().get_stage().GetPrimAtPath(primPath)

            if prim.HasProperty('visibility') == False:
                self._errorMsg = 'Invalid prim(s) selected'
                return False
            
            if prim in targetChildren:
                self._errorMsg = 'Unable to align to parent object'
                return False

            if targetParent:
                if prim == targetParent:
                    self._errorMsg = 'Unable to align to child object'
                    return False

                primParent = prim.GetParent()
                if primParent and primParent != targetParent:
                    self._errorMsg = 'Selected objects are of different parent'
                    return False

        return True
                

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        self._selectedPrims = self._get_prims()
        print('Rebuild window')
        


        with ui.ScrollingFrame(name="window_bg",
                               horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(style={"margin":1}, height=0):

                if self._validate_prims() == False:
                    self._build_label_message()
                else:
                    self._build_target_field(self._selectedPrims[-1])
                    # self._build_select(REL_NAME, REL_NAME)
                    self._build_tabs()
                    self._build_checkboxes()
                    self._build_align_select()
                    self._build_button()

                # self._build_align_select()

                # The Go button
                # ui.Button("Align", clicked_fn=self._align)
 