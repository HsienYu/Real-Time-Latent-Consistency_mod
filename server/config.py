from typing import NamedTuple
import argparse
import os


class Args(NamedTuple):
    host: str
    port: int
    reload: bool
    max_queue_size: int
    timeout: float
    safety_checker: bool
    torch_compile: bool
    taesd: bool
    pipeline: str
    ssl_certfile: str
    ssl_keyfile: str
    sfast: bool
    onediff: bool = False
    compel: bool = False
    debug: bool = False
    ndi_send: bool = False
    ndi_name: str = "LCM NDI"
    syphon_send: bool = False
    syphon_name: str = "LCM Syphon"
    syphon_flip_vertical: bool = False

    def pretty_print(self):
        print("\n")
        for field, value in self._asdict().items():
            print(f"{field}: {value}")
        print("\n")


MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", 0))
TIMEOUT = float(os.environ.get("TIMEOUT", 0))
SAFETY_CHECKER = os.environ.get("SAFETY_CHECKER", None) == "True"
TORCH_COMPILE = os.environ.get("TORCH_COMPILE", None) == "True"
USE_TAESD = os.environ.get("USE_TAESD", "False") == "True"
default_host = os.getenv("HOST", "0.0.0.0")
default_port = int(os.getenv("PORT", "7860"))
NDI_SEND = os.environ.get("NDI_SEND", "False") == "True"
NDI_NAME = os.environ.get("NDI_NAME", "LCM NDI")
SYPHON_SEND = os.environ.get("SYPHON_SEND", "False") == "True"
SYPHON_NAME = os.environ.get("SYPHON_NAME", "LCM Syphon")
SYPHON_FLIP_VERTICAL = os.environ.get(
    "SYPHON_FLIP_VERTICAL", "True") == "True"

parser = argparse.ArgumentParser(description="Run the app")
parser.add_argument("--host", type=str,
                    default=default_host, help="Host address")
parser.add_argument("--port", type=int,
                    default=default_port, help="Port number")
parser.add_argument("--reload", action="store_true",
                    help="Reload code on change")
parser.add_argument(
    "--max-queue-size",
    dest="max_queue_size",
    type=int,
    default=MAX_QUEUE_SIZE,
    help="Max Queue Size",
)
parser.add_argument("--timeout", type=float, default=TIMEOUT, help="Timeout")
parser.add_argument(
    "--safety-checker",
    dest="safety_checker",
    action="store_true",
    default=SAFETY_CHECKER,
    help="Safety Checker",
)
parser.add_argument(
    "--torch-compile",
    dest="torch_compile",
    action="store_true",
    default=TORCH_COMPILE,
    help="Torch Compile",
)
parser.add_argument(
    "--taesd",
    dest="taesd",
    action="store_true",
    help="Use Tiny Autoencoder",
)
parser.add_argument(
    "--pipeline",
    type=str,
    default="txt2img",
    help="Pipeline to use",
)
parser.add_argument(
    "--ssl-certfile",
    dest="ssl_certfile",
    type=str,
    default=None,
    help="SSL certfile",
)
parser.add_argument(
    "--ssl-keyfile",
    dest="ssl_keyfile",
    type=str,
    default=None,
    help="SSL keyfile",
)
parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Debug",
)
parser.add_argument(
    "--compel",
    action="store_true",
    default=False,
    help="Compel",
)
parser.add_argument(
    "--sfast",
    action="store_true",
    default=False,
    help="Enable Stable Fast",
)
parser.add_argument(
    "--onediff",
    action="store_true",
    default=False,
    help="Enable OneDiff",
)
parser.add_argument(
    "--ndi-send",
    dest="ndi_send",
    action="store_true",
    default=NDI_SEND,
    help="Send the generated video over NDI (requires NDI SDK and ndi-python)",
)
parser.add_argument(
    "--ndi-name",
    dest="ndi_name",
    type=str,
    default=NDI_NAME,
    help="NDI stream name to advertise on the network",
)
parser.add_argument(
    "--syphon-send",
    dest="syphon_send",
    action="store_true",
    default=SYPHON_SEND,
    help="Send the generated video over Syphon (macOS)",
)
parser.add_argument(
    "--syphon-name",
    dest="syphon_name",
    type=str,
    default=SYPHON_NAME,
    help="Syphon server name (macOS)",
)
parser.add_argument(
    "--syphon-flip-vertical",
    dest="syphon_flip_vertical",
    action="store_true",
    default=SYPHON_FLIP_VERTICAL,
    help="Flip image vertically before sending over Syphon",
)
parser.add_argument(
    "--no-syphon-flip-vertical",
    dest="syphon_flip_vertical",
    action="store_false",
    help="Do not flip image vertically for Syphon",
)
parser.set_defaults(taesd=USE_TAESD)

config = Args(**vars(parser.parse_args()))
config.pretty_print()
