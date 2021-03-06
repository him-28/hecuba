import unittest
import time
import uuid
from cassandra.cluster import Cluster



class Hfetch_Tests(unittest.TestCase):
    keyspace = "hnumpy_test"
    contact_names = ['127.0.0.1']
    nodePort = 9042
    cluster = Cluster(contact_names,port=nodePort)
    session = cluster.connect()

    @classmethod
    def setUpClass(cls):
        cls.session.execute("CREATE KEYSPACE IF NOT EXISTS %s WITH replication "
                               "= {'class': 'SimpleStrategy', 'replication_factor': 1};" % cls.keyspace)
        cls.session.execute("CREATE TYPE IF NOT EXISTS %s.numpy_meta(dims frozen<list<int>>,type int,type_size int);" % cls.keyspace)

    @classmethod
    def tearDownClass(cls):
        #self.session.execute("DROP KEYSPACE IF EXISTS %s;" % cls.keyspace)
        pass

    def test_simple_memory(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        
        Analyzes:
        
        '''''''''
        dims = 2
        elem_dim = 4096

        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort


        table = "arrays_numpies"

        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute("CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))

        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)
        time.sleep(5)
        a = Hcache(self.keyspace, table, storage_id, [], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})

        #prepare data

        bigarr = np.arange(pow(elem_dim, dims)).reshape(elem_dim,elem_dim)

        print 'To be written '
        keys = [storage_id,-1,-1]
        values = [bigarr.astype('i')]
        print values
        #insert
        a.put_row(keys, values)

        #delete is a blocking op which waits the data to be flushed
        del a

        a = Hcache(self.keyspace, table, storage_id, [], ["storage_id",'cluster_id','block_id'], [{"name": "payload", "type": "numpy"}], {})
        #retrieve
        result = a.get_row(keys)
        print 'Retrieved from cassandra'
        print result
        if np.array_equal(bigarr,result[0]):
            print 'Created and retrieved are equal'
        else:
            self.fail('Created and retrieved ndarrays differ')
        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))

    def test_multidim(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        
        Analyzes:
        
        '''''''''
        dims = 3
        elem_dim = 5

        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort


        table = "arrays_numpies"

        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute("CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))
        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)
        time.sleep(5)
        a = Hcache(self.keyspace, table, storage_id, [], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})

        #prepare data
        bigarr = np.arange(pow(elem_dim, dims)).reshape(elem_dim, elem_dim, elem_dim)

        keys = [storage_id,-1,-1]
        values = [bigarr.astype('i')]

        #insert
        a.put_row(keys, values)

        # othw we ask for the row before it has been processed
        time.sleep(2)

        #retrieve
        result = a.get_row(keys)
        if np.array_equal(bigarr,result[0]):
            print 'Created and retrieved are equal'
        else:
            print 'Created and retrieved arrays differ, sth went wrong '
            print 'Array sent ', bigarr
            print 'Array retrieved ', result[0]
        time.sleep(2)
        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))


    def test_nopart(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        
        Analyzes:
        
        '''''''''

        elem_dim = 128
        dims = 2
        table = "arrays_numpies"

        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort


        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute("CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))

        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)
        time.sleep(5)
        a = Hcache(self.keyspace, table, storage_id, [], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})

        keys = [storage_id,-1,-1]
        bigarr = np.arange(pow(elem_dim, dims)).reshape(elem_dim, elem_dim)
        bigarr.itemset(0, 14.0)
        print 'Array to be written', bigarr.astype('d')

        t1 = time.time()
        a.put_row(keys, [bigarr.astype('d')])
        print 'Elapsed time', time.time() - t1

        time.sleep(2)
        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))

    def test_part(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        
        Analyzes:
        
        '''''''''

        dims = 2
        elem_dim = 128
        table = "arrays_numpies"

        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute("CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))

        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)

        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort

        time.sleep(5)
        a = Hcache(self.keyspace, table, storage_id, [(-8070430489100700000, 8070450532247928832)], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})

        keys = [storage_id,-1,-1]
        bigarr = np.arange(pow(elem_dim, dims)).reshape(elem_dim, elem_dim)
        bigarr.itemset(0, 14.0)
        print 'Array to be written', bigarr.astype('d')

        t1 = time.time()
        a.put_row(keys, [bigarr.astype('d')])
        print 'Elapsed time', time.time() - t1
        print '2D, elem dimension: ', elem_dim

        time.sleep(2)
        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))



    def test_npy_uuid(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        
        Analyzes:
        
        '''''''''

        dims = 2
        elem_dim = 128
        table = "arrays_numpies"

        print 'Dimensions: ', dims, ' Element in each dim: ', elem_dim
        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort

        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute(
            "CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))

        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)

        time.sleep(5)

        a = Hcache(self.keyspace, table, storage_id, [], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})


        bigarr = np.arange(pow(elem_dim, 2)).reshape(elem_dim, elem_dim)
        bigarr.itemset(0, 14.0)
        #print 'Array to be written', bigarr.astype('d')

        t1 = time.time()
        keys = [storage_id,-1,-1]
        a.put_row(keys, [bigarr.astype('d')])

        print 'Elapsed time', time.time() - t1
        print '2D, elem dimension: ', elem_dim

        time.sleep(3)
        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))

    def test_arr_put_get(self):
        from hfetch import connectCassandra
        from hfetch import Hcache
        import numpy as np
        '''''''''
        Running arr_put_get test
        
        Analyzes:
        
        '''''''''
        dims = 2
        elem_dim = 128
        table = "arrays_numpies"

        print 'Dimensions: ', dims, ' Element in each dim: ', elem_dim
        try:
            connectCassandra(self.contact_names, self.nodePort)
        except RuntimeError, e:
            print e
            print 'can\'t connect, verify the contact points and port', self.contact_names, self.nodePort

        self.session.execute("DROP TABLE if exists %s.%s;" % (self.keyspace, table))
        self.session.execute(
            "CREATE TABLE %s.%s(storage_id uuid, cluster_id int, block_id int, payload blob,PRIMARY KEY((storage_id,cluster_id),block_id));" % (self.keyspace, table))

        storage_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.keyspace + '.' + table)
        time.sleep(5)
        a = Hcache(self.keyspace, table, storage_id, [], ['storage_id','cluster_id','block_id'], [{'name': "payload", 'type': 'numpy'}], {})

        bigarr = np.arange(pow(elem_dim, dims)).reshape(elem_dim, elem_dim)
        bigarr.itemset(0, 14.0)
        print 'Array to be written', bigarr.astype('d')

        t1 = time.time()
        keys = [storage_id,-1,-1]
        a.put_row(keys, [bigarr.astype('d')])

        # othw we ask for the row before it has been processed
        time.sleep(5)

        try:
            result = a.get_row(keys)
            resarr = result[0]
            print "And the result is... ", resarr.reshape((elem_dim, elem_dim))
            print 'Elapsed time', time.time() - t1
            print '2D, elem dimension: ', elem_dim
        except KeyError:
            print 'not found'

        self.session.execute("DROP TABLE %s.%s;" % (self.keyspace, table))
