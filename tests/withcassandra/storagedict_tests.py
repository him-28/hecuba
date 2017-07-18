import unittest

from hecuba import config
from hecuba.hdict import StorageDict
from app.words import Words
import uuid


class MyStorageDict(StorageDict):
    '''
    @TypeSpec <<position:int>,val:int>
    '''
    pass


class MyStorageDict2(StorageDict):
    '''
    @TypeSpec <<position:int, position2:text>,val:int>
    '''
    pass


class StorageDictTest(unittest.TestCase):
    def test_init_empty(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab1")
        tablename = "ksp.tab1"
        tokens = [(1l, 2l), (2l, 3l), (3l, 4l)]
        nopars = StorageDict(tablename,
                             [('position', 'int')],
                             [('value', 'int')],
                             tokens)
        self.assertEqual("tab1", nopars._table)
        self.assertEqual("ksp", nopars._ksp)

        res = config.session.execute(
            'SELECT storage_id, primary_keys, columns, class_name, name, tokens, istorage_props,indexed_on ' +
            'FROM hecuba.istorage WHERE storage_id = %s', [nopars._storage_id])[0]

        self.assertEqual(uuid.uuid3(uuid.NAMESPACE_DNS, tablename), nopars._storage_id)
        self.assertEqual(nopars.__class__.__module__, 'hecuba.hdict')
        self.assertEqual(nopars.__class__.__name__, 'StorageDict')

        rebuild = StorageDict.build_remotely(res)
        self.assertEqual('tab1', rebuild._table)
        self.assertEqual("ksp", rebuild._ksp)
        self.assertEqual(uuid.uuid3(uuid.NAMESPACE_DNS, tablename), rebuild._storage_id)

        self.assertEqual(nopars._is_persistent, rebuild._is_persistent)

    def test_init_empty_def_keyspace(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab1")
        tablename = "tab1"
        tokens = [(1l, 2l), (2l, 3l), (3l, 4l)]
        nopars = StorageDict(tablename,
                             [('position', 'int')],
                             [('value', 'int')],
                             tokens)
        self.assertEqual("tab1", nopars._table)
        self.assertEqual(config.execution_name, nopars._ksp)

        res = config.session.execute(
            'SELECT storage_id, primary_keys, columns, class_name, name, tokens, istorage_props,indexed_on ' +
            'FROM hecuba.istorage WHERE storage_id = %s', [nopars._storage_id])[0]

        self.assertEqual(uuid.uuid3(uuid.NAMESPACE_DNS, config.execution_name + '.' + tablename), nopars._storage_id)
        self.assertEqual(nopars.__class__.__module__, 'hecuba.hdict')
        self.assertEqual(nopars.__class__.__name__, 'StorageDict')

        rebuild = StorageDict.build_remotely(res)
        self.assertEqual('tab1', rebuild._table)
        self.assertEqual(config.execution_name, rebuild._ksp)
        self.assertEqual(uuid.uuid3(uuid.NAMESPACE_DNS, config.execution_name + '.' + tablename), rebuild._storage_id)

        self.assertEqual(nopars._is_persistent, rebuild._is_persistent)

    def test_simple_insertions(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab10")
        tablename = "tab10"
        tokens = [(1l, 2l), (2l, 3l), (3l, 4l)]
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')],
                         tokens)

        for i in range(100):
            pd[i] = 'ciao' + str(i)
        del pd
        count, = config.session.execute('SELECT count(*) FROM my_app.tab10')[0]
        self.assertEqual(count, 100)

    def test_dict_print(self):
        tablename = "tab10"
        config.session.execute("DROP TABLE IF EXISTS my_app." + tablename)
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])

        self.assertEquals(pd.__repr__(), "")

        pd[0] = 'a'
        self.assertEquals(pd.__repr__(), "{0: 'a'}")

        pd[1] = 'b'
        self.assertEquals(pd.__repr__(), "{0: 'a', 1: 'b'}")

        for i in range(1100):
            pd[i] = str(i)
        self.assertEquals(pd.__repr__().count(':'), 1000)

    def test_get_strs(self):
        tablename = "tab10"
        config.session.execute("DROP TABLE IF EXISTS my_app." + tablename)
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])
        pd[0] = 'str1'
        self.assertEquals(pd[0], 'str1')
        '''
        config.session.execute("DROP TABLE IF EXISTS my_app." + tablename)
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'list<text>')])
        pd[0] = ['str1', 'str2']
        self.assertEquals(pd[0], ['str1', 'str2'])

        config.session.execute("DROP TABLE IF EXISTS my_app." + tablename)
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'tuple<text,text>')])
        pd[0] = 'str1', 'str2'
        self.assertEquals(pd[0], 'str1', 'str2')
        '''

    def test_make_persistent(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.t_make_words")
        nopars = Words()
        self.assertFalse(nopars._is_persistent)
        nopars.ciao = 1
        nopars.ciao2 = "1"
        nopars.ciao3 = [1, 2, 3]
        nopars.ciao4 = (1, 2, 3)
        for i in range(10):
            nopars.words[i] = 'ciao' + str(i)

        count, = config.session.execute(
            "SELECT count(*) FROM system_schema.tables WHERE keyspace_name = 'my_app' and table_name = 't_make_words'")[
            0]
        self.assertEqual(0, count)

        nopars.make_persistent("t_make")

        del nopars
        count, = config.session.execute('SELECT count(*) FROM my_app.t_make_words')[0]
        self.assertEqual(10, count)

    def test_empty_persistent(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.wordsso_words")
        config.session.execute("DROP TABLE IF EXISTS my_app.wordsso")
        from app.words import Words
        so = Words()
        so.make_persistent("wordsso")
        so.ciao = "an attribute"
        so.another = 123
        config.batch_size = 1
        config.cache_activated = False
        for i in range(10):
            so.words[i] = str.join(',', map(lambda a: "ciao", range(i)))

        del so
        count, = config.session.execute('SELECT count(*) FROM my_app.wordsso_words')[0]
        self.assertEqual(10, count)

        so = Words("wordsso")
        so.delete_persistent()
        so.words.delete_persistent()

        count, = config.session.execute('SELECT count(*) FROM my_app.wordsso_words')[0]
        self.assertEqual(0, count)

    def test_simple_iteritems_test(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab_a1")

        pd = StorageDict("tab_a1",
                         [('position', 'int')],
                         [('value', 'text')])

        what_should_be = {}
        for i in range(100):
            pd[i] = 'ciao' + str(i)
            what_should_be[i] = 'ciao' + str(i)
        del pd
        count, = config.session.execute('SELECT count(*) FROM my_app.tab_a1')[0]
        self.assertEqual(count, 100)
        pd = StorageDict("tab_a1",
                         [('position', 'int')],
                         [('value', 'text')])
        count = 0
        res = {}
        for key, val in pd.iteritems():
            res[key] = val
            count += 1
        self.assertEqual(count, 100)
        self.assertEqual(what_should_be, res)

    def test_simple_itervalues_test(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab_a2")
        tablename = "tab_a2"
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])

        what_should_be = set()
        for i in range(100):
            pd[i] = 'ciao' + str(i)
            what_should_be.add('ciao' + str(i))
        del pd
        count, = config.session.execute('SELECT count(*) FROM my_app.tab_a2')[0]

        self.assertEqual(count, 100)

        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])
        count = 0
        res = set()
        for val in pd.itervalues():
            res.add(val)
            count += 1
        self.assertEqual(count, 100)
        self.assertEqual(what_should_be, res)

    def test_simple_iterkeys_test(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab_a3")
        tablename = "tab_a3"
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])

        what_should_be = set()
        for i in range(100):
            pd[i] = 'ciao' + str(i)
            what_should_be.add(i)
        del pd
        count, = config.session.execute('SELECT count(*) FROM my_app.tab_a3')[0]
        self.assertEqual(count, 100)
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])
        count = 0
        res = set()
        for val in pd.iterkeys():
            res.add(val)
            count += 1
        self.assertEqual(count, 100)
        self.assertEqual(what_should_be, res)

    def test_simple_contains(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab_a4")
        tablename = "tab_a4"
        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])

        for i in range(100):
            pd[i] = 'ciao' + str(i)
        del pd
        count, = config.session.execute('SELECT count(*) FROM my_app.tab_a4')[0]
        self.assertEqual(count, 100)

        pd = StorageDict(tablename,
                         [('position', 'int')],
                         [('value', 'text')])
        for i in range(100):
            self.assertTrue(i in pd)

    def test_composed_iteritems_test(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab12")
        tablename = "tab12"
        pd = StorageDict(tablename,
                         [('pid', 'int'), ('time', 'int')],
                         [('value', 'text'), ('x', 'float'), ('y', 'float'), ('z', 'float')])

        what_should_be = {}
        for i in range(100):
            pd[i, i + 100] = ('ciao' + str(i), i * 0.1, i * 0.2, i * 0.3)
            what_should_be[i, i + 100] = ('ciao' + str(i), i * 0.1, i * 0.2, i * 0.3)

        del pd

        count, = config.session.execute('SELECT count(*) FROM my_app.tab12')[0]
        self.assertEqual(count, 100)
        pd = StorageDict(tablename,
                         [('pid', 'int'), ('time', 'int')],
                         [('value', 'text'), ('x', 'float'), ('y', 'float'), ('z', 'float')])
        count = 0
        res = {}
        for key, val in pd.iteritems():
            res[key] = val
            count += 1
        self.assertEqual(count, 100)
        delta = 0.000001
        for i in range(100):
            a = what_should_be[i, i + 100]
            b = res[i, i + 100]
            self.assertEqual(a[0], b.value)
            self.assertAlmostEquals(a[1], b.x, delta=delta)
            self.assertAlmostEquals(a[2], b.y, delta=delta)
            self.assertAlmostEquals(a[3], b.z, delta=delta)

    def test_composed_key_return_list_iteritems_test(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.tab13")
        tablename = "tab13"
        pd = StorageDict(tablename,
                         [('pid', 'int'), ('time', 'float')],
                         [('value', 'text'), ('x', 'float'), ('y', 'float'), ('z', 'float')])

        what_should_be = {}
        for i in range(100):
            pd[i, i + 100] = ('ciao' + str(i), i * 0.1, i * 0.2, i * 0.3)
            what_should_be[i, i + 100] = ('ciao' + str(i), i * 0.1, i * 0.2, i * 0.3)

        del pd

        count, = config.session.execute('SELECT count(*) FROM my_app.tab13')[0]
        self.assertEqual(count, 100)
        pd = StorageDict(tablename,
                         [('pid', 'int')],
                         [('time', 'float'), ('value', 'text'), ('x', 'float'), ('y', 'float'), ('z', 'float')])
        count = 0
        res = {}
        for key, val in pd.iteritems():
            self.assertTrue(isinstance(key, int))
            self.assertTrue(isinstance(val[0], float))
            res[key] = val
            count += 1
        self.assertEqual(count, 100)
        # casting to avoid 1.0000001 float python problem
        data = set([(key, int(val.time), val.value, int(val.x), int(val.y), int(val.z)) for key, val in pd.iteritems()])
        data2 = set([(key[0], int(key[1]), val[0], int(val[1]), int(val[2]), int(val[3])) for key, val in what_should_be.iteritems()])
        self.assertEqual(data, data2)

    def test_storagedict_newinterface_localmemory(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.my_dict")

        my_dict = MyStorageDict()
        my_dict[0] = 1
        error = False
        try:
            result = config.session.execute('SELECT * FROM my_app.my_dict')[0]
        except Exception as e:
            error = True
        self.assertEquals(True, error)

    def test_storagedict_newinterface_memorytopersistent(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.my_dict")

        my_dict = MyStorageDict()
        my_dict[0] = 1
        error = False
        try:
            result = config.session.execute('SELECT * FROM my_app.my_dict')[0]
        except Exception as e:
            error = True
        self.assertEquals(True, error)

        my_dict.make_persistent('my_dict')
        count, = config.session.execute('SELECT count(*) FROM my_app.my_dict')[0]
        self.assertEquals(1, count)

    def test_storagedict_newinterface_persistent(self):
        config.session.execute("DROP TABLE IF EXISTS my_app.my_dict")

        my_dict = MyStorageDict()
        my_dict[0] = 1
        my_dict.make_persistent('my_dict')
        count, = config.session.execute('SELECT count(*) FROM my_app.my_dict')[0]
        self.assertEquals(1, count)

        my_dict[1] = 2
        count, = config.session.execute('SELECT count(*) FROM my_app.my_dict')[0]
        self.assertEquals(2, count)

        my_dict2 = MyStorageDict('my_dict')
        self.assertEquals(1, my_dict2[0])
        self.assertEquals(2, my_dict2[1])

if __name__ == '__main__':
    unittest.main()
