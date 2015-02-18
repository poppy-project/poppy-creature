import os
import re

from pypot.robot import Robot, from_json


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class AbstractPoppyCreature(Robot):
    """ Abstract Class for Any Poppy Creature. """

    def __new__(cls,
                config=None,
                simulator=None, scene=None, host='127.0.0.1', port=19997, id=0,
                sync=True):
        """ Poppy Creature Factory.

        Creates a Robot (real or simulated) and specifies it to make it a specific Poppy Creature.

        :param str config: path to a specific json config (if None uses the default config of the poppy creature - e.g. poppy_humanoid.json)

        :param str simulator: name of the simulator used (only vrep for the moment)
        :param str scene: specify a particular simulation scene (if None uses the default scene of the poppy creature - e.g. poppy_humanoid.ttt)
        :param str host: host of the simulator
        :param int port: port of the simulator
        :param int id: id of robot in the v-rep scene (not used yet!)
        :param bool sync: choose if automatically starts the synchronization loops

        .. warning:: You can not specify a particular config when using a simulated robot!

        """
        if config and simulator:
            raise ValueError('Cannot set a specific config '
                             'when using a simulated version!')

        creature = camelcase_to_underscore(cls.__name__)
        base_path = os.path.dirname(__import__(creature).__file__)

        if config is None:
            config = os.path.join(os.path.join(base_path, 'configuration'),
                                  '{}.json'.format(creature))

        if simulator is not None:
            if simulator != 'vrep':
                raise ValueError('Unknown simulation mode: "{}"'.format(simulator))

            from pypot.vrep import from_vrep

            scene_path = os.path.join(base_path, 'vrep-scene')

            if scene is None:
                scene = '{}.ttt'.format(creature)

            if not os.path.exists(scene):
                if ((os.path.basename(scene) != scene) or
                        (not os.path.exists(os.path.join(scene_path, scene)))):
                    raise ValueError('Could not find the scene "{}"!'.format(scene))

                scene = os.path.join(scene_path, scene)

            # TODO: use the id so we can have multiple poppy creatures
            # inside a single vrep scene
            poppy_creature = from_vrep(config, host, port, scene)
            poppy_creature.simulated = True

        else:
            poppy_creature = from_json(config, sync)
            poppy_creature.simulated = False

        cls.setup(poppy_creature)

        return poppy_creature

    @classmethod
    def setup(cls, robot):
        """ Classmethod used to specify your poppy creature.

        This is where you should attach any specific primitives for instance.

        """
        pass
