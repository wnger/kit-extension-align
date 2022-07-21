
__all__ = ["AlignModel"]

# from turtle import pos
from typing import List
import omni.usd
import omni.kit.commands
from pxr import Tf, Usd, UsdGeom, Sdf, Gf

class AlignModel:
    def __init__(self, stage):
        print('myModelPrim', stage)
        # super().__init__()
        # self._target_path = target_path
        # self._get_position()

    def get_selection() -> List[str]:
        """Get the list of currently selected prims"""
        return omni.usd.get_context().get_selection().get_selected_prim_paths()

    def get_bound(self, prim):
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        return range
        # print('Range', range)
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

    def set_position(self, sourcePrim, targetPrim, faceVal, transVal):

        # Source prim stats
        rangeSource = self.get_bound(sourcePrim)
        bboxMinSource = rangeSource.GetMin()
        bboxMaxSource = rangeSource.GetMax()

        # Get size
        sourceH = bboxMaxSource[1] - bboxMinSource[1]
        sourceW = bboxMaxSource[0] - bboxMinSource[0]
        sourceD = bboxMaxSource[2] - bboxMinSource[2]

        # If source is too small, eg. Xform
        if sourceH < 0:
            sourceH = 0
        if sourceW < 0:
            sourceW = 0
        if sourceD < 0:
            sourceD = 0

        print('boxMinSource', bboxMinSource)
        print('boxMaxSource', bboxMaxSource)
        print('sourceH', sourceH)
        range = self.get_bound(targetPrim)
        # print('Range', range)
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()
        print('boxMinTarget', bboxMin)
        print('boxMaxTarget', bboxMax)
        print('transVal', transVal, type(transVal))
        print('faceVal', faceVal)

        newX = (bboxMinSource[0] + bboxMaxSource[0]) * 0.5
        newY = (bboxMinSource[1] + bboxMaxSource[1]) * 0.5
        newZ = (bboxMinSource[2] + bboxMaxSource[2]) * 0.5

        if transVal == 0:
            newX = (bboxMin[0] + bboxMax[0]) * 0.5
        elif transVal == 1:
            newY = (bboxMin[1] + bboxMax[1]) * 0.5
        elif transVal == 2:
            newZ = (bboxMin[2] + bboxMax[2]) * 0.5
        elif transVal == 3:
            newX = (bboxMin[0] + bboxMax[0]) * 0.5
            newY = (bboxMin[1] + bboxMax[1]) * 0.5
            newZ = (bboxMin[2] + bboxMax[2]) * 0.5

        if faceVal == 1:
            # Top
            newY = bboxMax[1] + (sourceH*0.5)
        elif faceVal == 2:
            # Bottom
            newY = bboxMin[1] - (sourceH*0.5)
        elif faceVal == 3:
            # Left
            newX = bboxMin[0] - (sourceW*0.5)
        elif faceVal == 4:
            # Right
            newX = bboxMax[0] + (sourceW*0.5)
        elif faceVal == 5:
            # Front
            newZ = bboxMax[2] + (sourceD*0.5)
        elif faceVal == 6:
            # Back
            newZ = bboxMin[2] - (sourceD*0.5)

        position = [newX, newY, newZ]
        return position

    def set_align(self, faceVal, transVal):
        """Returns position of currently selected object"""
        # print('Get position', self._prim_path)
        stage = omni.usd.get_context().get_stage()
        # if not stage or not self._current_path:
        #     return [0, 0, 0]



        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print('selectedPrims', selectedPrims, selectedPrims[-1])

        if len(selectedPrims) > 1:
            targetPrim = stage.GetPrimAtPath(selectedPrims[-1])
            for prim in selectedPrims[:-1]:
                sourcePrim = stage.GetPrimAtPath(prim)
                print('sourcePrim', sourcePrim)
                pos = self.set_position(sourcePrim, targetPrim, faceVal, transVal)
                omni.kit.commands.execute('TransformPrimSRT',
                    path=Sdf.Path(prim),
                    new_translation=Gf.Vec3d(pos[0], pos[1], pos[2]),
                    new_rotation_euler=None,
                    new_rotation_order=None,
                    new_scale=None,
                    old_translation=None,
                    old_rotation_euler=None,
                    old_rotation_order=None,
                    old_scale=None)

            # sourcePrim = stage.GetPrimAtPath(selectedPrims[0])
            
            
            # sourcePos = self.get_position(sourcePrim)
                    # Get position directly from USD



        return
        for primPath in selectedPrims:
            print('myPrim', primPath)
            sourcePrim = stage.GetPrimAtPath(primPath)
            sourcePos = self.get_position(sourcePrim)
            print('sourcePos', sourcePos)
            omni.kit.commands.execute('TransformPrimSRT',
                path=Sdf.Path(primPath),
                new_translation=Gf.Vec3d(targetPos[0], targetPos[1], targetPos[2]),
                new_rotation_euler=None,
                new_rotation_order=None,
                new_scale=None,
                old_translation=None,
                old_rotation_euler=None,
                old_rotation_order=None,
                old_scale=None)


        # print('sourceObj', sourceObj)
        return 