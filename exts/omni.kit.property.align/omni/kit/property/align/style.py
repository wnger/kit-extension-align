__all__ = ["align_model_style"]

from omni.ui import color as cl
from omni.ui import constant as fl
from omni.ui import url
import omni.kit.app
import omni.ui as ui
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

ATTR_LABEL_WIDTH = 10

url.checkbox_on_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_on.svg"
url.checkbox_off_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_off.svg"

align_model_style = {
    "Image::checked": {"image_url": url.checkbox_on_icon},
    "Image::unchecked": {"image_url": url.checkbox_off_icon},
}