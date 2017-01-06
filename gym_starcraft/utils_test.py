import utils

if __name__ == '__main__':
    assert utils.get_degree(10, -10, 10, -20) == -90
    assert utils.get_degree(10, -10, 10, -5) == 90
    assert utils.get_degree(10, -10, 5, -10) == 180
    assert utils.get_degree(10, -10, 15, -10) == 0
    assert utils.get_degree(10, -10, 20, -20) == -45

    assert utils.get_distance(10, -10, 10, -20) == 10
    assert utils.get_distance(10, -10, 10, -5) == 5
    assert utils.get_distance(10, -10, 5, -10) == 5
    assert utils.get_distance(10, -10, 15, -10) == 5

    assert utils.get_position(90, 10, 10, -10) == (10, 0)
    assert utils.get_position(0, 10, 10, -10) == (20, -10)
    assert utils.get_position(180, 10, 10, -10) == (0, -10)
    x1, y1 = utils.get_position(-90, 10, 10, -10)
    assert int(x1) == 10
    assert int(y1) == -20
