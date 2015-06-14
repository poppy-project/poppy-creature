import logging
import os
import re
from threading import Thread

from pypot.robot import Robot, from_json
from pypot.server.snap import SnapRobotServer

logger = logging.getLogger(__name__)
SERVICE_THREADS = {}


class DeamonThread(Thread):

    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self, *args, **kwargs):
        try:
            logger.info("Start thread %s" % self)
            Thread.run(self, *args, **kwargs)
        except:
            logger.exception("Error on thread %s " % self)


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class AbstractPoppyCreature(Robot):

    """ Abstract Class for Any Poppy Creature. """

    def __new__(cls,
                base_path=None, config=None,
                simulator=None, scene=None, host='127.0.0.1', port=19997, id=0,
                use_snap=False, snap_host='0.0.0.0', snap_port=6969, snap_quiet=True,
                use_http=False, http_host='0.0.0.0', http_port=8080, http_quiet=True,
                use_remote=False, remote_host='0.0.0.0', remote_port=4242,
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
        base_path = (os.path.dirname(__import__(creature).__file__)
                     if base_path is None else base_path)

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

        if use_snap:
            poppy_creature.snap = SnapRobotServer(
                poppy_creature, snap_host, snap_port, quiet=snap_quiet)

        if(use_http):
            from pypot.server.httpserver import HTTPRobotServer
            poppy_creature.http = HTTPRobotServer(poppy_creature, http_host, http_port,
                                                  cross_domain_origin="*", quiet=http_quiet)

        if(use_remote):
            from pypot.server import RemoteRobotServer
            poppy_creature.remote = RemoteRobotServer(poppy_creature, remote_host, remote_port)

        cls.setup(poppy_creature)

        return poppy_creature

    @classmethod
    def start_background_services(cls, robot, services=['snap', 'http', 'remote']):
        for service in services:
            if(hasattr(robot, service)):
                if service in SERVICE_THREADS:
                    logger.warning(
                        "A {} background service is already running, you may have to restart your script or reset your notebook kernel to start it again.".format(service))
                else:
                    SERVICE_THREADS[service] = DeamonThread(
                        target=getattr(robot, service).run, name="{}_server".format(service))
                    SERVICE_THREADS[service].daemon = True
                    SERVICE_THREADS[service].start()
                    logger.info("Starting {} service".format(service))

    @classmethod
    def setup(cls, robot):
        """ Classmethod used to specify your poppy creature.

        This is where you should attach any specific primitives for instance.

        """
        pass
