import logging

logger = logging.getLogger(__name__)
logging.warning('You are still using the deprecated poppy-creature package! '
                'You should replace all "from poppy.creatures import *" '
                'with "from pypot.creatures import *" in order to be compatible with future development.')


from ._version import __version__

from pypot.creatures import *
