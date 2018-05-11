import mysql.connector
import json
import hashlib

db_config = {   'host' :'localhost',
                'user' : 'admin',
                'password' :'551996',
                'database' :'titanBox'
            }

conn = mysql.connector.connect(**db_config)
cur = conn.cursor()
cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def do_user_have_file(file_tag,ipv4_addr):
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    user_id = cur.fetchone()[0]

    query = """select Id
                from Files
                where Tag = %s"""
    cur.execute(query,(file_tag,))
    file_id = cur.fetchone()[0]

    query = """select count(*)
                from FileBelongsTo
                where userId = %s and FileId = %s"""
    cur.execute(query,(user_id,file_id,))
    res = cur.fetchone()
    return bool(res[0])

def list_of_files(ipv4_addr):
    """This function will list files of user logged in on machine having ipv4_addr"""
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    list_of_files = []
    if res is None:
        return list_of_files
    user_id = res[0]
    query = """select FileId
                from FileBelongsTo
                where userId = %s"""
    cur.execute(query,(user_id,))
    res = cur.fetchall()
    for tupl in res:
        query = """select Name
                    from Files
                    where Id = %s"""
        cur.execute(query,(tupl[0],))
        resu = cur.fetchone()
        list_of_files.append(resu[0])
    return list_of_files

def no_of_files():
    """This function will return no. of files on cloud"""
    query = """select count(*)
                from Files"""
    cur.execute(query)
    res = cur.fetchone()
    return res[0]

def match_file_tag(file_tag):
    """This function will match file_tag with present tags"""
    query = """select count(*)
                from Files
                where Tag = %s"""
    cur.execute(query,(file_tag,))
    res = cur.fetchone()
    return bool(res[0])

def no_of_blocks():
    """This function will return total no. of blocks on cloud"""
    query = """select count(*)
                from Blocks"""
    cur.execute(query)
    res = cur.fetchone()
    return res[0]

def block_count(file_name):
    """This function will return no. of blocks identified by file file_name"""
    query = """select Id
                from Files
                where Name = %s"""
    cur.execute(query,(file_name,))
    file_id = cur.fetchone()[0]
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""

    cur.execute(query,(file_id,))
    list_of_blocks = json.loads(cur.fetchone()[0])
    return len(list_of_blocks)

def total_blocks(file_tag):
    """This function will return no. of blocks occupied by file identified by file_tag"""
    query = """select Id
                from Files
                where Tag = %s"""
    cur.execute(query,(file_tag,))
    res = cur.fetchone()
    file_id = res[0]
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    res = cur.fetchone()
    list_of_blocks = json.loads(res[0])
    return len(list_of_blocks)

def match_block_tag(block_tag):

    query = """select count(*)
                from Blocks
                where Tag = %s"""
    cur.execute(query,(block_tag,))
    res = cur.fetchone()
    return res[0]

def verify(file_tag,block_tag,blockno):
    #Retrieve file_id
    query="""select Id
            from Files
            where Tag = %s"""
    cur.execute(query,(file_tag,))
    res = cur.fetchone()
    file_id = res[0]
    #Retrieve the block_id of blockno block
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    res=cur.fetchone()
    list_of_block_ids = json.loads(res[0])
    block_id = list_of_block_ids[blockno-1]
    #Retrieve block tag of block
    query = """select Tag
                from Blocks
                where Id = %s"""
    cur.execute(query,(block_id,))
    res = cur.fetchone()
    return res[0] == block_tag

def add_file_reference(ipv4_addr,file_tag):
    #Retrieve user_id
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    user_id = res[0]

    #Retrieve file_id
    query = """select Id
                from Files
                where Tag = %s"""
    cur.execute(query,(file_tag,))
    res = cur.fetchone()
    file_id = res[0]
    #Check if it exists or not
    query = """select count(*)
                from FileBelongsTo
                where userId = %s and FileId = %s"""
    cur.execute(query,(user_id,file_id,))
    res = cur.fetchone()
    if bool(res[0]):
        return
    query = """insert into FileBelongsTo
                values(%s,%s)"""
    cur.execute(query,(user_id,file_id,))
    conn.commit()

