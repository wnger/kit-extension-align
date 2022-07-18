import os
import carb
import omni.ext
from pxr import Sdf, Usd, UsdGeom, Gf
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload


class AlignPropertyExtension(omni.ext.IExt):
    def __init__(self):
        self._registered = False
        self._menu_items = []

    def on_startup(self, ext_id):
        self._register_widget()
        # self._register_add_menus()

    def on_shutdown(self):
        # self._unregister_add_menus()
        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as property_window_ext
        from .align_widget import AlignWidget

        property_window = property_window_ext.get_window()
        if property_window:
            # register ExampleAttributeWidget class with property window.
            # you can have multple of these but must have to be different scheme names
            # but always "prim" or "layer" type
            #   "prim" when a prim is selected
            #   "layer" only seen when root layer is selected in layer window
            property_window.register_widget("prim", "align_properties", AlignWidget())
            self._registered = True
            # ordering of property widget is controlled by omni.kit.property.bundle

    def _unregister_widget(self):
        import omni.kit.window.property as property_window_ext

        property_window = property_window_ext.get_window()
        if property_window:
            # remove ExampleAttributeWidget class with property window
            property_window.unregister_widget("prim", "align_properties")
            self._registered = False

    def _register_add_menus(self):
        from omni.kit.property.usd import PrimPathWidget

        # add menus to property window path/+add and context menus +add submenu.
        # show_fn: controls when option will be shown, IE when selected prim(s) are Xform or Mesh.
        # onclick_fn: is called when user selects menu item.
        # self._menu_items.append(
        #     PrimPathWidget.add_button_menu_entry(
        #         "Example/Hovercraft Wheels",
        #         show_fn=AlignPropertyExtension.prim_is_example_type,
        #         onclick_fn=AlignPropertyExtension.click_add_hovercraft_wheels
        #     )
        # )
        #
        # self._menu_items.append(
        #     PrimPathWidget.add_button_menu_entry(
        #         "Example/Deafening Silence",
        #         show_fn=AlignPropertyExtension.prim_is_example_type,
        #         onclick_fn=AlignPropertyExtension.click_add_deafening_silence
        #     )
        # )


        # self._menu_items.append(
        #     PrimPathWidget.add_button_menu_entry(
        #         "Example/Melancholy Merriment",
        #         show_fn=AlignPropertyExtension.prim_is_example_type,
        #         onclick_fn=AlignPropertyExtension.click_add_melancholy_merriment
        #     )
        # )

    def _unregister_add_menus(self):
        from omni.kit.property.usd import PrimPathWidget

        # remove menus to property window path/+add and context menus +add submenu.
        for item in self._menu_items:
            PrimPathWidget.remove_button_menu_entry(item)

        self._menu_items = None

    @staticmethod
    def prim_is_example_type(objects: dict) -> bool:
        """
        checks if prims are required type
        """
        if not "stage" in objects or not "prim_list" in objects or not objects["stage"]:
            return False

        stage = objects["stage"]
        if not stage:
            return False

        prim_list = objects["prim_list"]
        for path in prim_list:
            if isinstance(path, Usd.Prim):
                prim = path
            else:
                prim = stage.GetPrimAtPath(path)
            if prim:
                if not (prim.IsA(UsdGeom.Xform) or prim.IsA(UsdGeom.Mesh)):
                    return False

        return len(prim_list) > 0

    @staticmethod
    def click_add_hovercraft_wheels(payload: PrimSelectionPayload):
        """
        create hovercraftWheels Prim.Attribute
        """
        stage = payload.get_stage()
        # for prim_path in payload:
        #     prim = stage.GetPrimAtPath(prim_path) if stage and prim_path else None
        #     if prim:
        #         attr = prim.CreateAttribute("hovercraftWheels",  Sdf.ValueTypeNames.Token, False)
        #         attr.SetMetadata("allowedTokens", ["None", "Square", "Round", "Triangle"])
        #         attr.Set("Round")

    @staticmethod
    def click_add_deafening_silence(payload: PrimSelectionPayload):
        """
        create deafeningSilence Prim.Attribute
        """
        stage = payload.get_stage()
        for prim_path in payload:
            prim = stage.GetPrimAtPath(prim_path) if stage and prim_path else None
            if prim:
                attr = prim.CreateAttribute("deafeningSilence",  Sdf.ValueTypeNames.Float, False)
                attr.Set(1.0)

    @staticmethod
    def click_add_random_order(payload: PrimSelectionPayload):
        """
        create randomOrder Prim.Attribute
        """
        stage = payload.get_stage()
        for prim_path in payload:
            prim = stage.GetPrimAtPath(prim_path) if stage and prim_path else None
            if prim:
                attr = prim.CreateAttribute("randomOrder",  Sdf.ValueTypeNames.Bool, False)
                attr.Set(False)

    @staticmethod
    def click_add_melancholy_merriment(payload: PrimSelectionPayload):
        """
        create melancholyMerriment Prim.Attribute
        """
        stage = payload.get_stage()
        for prim_path in payload:
            prim = stage.GetPrimAtPath(prim_path) if stage and prim_path else None
            if prim:
                attr = prim.CreateAttribute("melancholyMerriment", Sdf.ValueTypeNames.Float3, False)
                attr.Set(Gf.Vec3f(1.0, 1.0, 1.0))
