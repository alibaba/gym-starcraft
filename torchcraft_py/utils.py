def print_err(msg):
    raise RuntimeError(msg)


def is_empty(data):
    return data is not None and len(data) == 0


def to_str(*args):
    s = ""
    for a in args:
        if type(a) == float and a == int(a):
            r = str(int(a))
        else:
            r = str(a)
        s += r

    return s


def get_bool(b):
    if b == 'true' or b == 'TRUE' or b == 'True' or b == '1':
        return True
    else:
        return False


def get_int(args, c):
    if type(args) != list:
        print 'Error'
        return -1

    i = int(args[c])
    c += 1
    return i, c


def get_float(args, c):
    if type(args) != list:
        raise RuntimeError("Error args type" + type(args) + ", should be list.")

    i = float(args[c])
    c += 1
    return i, c


def parse_table(s):
    result = {}
    if len(s) < 2:
        return result

    s = s[1:-1]
    kvs = s.split(',')
    for kv in kvs:
        if len(kv) == 0:
            continue
        pair = kv.split('=')
        if len(pair) != 2:
            continue
        result[pair[0].strip()] = pair[1].strip()
    return result


def parse_list(s):
    result = []
    if len(s) < 2:
        return result

    s = s[1:-1]
    values = s.split(',')
    for v in values:
        v = v.strip()
        if len(v) > 0:
            result.append(v)
    return result


def get_weakest(units_table):
    min_total_hp = 1E30
    weakest_uid = -1
    for uid, ut in units_table.iteritems():
        if ut is None:
            continue
        tmp_hp = ut.health + ut.shield
        if tmp_hp < min_total_hp:
            min_total_hp = tmp_hp
            weakest_uid = uid
    return weakest_uid


def progress(nloop, battles_won, battles_game, total_battles):
    print "Loop: %5d | WinRate: %1.3f | #Wins: %4d | #Battles: %4d | #TotalBattles: %4d" % (
        nloop, battles_won / (battles_game + 1E-6), battles_won, battles_game,
        total_battles)
