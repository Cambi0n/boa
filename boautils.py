 
import os, sys
try:
    import cPickle as pickle
except:
    import pickle
import ConfigParser
 
def listDirectories(parentdir):
    try:
        os.makedirs(parentdir)
    except OSError:
        if os.path.isdir(parentdir):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise
    
    return [ name for name in os.listdir(parentdir) if os.path.isdir(os.path.join(parentdir, name)) ]

def makeDirectory(parentdir, newdir):
    newpath = os.path.join(parentdir, newdir)
    try:
        os.makedirs(newpath)
    except OSError:
        if os.path.isdir(newpath):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def listFiles(parentdir):
    return [ name for name in os.listdir(parentdir) if os.path.isfile(os.path.join(parentdir, name)) ]
        
def saveclasstodisk(clas,fname):
#    curpath = os.path.abspath(os.curdir)
#    print "Current path is: %s" % (curpath)
#    print "Trying to open: %s" % (fname)
    
    f = open(fname, 'wb')
    pickle.dump(clas,f, pickle.HIGHEST_PROTOCOL)
    f.close()
    
def loadclassfromdisk(fname):
#    curpath = os.path.abspath(os.curdir)
#    print "Current path is: %s" % (curpath)
#    print "Trying to open: %s" % (fname)
    
    f = open(fname, 'rb')
    clas = pickle.load(f)
    f.close()
    return clas

def parseConfigFile(fname):
    parser = ConfigParser.SafeConfigParser()
    parser.read(fname)
    
    dictlist = []

    for section_name in parser.sections():
        dict1 = {}
        for name, value in parser.items(section_name):
            dict1[name] = value
        dictlist.append(dict1)
        
    return dictlist
    
def load_new_encounter(enc_with_path):
    path, filename = os.path.split(enc_with_path)
    filename, ext = os.path.splitext(filename)
    sys.path.insert(0,path)
    module = __import__(filename)
#    reload(module) # Might be out of date
    del sys.path[0]
    return module, path
        