def add_key_reference(block_tag,block_key,ipv4_addr):
    #Retrieve block_id
    query = """select Id
                from Blocks
                where Tag = %s"""

    cur.execute(query,(block_tag,))
    block_id = cur.fetchone()[0]
    query = """select count(*)
                from EncryptionKeys
                where EncryptionKey = %s"""
    cur.execute(query,(block_key,))
    res = cur.fetchone()
    if res[0] == 0:
        #Retrieve key_id
        query = """insert into EncryptionKeys(EncryptionKey)
               values(%s)"""

        cur.execute(query,(block_key,))
        conn.commit()

    query = """select Id
                from EncryptionKeys
                where EncryptionKey = %s"""
    cur.execute(query,(block_key,))
    key_id = cur.fetchone()[0]
    #Retrieve user_id
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    user_id = cur.fetchone()[0]

    query = """select count(*)
                from KeyStore
                where userId = %s and blockId = %s and keyId = %s"""
    cur.execute(query,(user_id,block_id,key_id,))
    res = cur.fetchone()
    if res[0] == 0:
        #Insert all details into keystore

        query = """insert into KeyStore
                        values(%s,%s,%s)"""
        cur.execute(query, (user_id, block_id, key_id,))
        conn.commit()


def add_block_reference(block_tag,ipv4_addr,file_tag,file_name,block_key):
    #Find block_id first
    query = """select Id 
                from Blocks
                where Tag = %s"""
    cur.execute(query,(block_tag,))
    res = cur.fetchone()
    block_id = res[0]

    #Find user_id
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    user_id = res[0]

    query = """insert into EncryptionKeys(EncryptionKey)
                values(%s)"""
    cur.execute(query,(block_key,))
    conn.commit()

    query = """select Id
                    from EncryptionKeys
                    where EncryptionKey = %s"""
    cur.execute(query, (block_key,))
    res = cur.fetchone()
    key_id = res[0]
    query = """insert into KeyStore
                    values(%s,%s,%s)"""
    cur.execute(query, (user_id, block_id, key_id,))
    conn.commit()

    # Check whether file is listed in Files table, if yes retrieve file_id else make an entry
    query = """select count(*)
                    from Files
                    where Name = %s"""

    cur.execute(query, (file_name,))
    res = cur.fetchone()

    file_id = 0
    if bool(res[0]):
        # File is listed in Files table retrieve its file_id
        query = """select Id
                        from Files
                        where Name = %s"""

        cur.execute(query, (file_name,))
        res = cur.fetchone()
        file_id = res[0]

    else:
        # File is not listed,make_an_entry into Files table, FileBelongsTo table, BlockBelongsTo table
        query = """insert into Files(Name,Tag)
                        values(%s,%s)"""
        cur.execute(query, (file_name, file_tag,))
        conn.commit()
        query = """select Id 
                        from Files
                        where Name = %s"""

        cur.execute(query, (file_name,))
        res = cur.fetchone()
        file_id = res[0]

        query = """insert into FileBelongsTo
                        values(%s,%s)"""
        cur.execute(query, (user_id, file_id,))
        conn.commit()
        list_of_blocks = []
        jsonObj = json.dumps(list_of_blocks)
        query = """insert into BlockBelongsTo
                        values(%s,%s)"""
        cur.execute(query, (file_id, jsonObj,))
        conn.commit()
    query = """select BlockId
                    from BlockBelongsTo
                    where FileId = %s"""
    cur.execute(query, (file_id,))
    res = cur.fetchone()

    list_of_blocks = json.loads(res[0])
    list_of_blocks.append(block_id)
    jsonObj = json.dumps(list_of_blocks)
    query = """update BlockBelongsTo
                    set BlockId = %s
                    where FileId = %s"""
    cur.execute(query, (jsonObj, file_id,))
    conn.commit()

