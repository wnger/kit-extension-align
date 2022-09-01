__all__ = ["align_model_style"]

import omni.kit.app
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

ATTR_LABEL_WIDTH = 10
VHEIGHT = 10

align_model_style = {}
for i in ['x', 'y', 'z']:
    align_model_style["Image::checked-"+i.upper()] = {"image_url": f"{EXTENSION_FOLDER_PATH}/icons/checkbox_on_{i}.svg" }
    align_model_style["Image::unchecked-"+i.upper()] = {"image_url": f"{EXTENSION_FOLDER_PATH}/icons/checkbox_off_{i}.svg"}

v_style = {
    "margin_height": 1,
    "margin_width": 2
}