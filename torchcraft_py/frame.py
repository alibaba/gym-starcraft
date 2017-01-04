import json

import utils


class Order:
    def __init__(self):
        self.first_frame = 0
        self.type = 0  # See BWAPI::Orders::Enum

        self.targetId = 0
        self.targetX, self.targetY = 0, 0

    def __eq__(self, o):
        return self.type == o.type and self.targetId == o.targetId \
               and self.targetX == o.targetX and self.targetY == o.targetY


class Unit:
    def __init__(self):
        self.id, self.x, self.y = 0, 0, 0
        self.health, self.max_health, self.shield, self.energy = 0, 0, 0, 0
        self.maxCD, self.groundCD, self.airCD = 0, 0, 0
        self.idle, self.visible = False, False
        self.type, self.armor, self.shieldArmor, self.size = 0, 0, 0, 0

        self.pixel_x, self.pixel_y = 0, 0
        self.pixel_size_x, self.pixel_size_y = 0, 0

        self.groundATK, self.airATK = 0, 0
        self.groundDmgType, self.airDmgType = 0, 0
        self.groundRange, self.airRange = 0, 0

        self.orders = []

        self.velocityX, self.velocityY = 0.0, 0.0

        self.playerId = 0

    def read(self, args, c):
        self.id, c = utils.get_int(args, c)
        self.x, c = utils.get_int(args, c)
        self.y, c = utils.get_int(args, c)
        self.health, c = utils.get_int(args, c)
        self.max_health, c = utils.get_int(args, c)
        self.shield, c = utils.get_int(args, c)
        self.energy, c = utils.get_int(args, c)

        self.maxCD, c = utils.get_int(args, c)
        self.groundCD, c = utils.get_int(args, c)
        self.airCD, c = utils.get_int(args, c)
        self.idle, c = utils.get_int(args, c)
        self.visible, c = utils.get_int(args, c)
        self.type, c = utils.get_int(args, c)

        self.armor, c = utils.get_int(args, c)
        self.shieldArmor, c = utils.get_int(args, c)
        self.size, c = utils.get_int(args, c)

        self.pixel_x, c = utils.get_int(args, c)
        self.pixel_y, c = utils.get_int(args, c)
        self.pixel_size_x, c = utils.get_int(args, c)
        self.pixel_size_y, c = utils.get_int(args, c)

        self.groundATK, c = utils.get_int(args, c)
        self.airATK, c = utils.get_int(args, c)
        self.groundDmgType, c = utils.get_int(args, c)
        self.airDmgType, c = utils.get_int(args, c)

        self.groundRange, c = utils.get_int(args, c)
        self.airRange, c = utils.get_int(args, c)

        n_orders, c = utils.get_int(args, c)
        if n_orders < 0:
            utils.print_err("Corrupted replay: n_orders < 0")
            return

        self.orders = []
        for i in range(0, n_orders):
            self.orders.append(Order())
            self.orders[i].first_frame, c = utils.get_int(args, c)
            self.orders[i].type, c = utils.get_int(args, c)
            self.orders[i].targetId, c = utils.get_int(args, c)
            self.orders[i].targetX, c = utils.get_int(args, c)
            self.orders[i].targetY, c = utils.get_int(args, c)

        self.velocityX, c = utils.get_float(args, c)
        self.velocityY, c = utils.get_float(args, c)

        self.playerId, c = utils.get_int(args, c)

        return c

    def to_arr(self):
        return [self.id, self.x, self.y,
                self.health, self.max_health,
                self.shield, self.energy, self.maxCD,
                self.groundCD, self.airCD, self.idle,
                self.visible, self.type, self.armor,
                self.shieldArmor, self.size,
                self.pixel_x, self.pixel_y,
                self.pixel_size_x, self.pixel_size_y,
                self.groundATK, self.airATK,
                self.groundDmgType,
                self.airDmgType, self.groundRange,
                self.airRange]

    def __str__(self):
        s = utils.to_str(self.id, " ", self.x, " ", self.y, " ",
                         self.health, " ", self.max_health, " ",
                         self.shield, " ", self.energy, " ", self.maxCD, " ",
                         self.groundCD, " ", self.airCD, " ", self.idle, " ",
                         self.visible, " ", self.type, " ", self.armor, " ",
                         self.shieldArmor, " ", self.size, " ",
                         self.pixel_x, " ", self.pixel_y, " ",
                         self.pixel_size_x, " ", self.pixel_size_y, " ",
                         self.groundATK, " ", self.airATK, " ",
                         self.groundDmgType, " ",
                         self.airDmgType, " ", self.groundRange, " ",
                         self.airRange, " ")

        s += utils.to_str(len(self.orders), " ")
        for c in self.orders:
            s += utils.to_str(c.first_frame, " ",
                              c.type, " ", c.targetId, " ",
                              c.targetX, " ", c.targetY, " ")

        s += utils.to_str(self.velocityX, " ", self.velocityY)
        s += utils.to_str(" ", self.playerId)
        return s

    def write(self):
        return self.__str__()