def push_block(block,file_name,block_tag,block_key,ipv4_addr,file_tag):
    #First push block into Blocks table and store its block_id for future
    query = """insert into Blocks(Block,Tag)
                values(%s,%s)"""
    cur.execute(query,(block,block_tag,))
    conn.commit()

    query = """select Id
                from Blocks
                where Tag = %s"""

    cur.execute(query,(block_tag,))
    res = cur.fetchone()

    block_id = res[0]
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""

    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    user_id = res[0]
    query = """insert into EncryptionKeys(EncryptionKey)
                values(%s)"""
    cur.execute(query,(block_key,))
    conn.commit()
    query = """select Id
                from EncryptionKeys
                where EncryptionKey = %s"""
    cur.execute(query,(block_key,))
    res = cur.fetchone()
    key_id = res[0]
    query = """insert into KeyStore
                values(%s,%s,%s)"""
    cur.execute(query,(user_id,block_id,key_id,))
    conn.commit()
    #Check whether file is listed in Files table, if yes retrieve file_id else make an entry
    query = """select count(*)
                from Files
                where Name = %s"""
    cur.execute(query,(file_name,))
    res = cur.fetchone()
    file_id = 0
    if bool(res[0]):
        #File is listed in Files table retrieve its file_id
        query = """select Id
                    from Files
                    where Name = %s"""
        cur.execute(query,(file_name,))
        res = cur.fetchone()
        file_id = res[0]
    else:
        #File is not listed,make_an_entry into Files table, FileBelongsTo table, BlockBelongsTo table
        query = """insert into Files(Name,Tag)
                    values(%s,%s)"""
        cur.execute(query,(file_name,file_tag,))
        conn.commit()
        query = """select Id 
                    from Files
                    where Name = %s"""
        cur.execute(query,(file_name,))
        res = cur.fetchone()
        file_id = res[0]
        query = """insert into FileBelongsTo
                    values(%s,%s)"""
        cur.execute(query,(user_id,file_id,))
        conn.commit()
        list_of_blocks = []
        jsonObj = json.dumps(list_of_blocks)
        query = """insert into BlockBelongsTo
                    values(%s,%s)"""
        cur.execute(query,(file_id,jsonObj,))
        conn.commit()
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    res = cur.fetchone()
    list_of_blocks = json.loads(res[0])
    list_of_blocks.append(block_id)
    jsonObj = json.dumps(list_of_blocks)
    query = """update BlockBelongsTo
                set BlockId = %s
                where FileId = %s"""
    cur.execute(query,(jsonObj,file_id,))
    conn.commit()

def retrieve_block(block_no,file_name,ipv4_addr):
    """This function will return block content and block key"""
    #retrieve file_id
    query = """select Id
                from Files
                where Name = %s"""
    cur.execute(query,(file_name,))
    file_id = cur.fetchone()[0]
    #Retrieve block_id
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    list_of_block_id = json.loads(cur.fetchone()[0])
    block_id = list_of_block_id[block_no-1]
    query = """select Block
                from Blocks
                where Id = %s"""
    cur.execute(query,(block_id,))
    res = cur.fetchone()
    buf = res[0]
    #retrieve user_id
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    user_id = res[0]
    #retrieve key_id
    query = """select keyId
                from KeyStore
                where userId = %s and blockId = %s"""
    cur.execute(query,(user_id,block_id,))
    res = cur.fetchone()
    key_id = res[0]
    #retrieve key
    query = """select EncryptionKey
                from EncryptionKeys
                where Id = %s"""
    cur.execute(query,(key_id,))
    res = cur.fetchone()
    key = res[0]
    return buf,key

def delete_records(filename,ipv4_addr):
    #retrieve user_id
    query = """select id
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    user_id = res[0]
    #retrieve file_id
    query = """select Id
                from Files
                where Name = %s"""
    cur.execute(query,(filename,))
    res = cur.fetchone()
    file_id = res[0]
    #retrieve list of blocks
    query = """select BlockId
                from BlockBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    res = cur.fetchone()
    list_of_block_id = json.loads(res[0])
    #delete keys
    for block_id in list_of_block_id:
        #retrieve keyId
        query = """select keyId
                    from KeyStore
                    where userId = %s and blockId = %s"""
        cur.execute(query,(user_id,block_id,))
        res = cur.fetchone()
        key_id = res[0]
        query = """delete from KeyStore
                    where userId = %s and blockId = %s and keyId = %s"""
        cur.execute(query,(user_id,block_id,key_id,))
        conn.commit()
        query = """select count(*)
                    from KeyStore
                    where keyId = %s"""
        cur.execute(query,(key_id,))
        res = cur.fetchone()
        if res[0] == 0:
            query = """delete from EncryptionKeys
                        where Id = %s"""
            cur.execute(query,(key_id,))
            conn.commit()
    #Check whether any user possess same file or not
    query = """delete from FileBelongsTo
                where userId = %s and FileId = %s"""
    cur.execute(query,(user_id,file_id,))
    conn.commit()
    query = """select count(*)
                from FileBelongsTo
                where FileId = %s"""
    cur.execute(query,(file_id,))
    res = cur.fetchone()
    if res[0] == 0:
        #Delete each & every block & file also
        for block_id in list_of_block_id:
            query = """delete from BlockBelongsTo
                        where FileId = %s"""
            cur.execute(query,(file_id,))
            conn.commit()
            query = """delete from Blocks
                        where Id = %s"""
            cur.execute(query,(block_id,))
            conn.commit()
        query = """delete from Files
                            where Id = %s"""
        cur.execute(query, (file_id,))
        conn.commit()
