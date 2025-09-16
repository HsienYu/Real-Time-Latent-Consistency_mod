import ctypes
import numpy as np
from PIL import Image
import logging
from typing import Optional
import os
import platform

ndi = None  # type: ignore
_NDI_AVAILABLE = False

# Attempt to prepare runtime path (particularly for macOS)
try:
    if platform.system() == "Darwin":
        default_lib_path = "/usr/local/lib/libndi.dylib"
        if os.path.exists(default_lib_path):
            ndi_dir = os.path.dirname(default_lib_path)
            os.environ.setdefault("NDI_RUNTIME_DIR_V5", ndi_dir)
            dyld = os.environ.get("DYLD_LIBRARY_PATH", "")
            if ndi_dir not in dyld.split(":"):
                os.environ["DYLD_LIBRARY_PATH"] = f"{ndi_dir}:{dyld}" if dyld else ndi_dir
            # Preload the dylib globally so the Python wrapper can resolve symbols
            try:
                ctypes.CDLL(default_lib_path, mode=ctypes.RTLD_GLOBAL)
            except Exception as e:
                logging.warning(f"Failed to preload NDI dylib: {e}")
    # Try importing the Python wrapper
    import NDIlib as ndi  # type: ignore
    _NDI_AVAILABLE = True
except Exception as e:
    logging.warning(f"NDIlib import failed: {e}")


class NDISender:
    """
    Lightweight wrapper to send PIL images as NDI video frames.
    Falls back to no-op if NDIlib is not available.
    """

    def __init__(self, name: str = "LCM NDI"):
        self.name = name
        self._init_ok = False
        self._sender = None
        self._video_frame = None

        if not _NDI_AVAILABLE:
            logging.warning("NDIlib not available. NDI send is disabled.")
            return

        if not ndi.initialize():
            logging.error("Failed to initialize NDI library")
            return

        # Create NDI sender
        send_settings = ndi.SendCreate()
        # API expects attribute 'ndi_name'
        try:
            send_settings.ndi_name = name
        except Exception:
            # fallback for any binding differences
            try:
                setattr(send_settings, "ndi_name", name)
            except Exception:
                pass

        self._sender = ndi.send_create(send_settings)
        if self._sender is None:
            logging.error("Failed to create NDI sender")
            return

        self._video_frame = ndi.VideoFrameV2()
        self._init_ok = True
        logging.info(f"NDI sender initialized: {name}")

    def send_image(self, image: Image.Image):
        if not self._init_ok:
            return
        # Convert PIL image (RGB) to BGRA as expected by NDI
        try:
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            arr = np.array(image, dtype=np.uint8)
            # RGBA -> BGRA
            arr = arr[:, :, [2, 1, 0, 3]].copy()

            h, w, _ = arr.shape
            self._video_frame.width = w
            self._video_frame.height = h
            # Use BGRX (alpha ignored) is common; for BGRA, some bindings use BGRX constant
            self._video_frame.FourCC = getattr(ndi, "FOURCC_VIDEO_TYPE_BGRX", None) or getattr(
                ndi, "FOURCC_VIDEO_TYPE_BGRA", 0
            )
            self._video_frame.frame_rate_N = 60
            self._video_frame.frame_rate_D = 1
            # stride and data pointer
            if hasattr(self._video_frame, "line_stride_in_bytes"):
                self._video_frame.line_stride_in_bytes = w * 4
            # set data pointer (ctypes)
            ptr = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
            if hasattr(self._video_frame, "data"):
                self._video_frame.data = ptr
            elif hasattr(self._video_frame, "p_data"):
                self._video_frame.p_data = ptr

            ndi.send_send_video_v2(self._sender, self._video_frame)
        except Exception as e:
            logging.error(f"NDI send failed: {e}")

    def close(self):
        if not _NDI_AVAILABLE:
            return
        try:
            if self._sender is not None:
                ndi.send_destroy(self._sender)
                self._sender = None
            ndi.destroy()
        except Exception:
            pass


class NullNDISender:
    """No-op replacement when NDI isn't available or disabled."""

    def __init__(self, *args, **kwargs):
        pass

    def send_image(self, image: Image.Image):
        pass

    def close(self):
        pass
