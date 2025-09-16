import logging
from typing import Optional

from PIL import Image
import numpy as np

# Syphon-python (https://pypi.org/project/syphon-python/) provides a Metal-based
# server and utilities to copy numpy RGBA images into a Metal texture.

_SYPHON_AVAILABLE = False
_SYPHON_IMPORT_ERROR = None

try:
    import syphon
    from syphon import SyphonMetalServer  # type: ignore
    from syphon.utils.numpy import copy_image_to_mtl_texture  # type: ignore
    from syphon.utils.raw import create_mtl_texture  # type: ignore
    _SYPHON_AVAILABLE = True
except Exception as e:  # pragma: no cover
    _SYPHON_IMPORT_ERROR = e
    _SYPHON_AVAILABLE = False


class SyphonSender:
    """Syphon sender using syphon-python (Metal backend).

    Creates a SyphonMetalServer and a Metal texture sized to the current image.
    On each frame, copies the numpy RGBA into the texture and publishes it.
    """

    def __init__(self, name: str = "LCM Syphon", flip_vertical: bool = False) -> None:
        self.name = name
        self._server: Optional[SyphonMetalServer] = None  # type: ignore
        self._texture = None
        self._tex_size = (0, 0)
        self._flip_vertical = flip_vertical

        if not _SYPHON_AVAILABLE:
            logging.warning(
                f"Syphon not available ({_SYPHON_IMPORT_ERROR}). Syphon send is disabled."
            )
            return

        try:
            self._server = SyphonMetalServer(name)
            logging.info(f"Syphon sender initialized (Metal): {name}")
        except Exception as e:
            logging.error(f"Failed to create SyphonMetalServer: {e}")
            self._server = None

    def _ensure_texture(self, width: int, height: int) -> None:
        if not self._server:
            return
        if self._texture is None or self._tex_size != (width, height):
            try:
                self._texture = create_mtl_texture(
                    self._server.device, width, height)
                self._tex_size = (width, height)
                logging.info(f"Syphon texture (re)created: {width}x{height}")
            except Exception as e:
                logging.error(f"Failed to create Metal texture: {e}")
                self._texture = None
                self._tex_size = (0, 0)

    def send_image(self, image: Image.Image) -> None:
        if not self._server:
            return
        try:
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            width, height = image.size
            self._ensure_texture(width, height)
            if self._texture is None:
                return

            arr = np.array(image, dtype=np.uint8)
            if self._flip_vertical:
                arr = np.flipud(arr).copy()
            # copy into Metal texture and publish
            copy_image_to_mtl_texture(arr, self._texture)
            self._server.publish_frame_texture(self._texture)
        except Exception as e:
            logging.error(f"Syphon send failed: {e}")

    def close(self) -> None:
        try:
            if self._server is not None:
                # syphon-python provides stop() to tear down server
                stop = getattr(self._server, "stop", None)
                if callable(stop):
                    stop()
        except Exception:
            pass
        finally:
            self._server = None
            self._texture = None
            self._tex_size = (0, 0)


class NullSyphonSender:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def send_image(self, image: Image.Image) -> None:
        pass

    def close(self) -> None:
        pass
