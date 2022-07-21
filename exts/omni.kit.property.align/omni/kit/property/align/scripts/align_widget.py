# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from ..widget import AARelationshipEditWidget
from ..object_model import ObjectModel
from typing import List
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.relationship import RelationshipEditWidget, RelationshipTargetPicker
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_HEIGHT, LABEL_WIDTH
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder

import copy
import carb
import omni.ui as ui
import omni.usd
from pxr import Usd, Sdf, Vt, Gf, UsdGeom, Trace
from functools import partial
import weakref



REL_NAME = 'alignObject'

class AlignWidget(UsdPropertiesWidget):
    def __init__(self):
        super().__init__(title="Align", collapsed=False)
        self._attribute_list = ["alignObject", "hovercraftWheels", "deafeningSilence", "randomOrder", "melancholyMerriment"]

    def on_new_payload(self, payload):
        """
        Called when a new payload is delivered. PropertyWidget can take this opportunity to update its ui models,
        or schedule full UI rebuild.

        Args:
            payload: The new payload to refresh UI or update model.

        Return:
            True if the UI needs to be rebuilt. build_impl will be called as a result.
            False if the UI does not need to be rebuilt. build_impl will not be called.
        """

        # nothing selected, so do not show widget. If you don't do this
        # you widget will be always on, like the path widget you see
        # at the top.
        if not payload or len(payload) == 0:
            return False

        # filter out special cases like large number of prim selected. As
        # this can cause UI stalls in certain cases
        if not super().on_new_payload(payload):
            return False

        # check is all selected prims are relevent class/types
        prims = []
        # for prim_path in self._payload:
        #     prim = self._get_prim(prim_path)
        #     if not prim or not (prim.IsA(UsdGeom.Xform) or prim.IsA(UsdGeom.Mesh)):
        #         return False
        #                         # for prim_path in prim_paths:
        #         #     print('myPrim', prim_path)
        #         #     prim = self._get_prim(prim_path)
        #         #     prim.CreateRelationship("alignPrim")
        #         #     targets = prim.GetRelationship("alignPrim").GetTargets()
        #         #     print('targets', targets)
        #     prim.CreateRelationship(REL_NAME)
            # prims.append(prim)

        # get list of attributes and build a dictonary to make logic simpler later
        self._placeholer_list = {}
        for prim in prims:
            for key in self._attribute_list:
                if prim.GetAttribute(key):
                    self._placeholer_list[key] = True

        return True

    def _customize_props_layout(self, attrs):
        """
        To reorder the properties display order, reorder entries in props list.
        To override display group or name, call prop.override_display_group or prop.override_display_name respectively.
        If you want to hide/add certain property, remove/add them to the list.

        NOTE: All above changes won't go back to USD, they're pure UI overrides.

        Args:
            props: List of Tuple(property_name, property_group, metadata)

        Example:

            for prop in props:
                # Change display group:
                prop.override_display_group("New Display Group")

                # Change display name (you can change other metadata, it won't be write back to USD, only affect UI):
                prop.override_display_name("New Display Name")

            # add additional "property" that doesn't exist.
            props.append(UsdPropertyUiEntry("PlaceHolder", "Group", { Sdf.PrimSpec.TypeNameKey: "bool"}, Usd.Property))
        """
        from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty

        # custom UI builder
        def mm_build_fn(
            stage,
            attr_name,
            metadata,
            property_type,
            prim_paths: List[Sdf.Path],
            additional_label_kwargs={},
            additional_widget_kwarg={},
        ):
            def create_attr():
                self._placeholer_list["melancholyMerriment"] = True
                for prim_path in prim_paths:
                    prim = self._get_prim(prim_path)
                    attr = prim.CreateAttribute("melancholyMerriment", Sdf.ValueTypeNames.Float3, False)
                    attr.Set(Gf.Vec3f(1.0, 1.0, 1.0))
                    attr.SetMetadata("customData", {"default": Gf.Vec3f(1.0, 1.0, 1.0)})

            with ui.HStack(spacing=HORIZONTAL_SPACING):
                UsdPropertiesWidgetBuilder._create_label("Melancholy Merriment")
                ui.Button("Create \"Melancholy Merriment\"", clicked_fn=create_attr)

        # custom UI builder
        def mm_build_align_fn(
            stage,
            attr_name,
            metadata,
            property_type,
            prim_paths: List[Sdf.Path],
            additional_label_kwargs={},
            additional_widget_kwargs={},
        ):
            def create_align_attr(weak_self):
                weak_self = weak_self()
                self._placeholer_list["alignObject"] = True
                self._relationships = [stage.GetPrimAtPath(path).GetRelationship(REL_NAME) for path in prim_paths]
                for relationship in self._relationships:
                    if relationship:
                        targets = relationship.GetTargets()
                        if len(targets) > 0:
                            target = targets[0]
                            print('Target', target)
                            # oM = ObjectModel(stage, target)
                            # oM.set_position()
                            # pos = stage.GetPrimAtPath(target)
                            # print('Target prim', prim)

            print('prim_paths', prim_paths)
            with ui.VStack(height=0, spacing=HORIZONTAL_SPACING):
                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    UsdPropertiesWidgetBuilder._create_label("Select Target", metadata, None)
                    AARelationshipEditWidget(stage, REL_NAME, attr_name, prim_paths, additional_widget_kwargs)
                    # return RelationshipWidgetBuilder(stage, attr_name, metadata, prim_paths)
                    # button = ui.Button(
                    #     "Add Target(s)",
                    #     width=ui.Pixel(30),
                    #     clicked_fn=partial(on_add_target, weak_self=weakref.ref(self)),
                    #     # enabled=True
                    # )
                ui.Button("Align(Property)", clicked_fn=partial(create_align_attr, weak_self=weakref.ref(self)))

        # As these attributes are not part of the schema, placeholders need to be added. These are not
        # part of the prim until the value is changed. They will be added via prim.CreateAttribute(
        # This is also the reason for _placeholer_list as we don't want to add placeholders if valid
        # attribute already exists

        # NOTE: As these are not part of the schema and "default value" logic is not finialized yet
        # so resetting hovercraftWheels is weird as it gets reset to "True" and not one of the
        # item in the list.

        print('List', self._placeholer_list)
        # if not "alignObject" in self._placeholer_list:
        #     attrs.append(
        #         UsdPropertyUiEntry(
        #             "alignObject",
        #             "",
        #             {
        #                 Sdf.PrimSpec.TypeNameKey: "token",
        #                 "allowedTokens": Vt.TokenArray(3, ("None", "Square", "Round", "Triangle")),
        #                 "customData": {"default": "Round"},
        #             },
        #             Usd.Attribute,
        #         )
        #     )

        # insert placeholder attributes
        if not "hovercraftWheels" in self._placeholer_list:
            attrs.append(
                UsdPropertyUiEntry(
                    "hovercraftWheels",
                    "",
                    {
                        Sdf.PrimSpec.TypeNameKey: "token",
                        "allowedTokens": Vt.TokenArray(3, ("None", "Square", "Round", "Triangle")),
                        "customData": {"default": "Round"},
                    },
                    Usd.Attribute,
                )
            )


        if not "deafeningSilence" in self._placeholer_list:
            attrs.append(
                UsdPropertyUiEntry(
                    "deafeningSilence",
                    "",
                    {
                        Sdf.PrimSpec.TypeNameKey: "float",
                        "customData": {"default": 1}
                    },
                    Usd.Attribute,
                )
            )
        if not "randomOrder" in self._placeholer_list:
            attrs.append(
                UsdPropertyUiEntry(
                    "randomOrder",
                    "",
                    {Sdf.PrimSpec.TypeNameKey: "bool", "customData": {"default": False}},
                    Usd.Attribute,
                )
            )

        # remove any unwanted attrs (all of the Xform & Mesh
        # attributes as we don't want to display them in the widget)
        for attr in copy.copy(attrs):
            if not attr.attr_name in self._attribute_list:
                attrs.remove(attr)

        print("Attrs", attrs)
        # custom UI attributes
        frame = CustomLayoutFrame(hide_extra=False)
        with frame:
            if not "melancholyMerriment" in self._placeholer_list:
                # this uses a custom ui build function
                CustomLayoutProperty(None, None, build_fn=mm_build_fn)

            # if not "alignObject" in self._placeholer_list:
            #     # this uses a custom ui build function
            #     CustomLayoutProperty(None, None, build_fn=mm_build_align_fn)
            # Set layout order. this re-aranges attributes in widget to the following order,
            # any attributes that don't exist are not displayed. Which is why you don't see
            # "Create Melancholy Merriment" button and triple-float value together
            
            CustomLayoutProperty("melancholyMerriment", "Melancholy Merriment")
            CustomLayoutProperty("alignObject", "Select Target", build_fn=mm_build_align_fn)
            CustomLayoutProperty("hovercraftWheels", "Hovercraft Wheels")
            CustomLayoutProperty("deafeningSilence", "Deafening Silence")
            # CustomLayoutProperty("randomOrder", "Random Order")

        return frame.apply(attrs)


    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        """
        called when UsdPropertiesWidget needs to inform of a property change
        NOTE: This is a Tf.Notice.Register(Usd.Notice.ObjectsChanged) callback, so is time sensitive function
              Keep code in this function to a minimum as heavy work can slow down kit
        """
        if stage != self._payload.get_stage():
            return

        super()._on_usd_changed(notice=notice, stage=stage)

        # check for attribute changed or created by +add menu as widget refresh is required
        for path in notice.GetChangedInfoOnlyPaths():
            if path.name in self._attribute_list:
                # on_new_payload will not be called so need to update _placeholer_list
                # to prevent placeholders & real attributes being displayed
                self._placeholer_list[path.name] = True
                self.request_rebuild()