class Resources:
    def __init__(self):
        self.ore = 0
        self.gas = 0
        self.used_psi = 0
        self.total_psi = 0

    def read(self, args, c):
        self.ore, c = utils.get_int(args, c)
        self.gas, c = utils.get_int(args, c)
        self.used_psi, c = utils.get_int(args, c)
        self.total_psi, c = utils.get_int(args, c)

        return c

    def __str__(self):
        s = utils.to_str(self.ore, " ", self.gas, " ")
        s += utils.to_str(self.used_psi, " ", self.total_psi)
        return s

    def write(self):
        self.__str__()


class Bullet:
    def __init__(self):
        self.type, self.x, self.y = 0, 0, 0

    def read(self, args, c):
        self.type, c = utils.get_int(args, c)
        self.x, c = utils.get_int(args, c)
        self.y, c = utils.get_int(args, c)

        return c

    def __str__(self):
        s = utils.to_str(self.type, " ", self.x, " ", self.y)
        return s

    def write(self):
        self.__str__()


class Action:
    def __init__(self):
        self.action = []  # std::vector<int32_t>
        self.uid = 0
        self.aid = 0


class Frame:
    def __init__(self):
        self.units = {}  # std::unordered_map<int32_t, std::vector<Unit>>
        self.actions = {}  # std::unordered_map<int32_t, std::vector<Action>>
        self.resources = {}  # std::unordered_map<int32_t, Resources>
        self.bullets = []  # std::vector<Bullet>
        self.reward = 0
        self.is_terminal = 0

    """
    @:type o: Frame
    """

    def filter(self, x, y, o):
        def in_radius(ux, uy):
            return (x / 8 - ux) * (x / 8 - ux) + (y / 8 - uy) * (y / 8 - uy) <= 20 * 4 * 20 * 4

        for player in self.units.items():
            o.units[player[0]] = []
            for unit in player[1]:
                if in_radius(unit.x, unit.y):
                    o.units[player[0]].append(unit)
        for bullet in self.bullets:
            if in_radius(bullet.x, bullet.y):
                o.bullets.append(bullet)

    @staticmethod
    def parse_from(v):
        f = v[2:-2]
        ff = f.split(" ")
        frame = Frame()
        frame.read(ff, 0)
        return frame

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    """
    @:type next_frame: Frame
    """

    def combine(self, next_frame):
        # For units, accumulate presence and commands
        for player in next_frame.units.items():
            player_id = player[0]
            player_units = player[1]

            if player_id not in self.units:
                self.units[player_id] = player_units
                continue

            # Build dictionary of uid -> position in current frame unit vector
            idx = {}
            for i in xrange(0, len(self.units[player_id])):
                idx[self.units[player_id][i].id] = i
            # Iterate over units in next frame
            for unit in player_units:
                if unit.id not in idx:
                    # Unit wasn't in current frame, add it
                    self.units[player_id].append(unit)
                else:
                    i = idx[unit.id]
                    # Take unit state from next frame but accumulate orders
                    # so as to have a vector of all the orders taken
                    ords = self.units[player_id][i].orders
                    for order in unit.orders:
                        if len(ords) == 0 or order != ords[-1]:
                            ords.append(order)
                    self.units[player_id][i] = unit
                    self.units[player_id][i].orders = ords
            # For resources: keep the ones of the next frame
            if player_id in next_frame.resources:
                next_res = next_frame.resources[player_id]
                self.resources[player_id].ore = next_res.ore
                self.resources[player_id].gas = next_res.gas
                self.resources[player_id].used_psi = next_res.used_psi
                self.resources[player_id].total_psi = next_res.total_psi
        # For other stuff, simply keep that of next_frame
        self.actions = next_frame.actions
        self.bullets = next_frame.bullets
        self.reward = next_frame.reward
        self.is_terminal = next_frame.is_terminal

    def read(self, args, c):
        n_player, c = utils.get_int(args, c)
        if n_player < 0:
            utils.print_err("Corrupted replay: units n_player < 0")
            return
        for i in xrange(0, n_player):
            id_player, c = utils.get_int(args, c)
            n_units, c = utils.get_int(args, c)
            if n_units < 0:
                utils.print_err("Corrupted replay: n_units < 0")
                return
            self.units[id_player] = []
            for j in xrange(0, n_units):
                self.units[id_player].append(Unit())
                c = self.units[id_player][j].read(args, c)

        n_player, c = utils.get_int(args, c)
        if n_player < 0:
            utils.print_err("Corrupted replay: actions n_player < 0")
            return
        for i in xrange(0, n_player):
            id_player, c = utils.get_int(args, c)
            n_actions, c = utils.get_int(args, c)
            if n_actions < 0:
                utils.print_err("Corrupted replay: n_actions < 0")
                return
            self.actions[id_player] = []
            for j in xrange(0, n_actions):
                self.actions[id_player].append(Action())
                self.actions[id_player][j].uid, c = utils.get_int(args, c)
                self.actions[id_player][j].aid, c = utils.get_int(args, c)
                size_a, c = utils.get_int(args, c)
                if size_a < 0:
                    utils.print_err("Corrupted replay: size_a < 0")
                    return

                self.actions[id_player][j].action = [0] * size_a
                for k in xrange(0, size_a):
                    self.actions[id_player][j].action[k], c = utils.get_int(args, c)

        n_player, c = utils.get_int(args, c)
        if n_player < 0:
            utils.print_err("Corrupted replay: resources n_player < 0")
            return
        for i in xrange(0, n_player):
            id_player, c = utils.get_int(args, c)
            self.resources[id_player] = Resources()
            c = self.resources[id_player].read(args, c)

        n_bullets, c = utils.get_int(args, c)
        if n_bullets < 0:
            utils.print_err("Corrupted replay: n_bullets < 0")
            return
        for i in xrange(0, n_bullets):
            self.bullets.append(Bullet())
            c = self.bullets[i].read(args, c)
        self.reward, c = utils.get_int(args, c)
        self.is_terminal, c = utils.get_int(args, c)
        return c

    def __str__(self):
        s = utils.to_str(len(self.units), " ")
        for v in self.units.items():
            s += utils.to_str(v[0], " ", len(v[1]), " ")
            for u in v[1]:
                s += utils.to_str(u, " ")
        s += utils.to_str(len(self.actions), " ")
        for v in self.actions.items():
            s += utils.to_str(v[0], " ", len(v[1]), " ")
            for u in v[1]:
                s += utils.to_str(u.uid, " ", u.aid, " ", len(u.action), " ")
                for a in u.action:
                    s += utils.to_str(a, " ")
        s += utils.to_str(len(self.resources), " ")
        for r in self.resources.items():
            s += utils.to_str(r[0], " ", r[1], " ")
        s += utils.to_str(len(self.bullets), " ")
        for b in self.bullets:
            s += utils.to_str(b, " ")
        s += utils.to_str(self.reward, " ", self.is_terminal)
        return s

    def write(self):
        return self.__str__()
