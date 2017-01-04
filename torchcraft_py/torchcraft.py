import zmq

import frame
import proto
import utils

DEBUG = 0  # Can take values 0, 1, 2 (from no output to most verbose)

mode = {'micro_battles': True, 'replay': False}


class Client:
    def __init__(self, server_ip, server_port='11111'):
        assert (server_ip != ''), "Server IP cannot be empty"

        self.server = "tcp://" + server_ip + ":" + server_port
        self.socket = None
        self.message_just_sent = False

        self.state = ServerState()

    def connect(self):
        self.state.d = {'game_ended': False,
                        'battle_just_ended': False,
                        'battle_won': False,
                        'waiting_for_restart': False,
                        'units_myself': {},
                        'units_enemy': {}}

        print "Connecting to the TorchCraft server: " + self.server
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(self.server)

        # Send hello message
        hello = "protocol=" + proto.VERSION + ",micro_mode=" \
                + str(mode['micro_battles'])
        self.socket.send(hello)

        # Receive setup message
        msg = self.socket.recv()
        self.state.parse(msg)

        self.message_just_sent = False
        print "TorchCraft server connected"

        return msg

    def receive(self):
        if not self.message_just_sent:
            if DEBUG > 1:
                print 'Unexpectedly sending ""'
            self.send("")

        if not self.socket.poll(30000):
            self.close()
            print "Timeout, TorchCraft server probably crashed"

        msg = self.socket.recv()
        self.state.parse(msg)
        self.state.update()

        self.message_just_sent = False

        return msg

    def send(self, msg):
        if self.message_just_sent:
            tmp = self.receive()
            if DEBUG > 1:
                print "Unexpectedly received: " + tmp

        if type(msg) is list:
            result = ""
            for v in msg:
                if result != "":
                    result = result + ":" + str(v)
                else:
                    result = str(v)
            self.socket.send(result)
        else:
            self.socket.send(msg)

        self.message_just_sent = True

    def close(self):
        if self.socket is not None:
            self.socket.close()


class ServerState:
    def __init__(self):
        """Server state will get its content updated from bwapi, it will have
            * map_data            : [torch.ByteTensor] 2D. 255 (-1) where not walkable
            * map_name            : [string] Name on the current map
            * img_mode            : [string] Image mode selected (can be empty, raw, compress)
            * lag_frames          : [int] Number of frames from order to execution
            * frame_from_bwapi    : [int] Game frame number as seen from BWAPI
            * game_ended          : [boolean] Did the game end? (i.e. did the map end)
            * battle_just_ended   : [boolean] Did the battle just end? (battle!=game)
            * waiting_for_restart : [boolean] Are we waiting to restart a new battle?
            * battle_won          : [boolean] Did we win the battle?
            * units_myself        : [table] w/ {unitIDs: unitStates} as {keys: values}
            * units_enemy         : [table] Same as above, but for the enemy player
            * bullets             : [table] Table with all bullets (position and type)
            * screen_position     : [table] Position of screen {x, y} in pixels. {0, 0} is top-left
        """
        self.d = dict()

    def parse(self, msg):
        t = utils.parse_table(msg)
        for k, v in t.iteritems():
            if k == 'frame':
                self.d['frame_string'] = v
                self.d['frame'] = frame.Frame.parse_from(v)
            elif k == 'deaths':
                self.d['deaths'] = utils.parse_list(v)
            else:
                self.d[k] = v

    def update(self):
        if mode['micro_battles']:
            self.d['battle_just_ended'] = False
            self.d['battle_won'] = False

            if not utils.is_empty(self.d['deaths']):
                for uid in self.d['deaths']:
                    self._remove_unit(uid)
                    if self._check_battle_ended(
                            self.d['units_myself'],
                            self.d['units_enemy']):
                        # Ignore the killing of remaining units in that battle.
                        # This will be re-initialized anyway in the next frame.
                        break

        if not mode['micro_battles'] or not self.d['battle_just_ended']:
            if not mode['replay'] and self.d['frame'] is not None:
                self._parse_unit()

            if not utils.is_empty(self.d['deaths']):
                for uid in self.d['deaths']:
                    self._remove_unit(uid)
                self.d['deaths'] = None

            if mode['micro_battles'] and self.d['waiting_for_restart']:
                we = utils.is_empty(self.d['units_myself'])
                ee = utils.is_empty(self.d['units_enemy'])
                if not we and not ee:  # We both have units
                    self.d['waiting_for_restart'] = False

    def _parse_unit(self):
        self.d['units_myself'] = {}
        self.d['units_enemy'] = {}
        myself = int(self.d['player_id'])
        enemy = 1 - myself
        units = self.d['frame'].units
        if myself in units:
            for unit in units[myself]:
                if unit is None:
                    continue
                if unit.type in proto.unit_types:
                    self.d['units_myself'][unit.id] = unit
        if enemy in units:
            for unit in units[enemy]:
                if unit.type in proto.unit_types:
                    self.d['units_enemy'][unit.id] = unit

    def _remove_unit(self, uid):
        if mode['replay']:
            if uid in self.d['frame'].units:
                del self.d['frame'].units[uid]
        else:
            if uid in self.d['units_myself']:
                del self.d['units_myself'][uid]
            if uid in self.d['units_enemy']:
                del self.d['units_enemy'][uid]

    def _check_battle_ended(self, units_myself, units_enemy):
        if self.d['waiting_for_restart']:
            return False

        if utils.is_empty(units_myself) or utils.is_empty(units_enemy):
            self.d['battle_just_ended'] = True
            self.d['waiting_for_restart'] = True
            self.d['last_battle_ended'] = self.d['frame_from_bwapi']
            if not utils.is_empty(units_myself) or utils.is_empty(units_enemy):
                self.d['battle_won'] = True
            return True
        return False
