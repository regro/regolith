from regolith.chained_db import ChainDB


def test_dddi():
    a = {'a': {'a': {'a': 1}}}
    b = ChainDB(a)
    print(b['a'])
    print(b['a']['a'])
    print(b['a']['a']['a'])
    assert b['a']['a']['a'] + 1 == 2


def test_second_mapping():
    m1 = {'a': {'m': {'x': 0}}}
    m2 = {'a': {'m': {'y': 1}}}
    z = ChainDB(m1)
    z.maps.append(m2)
    print(z['a'])
    print(z['a']['m'].maps)
    assert z['a']['m']['y'] == 1


def test_double_mapping():
    m1 = {'a': {'m': {'y': 0}}}
    m2 = {'a': {'m': {'y': 1}}}
    z = ChainDB(m1)
    z.maps.append(m2)
    print(z['a'])
    print(z['a']['m'].maps)
    print(z['a']['m']['y'])
    assert z['a']['m']['y'] == 1


def test_list_mapping():
    m1 = {'a': {'m': [1, 2]}}
    m2 = {'a': {'m': [3, 4]}}
    z = ChainDB(m1)
    z.maps.append(m2)
    print(z['a'])
    print(z['a']['m'])
    assert z['a']['m'] == [3, 4]


def test_mixed_mapping():
    m1 = {'a': {'m': {'y': 1}}}
    m2 = {'a': {'m': 1}}
    z = ChainDB(m1)
    z.maps.append(m2)
    print(z['a'])
    print(z['a']['m'])
    assert z['a']['m'] == 1
