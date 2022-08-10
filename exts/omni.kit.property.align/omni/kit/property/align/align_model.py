
__all__ = ["AlignModel"]

# from turtle import pos
from types import new_class
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
        boundWorld = box_cache.ComputeWorldBound(prim)
        boundLocal = box_cache.ComputeLocalBound(prim)

        range = boundWorld.ComputeAlignedBox()

        # print('boundWorld', boundWorld.ComputeAlignedBox())
        # print('boundLocal', boundLocal.ComputeAlignedBox())
        return range
        # print('Range', range)
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

    def set_scale(self, primPath, oldScale, targetScale, transVal):
        print('Align scale', oldScale, targetScale, transVal)

        newScale = oldScale
        if transVal[0] == True:
            newScale[0] = targetScale[0]
        if transVal[1] == True:
            newScale[1] = targetScale[1]
        if transVal[2] == True:
            newScale[2] = targetScale[2]

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=None,
            new_rotation_euler=None,
            new_rotation_order=None,
            new_scale=newScale,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

    def set_rotate(self, primPath, oldRotate, targetRotate, transVal):
        print('Align rotate', oldRotate, targetRotate)
        newRotate = oldRotate
        if transVal[0] == True:
            newRotate[0] = targetRotate[0]
        if transVal[1] == True:
            newRotate[1] = targetRotate[1]
        if transVal[2] == True:
            newRotate[2] = targetRotate[2]

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=None,
            new_rotation_euler=newRotate,
            new_rotation_order=None,
            new_scale=None,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

    def set_transform(self, stage, primPath, oldPos, targetPrim, targetPos, faceVal, transVal):

        newPos = oldPos
        sourcePrim = stage.GetPrimAtPath(primPath)


        # if targetPrim.HasProperty('xformOp:translate:pivot'):
        #     targetPivot = self._set_pivot(targetPrim)
        #     print('targetPivot', targetPivot)

        newX = oldPos[0]
        newY = oldPos[1]
        newZ = oldPos[2]



        print('Source path', primPath)
        # range = self.get_bound(targetPrim)
        # print(range.GetMin(), range.GetMax())



        # Source prim stats
        rangeSource = self.get_bound(sourcePrim)
        print('Source bound', rangeSource)
        bboxMinSource = rangeSource.GetMin()
        bboxMaxSource = rangeSource.GetMax()
        print('sourceMin', bboxMinSource, 'sourceMax', bboxMaxSource)

        # Get size
        sourceH = bboxMaxSource[1] - bboxMinSource[1]
        sourceW = bboxMaxSource[0] - bboxMinSource[0]
        sourceD = bboxMaxSource[2] - bboxMinSource[2]

        print('sourceH', sourceH, 'sourceW', sourceW, 'sourceD', sourceD)

        # If source is too small, eg. Xform
        if sourceH < 0:
            sourceH = 0
        if sourceW < 0:
            sourceW = 0
        if sourceD < 0:
            sourceD = 0




        rangeTarget = self.get_bound(targetPrim)
        # print('Target bound', range)
        bboxMinTarget = rangeTarget .GetMin()
        bboxMaxTarget = rangeTarget .GetMax()
        print('targetMin', bboxMinTarget, 'targetMax', bboxMaxTarget)
        # print('boxMinTarget', bboxMin)
        # print('boxMaxTarget', bboxMax)
        # print('transVal', transVal, type(transVal))
        # print('faceVal', faceVal)

        # Get size
        targetH = bboxMaxTarget[1] - bboxMinTarget[1]
        targetW = bboxMaxTarget[0] - bboxMinTarget[0]
        targetD = bboxMaxTarget[2] - bboxMinTarget[2]
        print('targetH', targetH, 'targetW', targetW, 'targetD', targetD)

        targetTransform = self._set_pivot(targetPrim)
        print('targetTransform', targetTransform)

        # If target is too small
        if targetH < 0:
            targetH = 0
        if targetW < 0:
            targetW = 0
        if targetD < 0:
            targetD = 0

        
        if transVal[0] == True:
            newX = targetPos[0]
        if transVal[1] == True:
            newY = targetPos[1]
        if transVal[2] == True:
            newZ = targetPos[2]


        # Target is Xform
        if targetH == 0 and targetW == 0 and targetD == 0:
            if faceVal == 1:
                # Top
                newY += sourceH*0.5
            elif faceVal == 2:
                # Bottom
                newY -= sourceH*0.5
            elif faceVal == 3:
                # Left
                newX -= sourceW*0.5
            elif faceVal == 4:
                # Right
                newX += sourceW*0.5
            elif faceVal == 5:
                # Front
                newZ += sourceD*0.5
            elif faceVal == 6:
                # Back
                newZ -= sourceD*0.5
        else:
            if faceVal == 1:
                # Top
                newY = bboxMaxTarget[1] + (sourceH*0.5)
            elif faceVal == 2:
                # Bottom
                newY = bboxMinTarget[1] - (sourceH*0.5)
            elif faceVal == 3:
                # Left
                newX = bboxMinTarget[0] - (sourceW*0.5)
            elif faceVal == 4:
                # Right
                newX = bboxMaxTarget[0] + (sourceW*0.5)
            elif faceVal == 5:
                # Front
                newZ = bboxMaxTarget[2] + (sourceD*0.5)
            elif faceVal == 6:
                # Back
                newZ = bboxMinTarget[2] - (sourceD*0.5)

        print('TargetPos', [newX, newY, newZ])
        if sourcePrim.HasProperty('xformOp:translate:pivot'):
            sourcePivotVal = sourcePrim.GetProperty('xformOp:translate:pivot').Get()
            newX -= sourcePivotVal[0]
            newY -= sourcePivotVal[1]
            newZ -= sourcePivotVal[2]

        pos = [newX, newY, newZ]
        print('newPos', pos)

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=Gf.Vec3d(pos[0], pos[1], pos[2]),
            new_rotation_euler=None,
            new_rotation_order=None,
            new_scale=None,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

        return

    def _set_pivot(self, prim):
        
        Xformable = UsdGeom.Xformable(prim)
        xform = UsdGeom.XformCommonAPI(Xformable)
        t = xform.GetXformVectors(Usd.TimeCode.Default())
        t[3][0] += t[0][0]
        t[3][1] += t[0][1]
        t[3][2] += t[0][2]
        return t


    def set_align(self, tabVal, faceVal, transVal):
        """Returns position of currently selected object"""
        # print('Get position', self._prim_path)
        print('SetAlignTrans', tabVal, transVal)
        stage = omni.usd.get_context().get_stage()
        # if not stage or not self._current_path:
        #     return [0, 0, 0]



        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print('selectedPrims', selectedPrims, selectedPrims[-1])

        if len(selectedPrims) == 1:
            sourcePrim = stage.GetPrimAtPath(selectedPrims[0])
            bound = self.get_bound(sourcePrim)
            print('my bound', selectedPrims[0], bound)
            return

        if len(selectedPrims) > 1:
            targetPrim = stage.GetPrimAtPath(selectedPrims[-1])
            

            t = self._set_pivot(targetPrim)
            targetTransform = [t[2],t[1],t[3],t[3]]
            print('TransPivot', t)
            print('TransSRT', omni.usd.get_local_transform_SRT(targetPrim))

            omni.kit.undo.begin_group()
            for prim in selectedPrims[:-1]:
                sourcePrim = stage.GetPrimAtPath(prim)
                t = self._set_pivot(sourcePrim)
                oldTransform = [t[2],t[1],t[3],t[3]]
                # print('sourcePrim', sourcePrim, oldTransform)
                # print('targetPrim', targetTransform)
                if tabVal == 'Transform':
                    oldPos = oldTransform[3]
                    targetPos = targetTransform[3]
                    self.set_transform(stage, prim, oldPos, targetPrim, targetPos, faceVal, transVal)
                elif tabVal == 'Scale':
                    oldScale = oldTransform[0]
                    targetScale = targetTransform[0]
                    self.set_scale(prim, oldScale, targetScale, transVal)
                elif tabVal == 'Rotate':
                    oldRotate = oldTransform[1]
                    targetRotate = targetTransform[1]
                    self.set_rotate(prim, oldRotate, targetRotate, transVal)

            omni.kit.undo.end_group()