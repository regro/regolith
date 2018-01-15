from regolith.chained_db import ChainDB


def test_dddi():
    a = {'a': {'a': {'a': 1}}}
    z = ChainDB(a)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['a'], ChainDB)
    assert isinstance(z['a']['a']['a'], int)
    assert z['a']['a']['a'] + 1 == 2


def test_second_mapping():
    m1 = {'a': {'m': {'x': 0}}}
    m2 = {'a': {'m': {'y': 1}}}
    z = ChainDB(m1)
    z.maps.append(m2)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'].maps, list)
    assert z['a']['m']['y'] == 1


def test_double_mapping():
    m1 = {'a': {'m': {'y': 0}}}
    m2 = {'a': {'m': {'y': 1}}}
    z = ChainDB(m1)
    z.maps.append(m2)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'].maps, list)
    assert isinstance(z['a']['m']['y'], int)
    assert z['a']['m']['y'] == 1


def test_list_mapping():
    m1 = {'a': {'m': [1, 2]}}
    m2 = {'a': {'m': [3, 4]}}
    z = ChainDB(m1)
    z.maps.append(m2)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], list)
    assert z['a']['m'] == [3, 4]


def test_mixed_mapping():
    m1 = {'a': {'m': {'y': 1}}}
    m2 = {'a': {'m': 1}}
    z = ChainDB(m1)
    z.maps.append(m2)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], int)
    assert z['a']['m'] == 1


def test_exactness():
    d = {'y': 1}
    m1 = {'a': {'m': d}}
    z = ChainDB(m1)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], ChainDB)
    assert isinstance(z['a']['m'].maps[0], dict)
    assert d is z['a']['m'].maps[0]


def test_exactness_setting():
    d = {'y': 1}
    m1 = {'a': {'m': d}}
    z = ChainDB(m1)
    e = {'z': 2}
    z['a']['m'] = e
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], ChainDB)
    assert isinstance(z['a']['m'].maps[0], dict)
    assert e is z['a']['m'].maps[0]


def test_exactness_setting_multi():
    d = [1, 2]
    e = [3, 4]
    m1 = {'a': {'m': d}}
    m2 = {'a': {'m': e}}
    z = ChainDB(m1)
    z.maps.append(m2)
    g = [-1, -2]
    z['a']['m'] = g
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], list)
    assert isinstance(z['a'].maps[0], dict)
    assert g is z['a'].maps[1]['m']
    # We sent this to the first map not the last
    assert z['a']['m'] is g


def test_exactness_setting_multi2():
    d = [1, 2]
    e = [3, 4]
    ee = [5, 6]
    m1 = {'a': {'m': d}}
    m2 = {'a': {'m': e, 'mm': ee}}
    z = ChainDB(m1)
    z.maps.append(m2)
    g = [-1, -2]
    z['a']['mm'] = g
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], list)
    assert isinstance(z['a'].maps[0], dict)
    assert g is z['a'].maps[1]['mm']
    # We sent this to the first map not the last
    assert z['a']['m'] is not g


def test_exactness_setting_multi_novel():
    d = [1, 2]
    e = [3, 4]
    m1 = {'a': {'m': d}}
    m2 = {'a': {'m': e}}
    z = ChainDB(m1)
    z.maps.append(m2)
    g = [-1, -2]
    z['a']['mm'] = g
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['m'], list)
    assert isinstance(z['a'].maps[0], dict)
    assert g is z['a'].maps[0]['mm']
    # We sent this to the first map not the last
    assert z['a']['m'] is not g


def test_dicts_in_lists():
    c = [{'m': 1}, {'n': 2}]
    d = [{'o': 3}, {'p': 4}]
    t = c + d
    m1 = {'a': {'b': c}}
    m2 = {'a': {'b': d}}
    z = ChainDB(m1)
    z.maps.append(m2)
    assert isinstance(z['a'], ChainDB)
    assert isinstance(z['a']['b'], list)
    assert z['a']['b'] is not t
    assert c[0] is z['a']['b'][0]
    assert c[1] is z['a']['b'][1]
    assert d[0] is z['a']['b'][2]
    assert d[1] is z['a']['b'][3]
