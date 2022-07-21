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

# REL_NAME = 'alignObject'

class AARelationshipEditWidget:
    def __init__(self, stage, rel_name, attr_name, prim_paths, additional_widget_kwargs=None):
        self._relationships = [stage.GetPrimAtPath(path).GetRelationship(rel_name) for path in prim_paths]
        
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self._targets_limit = 1
        self._button = None
        self._target_picker = RelationshipTargetPicker(
            stage,
            self,
            self._additional_widget_kwargs.get("target_picker_filter_type_list", []),
            self._additional_widget_kwargs.get("target_picker_filter_lambda", None),
            self._additional_widget_kwargs.get("target_picker_on_add_targets", None),
        )
        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)
        self._on_remove_target = self._additional_widget_kwargs.get("on_remove_target", None)
        self._enabled = self._additional_widget_kwargs.get("enabled", True)

    def clean(self):
        self._target_picker.clean()
        self._target_picker = None
        self._frame = None
        self._button = None
        self._label = None
        self._on_remove_target = None
        self._enabled = True

    def _build(self):
        self.shared_targets = None
        print('mySelfRelationships', self._relationships)
        for relationship in self._relationships:
            targets = relationship.GetTargets()
            print('Targets', targets)
            if self.shared_targets is None:
                self.shared_targets = targets
            elif self.shared_targets != targets:
                self.shared_targets = None
                break

        with ui.VStack(spacing=2):
            if self.shared_targets is not None:
                for target in self.shared_targets:
                    with ui.HStack(spacing=2):
                        ui.StringField(name="models", read_only=True).model.set_value(target.pathString)

                        def on_remove_target(weak_self, target):
                            weak_self = weak_self()
                            print('Remove target')
                            if weak_self:
                                omni.kit.undo.begin_group()
                                for relationship in weak_self._relationships:
                                    print('Remove target', target)
                                    if relationship:
                                        omni.kit.commands.execute(
                                            "RemoveRelationshipTarget", relationship=relationship, target=target
                                        )
                                omni.kit.undo.end_group()
                                if self._on_remove_target:
                                    self._on_remove_target(target)

                        ui.Button(
                            "-",
                            enabled=self._enabled,
                            width=ui.Pixel(14),
                            clicked_fn=partial(on_remove_target, weak_self=weakref.ref(self), target=target),
                        )

                def on_add_target(weak_self):
                    weak_self = weak_self()
                    if weak_self:
                        weak_self._target_picker.show(weak_self._targets_limit - len(weak_self.shared_targets))

                within_target_limit = self._targets_limit == 0 or len(self.shared_targets) < self._targets_limit
                button = ui.Button(
                    "Add Target(s)",
                    width=ui.Pixel(30),
                    clicked_fn=partial(on_add_target, weak_self=weakref.ref(self)),
                    enabled=within_target_limit and self._enabled
                )
                if not within_target_limit:
                    button.set_tooltip(
                        f"Targets limit of {self._targets_limit} has been reached. To add more target(s), remove current one(s) first."
                    )
            else:
                ui.StringField(name="models", read_only=True).model.set_value("Mixed")

    def _set_dirty(self):
        self._frame.rebuild()