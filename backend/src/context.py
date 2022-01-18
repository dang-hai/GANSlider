import sys
import pathlib

PATH_TO_GANSPACE = str((pathlib.Path(__file__).parent.parent / 'ganspace').resolve())
sys.path.append(PATH_TO_GANSPACE)

from models import get_instrumented_model
from decomposition import get_or_compute
from config import Config