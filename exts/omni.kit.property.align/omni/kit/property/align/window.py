__all__ = ["AlignWindow"]

# from .widget import AARelationshipEditWidget
from .align_model import AlignModel
from typing import List
import omni.ui as ui
from .checkbox_model import CheckboxModel
from .combo_box_model import ComboBoxModel
from pxr import Usd, UsdShade, Sdf, Vt, Gf, UsdGeom, Trace

import omni.usd
import omni.kit.commands
from functools import partial
import weakref
import pathlib

from .style import align_model_style, v_style, EXTENSION_FOLDER_PATH, VHEIGHT

DEFAULT_TAB = 'Transform'
LABEL_WIDTH = 120
SPACING = 4

class AlignWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        self.frame.style = align_model_style
        self.frame.set_build_fn(self._build_fn)
        
        stage = self._get_context().get_stage()
        self._align_model = AlignModel(stage)

        # self._combo_box_model.add_item_changed_fn(self._on_combo_value_changed)
        self._tabList = ['Transform', 'Rotate', 'Scale']
        self._tabVal = self._tabList[0]

        self._target_prim_model = ui.SimpleStringModel()
        self._extension_path = EXTENSION_FOLDER_PATH
        
    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def destroy(self):
        # It will destroy all the children
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

    def _get_prims(self):
        prims = omni.usd.get_context().get_selection().get_selected_prim_paths()
        return prims

    def selectTab(self, button):
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
        with ui.VStack(spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Target", name="target", width=self.label_width)
                ui.StringField(model=self._target_prim_model, read_only=True)

    def _build_tabs(self):
        with ui.VStack(style=v_style, spacing=SPACING):
            with ui.HStack(style={"margin":0}, spacing=SPACING):
                for tVal in self._tabList:
                    tabStyle = {}
                    # Active tab
                    if self._tabVal == tVal:
                        tabStyle = {
                            "Button": {
                                "background_color": 0xFF777777
                            }
                        }
                    tab = ui.Button(tVal, style=tabStyle, spacing=0)
                    tab.set_clicked_fn(
                        lambda t=tab: self.selectTab(t))

    def _build_align_select(self):

        # Show align selection only on transform
        if self._tabVal != 'Transform':
            return

        self._combo_box_model = ComboBoxModel()
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Label("Align To Target", name="align-face", width=self.label_width)
                ui.ComboBox(self._combo_box_model)
                

    def _build_checkboxes(self):
        with ui.VStack(height=0, spacing=SPACING):
            with ui.HStack():
                ui.Label(f"Align {self._tabVal}", width=self.label_width)

                # Only check X axis if scale selected
                xVal = True if self._tabVal == 'Scale' else True
                yVal = False if self._tabVal == 'Scale' else True
                zVal = False if self._tabVal == 'Scale' else True

                self._checkboxX = CheckboxModel(label="X", default_value=xVal, tabVal=self._tabVal, style={"color": 0xFF6060AA})
                self._checkboxY = CheckboxModel(label="Y", default_value=yVal, tabVal=self._tabVal, style={"color": 0xFF76A371})
                self._checkboxZ = CheckboxModel(label="Z", default_value=zVal, tabVal=self._tabVal, style={"color": 0xFFA07D4F}) 

                # Connect other checkboxes
                self._checkboxX.setCheckbox([self._checkboxY, self._checkboxZ])
                self._checkboxY.setCheckbox([self._checkboxX, self._checkboxZ])
                self._checkboxZ.setCheckbox([self._checkboxX, self._checkboxY])

                
    def _build_button(self):
        
        def _align():

            xVal = self._checkboxX.get_item_value_model()
            yVal = self._checkboxY.get_item_value_model()
            zVal = self._checkboxZ.get_item_value_model()

            # No axis selected
            if xVal == yVal == zVal == False:
                return print('None selected')
            
            transVal = [xVal, yVal, zVal]

            # Get combo box value
            faceVal = self._combo_box_model.get_item_value_model(None, None).as_int

            self._align_model.set_align(self._tabVal, faceVal, transVal)

        with ui.VStack(height=35, style={"margin_height": 1.5}):
            ui.Button("Apply", clicked_fn=partial(_align))

    def _validate_prims(self):
        if len(self._selectedPrims) < 2:
            self._errorMsg = 'Not enough objects selected'
            return False

        # Get target prim, which is last selected item
        targetPrimPath = self._selectedPrims[-1]
        targetPrim = self._get_context().get_stage().GetPrimAtPath(targetPrimPath)

        # Get target parent if any
        targetParent = targetPrim.GetParent()
        targetChildren = targetPrim.GetChildren()
        
        for primPath in self._selectedPrims:

            prim = self._get_context().get_stage().GetPrimAtPath(primPath)

            # Ensure only transformable items are selected
            if prim.HasProperty('xformOp:translate') == False:
                self._errorMsg = 'Invalid object(s) selected'
                return False
            
            # Ensure selected items are on the same hierarchy
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
        
        with ui.VStack(style=v_style, height=0):

            if self._validate_prims() == False:
                self._build_label_message()
            else:
                self._build_target_field(self._selectedPrims[-1])
                self._build_tabs()
                self._build_checkboxes()
                self._build_align_select()
                self._build_button()
 