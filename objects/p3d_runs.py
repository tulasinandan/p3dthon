########################################################################################################################################################
########################################################################################################################################################
#                                                                                                                                                      #
#                                                 Python Progs :  p3d_runs.py                                                                          #
#                                                 Aruthor      :  Colby Haggerty                                                                       #
#                                                 Date         :  2013.11.30                                                                           #
#                                                                                                                                                      #
#                                                                                                                                                      #
########################################################################################################################################################
### Discription:
#
#       This class is ment to be the foundation for loading in any run data. The key idea is to load in a run object
#       that looks at a table that indexes all of a given runs information. The plan is that this can be called from 
#       any location and it will know how to where and how to handle the data you are looking for. This may warrent
#       the need to make another class that deals with the indexing file directly because it may become too complicated
#
########################################################################################################################################################
### Update: 2014.03.28
#
#       Here we are making some sizable changes to the structure of this set of python codes. Most importantly we are
#       now calling this set of software p3dthon (p3d + python). But serisously, We are chaging how a run object's data
#       is initilized. Each instante of the object will have its own file (runame.info) in the run_info directory.
#       the run_list.dat will then keep an uptodate list of all of users run objects. and the plan is python will
#       update this list per the user
#
#       TRY TO CODE: A class method like this try_to_get_internal_dict_member() that will atempt to refence a part of
#                    the data assumed to be set, and then adds it to the runinfo file when it dose not exsist
#
########################################################################################################################################################


import os
import datetime
import numpy as np
import struct
from scipy.io.idl import readsav

#temp = p3d_movie('path',000,{'no':'no'})
#print 'loaded temp?'

# Currently Configured for Yellowstone
USER = 'colbyh'
HOME_PATH = '/glade/u/home/'+USER+'/'
P3DTHON_PATH = HOME_PATH+'pythonprogs/2014.04.p3d_etal/'
SCRATCH_PATH = '/glade/scratch/'+USER+'/'

########################################################################################################################################################
################################################ Initilization of p3d run object #######################################################################
########################################################################################################################################################
class p3d_run(object):
    """p3d_run object """

    def __init__(self, runname): 
        """ Initilazition Routine for the p3d_run object

        Fill in method discription

        @param runname    : The string to identify runs, It should just corspond to a p3d run name

        @return: @todo

        Exemple  :

        Creation
        :
        2013-05-01
        11:21:19.671182
        """

        self.run_info_dict={'run_name':runname.lower()}

# First Check to see if the runname.info file exsists for this run
        self.run_info_file = P3DTHON_PATH+'p3dthon/run_info/'+runname.lower()+'.info'
        if os.path.isfile(self.run_info_file):
# File exsists! load up all the run data
            print 'File found and opened!!'
            self.load_info_file()
        else:
            print 'WARNING: '+self.run_info_file+' dose not exsist!'
            print "Do you want to create a new run.info file for this run?('y'/'')"
            get_raw = raw_input()
            if get_raw.lower() == 'y':
                print "### Creating new run: "
                print "### run.info file = " + self.run_info_file
                self.create_info_file()
            else:
                print "Do you want a temporary object to use the methods?('y'/'')"
                get_raw = raw_input()
                if get_raw.lower() == 'y':
                    print 'Not coded yet! talk to colby about this!'
                else:
                    print 'Not coded yet! talk to colby about this!'


########################################################################################################################################################
#       End:                                      Init                                                                                                 #
########################################################################################################################################################
#       Begin:                                   Creating and maintaining the run.info file                                                            #
########################################################################################################################################################

    def load_info_file(self):
        """ Class Method: uses preset file name for run info file and gets all items
        """
# Open the .info file and get all of the items
        with open(self.run_info_file) as fname:
            run_info_content = fname.readlines()
        fname.close()
# Go through Items and write them to the run info dictionary
        file_header = ''
        for item in run_info_content:
            if len(item.strip())>0:
                if item[0] != '!':
                    run_key = item.strip().split()[0]
                    run_val = item.strip().split()[1:]
####################################################################################################################################################### Colby DEBUG what ever this issue is 
## Colby Move this section to the wrigting section, It seems usefull to leave info in lists, but only write them out as strings
                    # We need to make sure that we are not wrighing things as lists
                    if type(run_val) is list:
                        if len(run_val) < 2:
                            run_val = run_val[0]
                        else:
                            temp_run_val =  ''
                            for elements in range(len(run_val)):
                                temp_run_val = temp_run_val + ' ' + str(run_val[elements])
                            run_val = temp_run_val.strip()

                    self.run_info_dict[run_key] = run_val
                else: 
                    if item.find('! File Last Updated on') < 0:
                        file_header = file_header+item
            if len(file_header) > 0:
                self.run_info_dict['file_header'] = file_header


    def create_info_file(self):
        """ Class Method: Creates an info file for a previsouly un named run
        """
        if os.path.isfile(self.run_info_file):
            print '!!!!!!! BIG ISSUE !!!!!!!!'
            print 'run.info file '+self.run_info_file+' exsists! Can not create file'
            print 'Abortting!!'
            return -1
        f = open(self.run_info_file,'w+')
        now = datetime.datetime.now()
        file_header = '! run.info file = '+self.run_info_file+'\n' + \
                      '! File Created With ' + os.getcwd()+'/p3d_runs.py\n' + \
                      '! File Created on ' + str(now.year)+'.'+str(now.month)+'.'+ str(now.day)+ \
                      ' at ' + str(now.hour)+':'+str(now.minute)+':'+ str(now.second)+ \
                      ' (Hr:Min:Sec) (NOTE: if yellowstone then Mnt Std Time)\n' \
                      '\n'
        f.write(file_header)
        f.close()

# I think the best way to saftly wright is to read the file, add or modify an item to the dict, then rewrite it
    
    def add_info_keyval(self,key,val):
        """ adds or modifies an item in the run.info file

        Fill in method discription

        @param key      : The string to identify a particluar item
        @param val      : the value coresponding to the particlar key

        @return: @todo

        Exemple  :

        Creation
        :
        2013-05-01
        11:21:19.671182
        """
# First we reread the run.info file so that every thing will remain up to date
        self.load_info_file()
# Next we check to see if we will be over righting any thing
        if self.run_info_dict.has_key(key):
            print 'WARNING: Trying to overwrite key'+key
            print '         with value of '+self.run_info_dict[key]
            print '         with new value of '+val
            print "Do you want to procced? ('y'/'')"
            get_raw = raw_input()
            if get_raw.lower() == 'y':
                print "### Modifing run.info: "
                self.run_info_dict[key] = val
                self.rewrite_info_file()
            else:
                return 0 
        else:
            print "### Adding info {'%s' : '%s'} to run.info %s" % (key,val,self.run_info_file)
            self.run_info_dict[key] = val
            self.rewrite_info_file()
            

    def rewrite_info_file(self):
        """ take the current run_info_dict, and writes it to run.info file
            This is a scarry method and you should be very carfull with it.
            It will happly erase your run.info file and not feal bad at all
            because it is a heartless machine

        Fill in method discription

        @return: @todo

        Exemple  :

        Creation
        :
        2013-05-01
        11:21:19.671182
        """
        now = datetime.datetime.now()
        file_text = self.run_info_dict['file_header']+'\n' + \
                      '! File Last Updated on ' + str(now.year)+'.'+str(now.month)+'.'+ str(now.day)+ \
                      ' at ' + str(now.hour)+':'+str(now.minute)+':'+ str(now.second) +'\n\n'
        for keys in self.run_info_dict.keys():
            if keys != 'file_header':
                file_text = file_text+str(keys)+' '+str(self.run_info_dict[keys])+'\n'

        f = open(self.run_info_file,'w')
        f.write(file_text)
        f.close()
        

    def test_info_key(self,key,info_discription=''):
        """ A Method that checks to seff a this peice of info is in the run.info file
            If the peice of info is not contained it addes its to the set
        """
        if key not in self.run_info_dict.keys():
            print '### WARNING: Key %s not found in run.info file!\n' % key
            print "             Would you like to add %s to run.infofile (y/''))?" % key
            get_raw = raw_input()
            if get_raw.lower() != 'y':
                print 'OK, no info added to run.info file! ABORTING METHOD CALL!!'
                return -1
            else:
                print "What value do you want to add for the key %s? " % (key)
                if len(info_discription) >0:
                    print 'Info Discription: %s' % (info_discription)
                get_raw = raw_input()
                self.add_info_keyval(key,get_raw)
                
    def change_info_val(self,key,info_discription=''):
        """ A Method that allows you to change a value coresponding to a particular key in the run.info file
        """
        print '### Attempting to change the value for the key  %s' % key
        print '### Current {Key : Value} pair:\n{%s : %s}' %(key,self.run_info_dict[key])
        print "### Change Value (y/'')?"
        get_raw = raw_input()
        if get_raw.lower() != 'y':
            print 'OK, no info value not changed in the run.info file! ABORTING METHOD CALL!!'
            return -1
        else:
            print "What is the new value for the key %s? " % (key)
            if len(info_discription) >0:
                print 'Info Discription: %s' % (info_discription)
            get_raw = raw_input()
            self.add_info_keyval(key,get_raw)

########################################################################################################################################################
#       End:                                     Edit run.info file                                                                                   #
########################################################################################################################################################
#       Begin:                                   Loading raw run files (param, movie, or dump)                                                         #
########################################################################################################################################################

    def load_param(self,change_flag=False,return_dict=False):
        """ Method to load in the param file for a given run
            It will try and then ask for where the file is. if it doent know
        """
# load_param requires a path for the param file! a run_info_dict entry of 'param_path'
        if self.test_info_key('param_path','Full path of param file for this run, included the files name') == -1:
            print 'Necesarry Path for the Param File not Set!!! ABORTING!!!'
            return -1
        self.param_dict = {}
# Add a try catch statment incase you cant find the file
        fname = os.path.expanduser(self.run_info_dict['param_path']).strip()
        scratch_sub = "/glade/scratch/colbyh"
        if fname.find("$SCRATCH") > -1:
            fname = fname[0:fname.find("$SCRATCH")]+scratch_sub+fname[fname.find("$SCRATCH")+8:]

        while not os.path.isfile(fname):
            self.change_info_val('param_path')
            fname = os.path.expanduser(self.run_info_dict['param_path']).strip()

            print 
        with open(fname) as f:
            content = f.readlines()
        for item in content:
            if '#define' in item and item[0] != '!':
                if len(item.split()) > 2:
                    key = item.split()[1]
                    val = convert(item.split()[2])
                else:
                    key = item.split()[1]
                    val = 'NO_ARG'
                self.param_dict[key] = val


    def reff_movie(self,movie_num=-1):
        import p3d_movie
# load_param requires a path for the param file! a run_info_dict entry of 'param_path'

# load_movie_log requires a path for the log file! a run_info_dict entry of 'movie_path'
#
#CoOLBY!!! make sure you pad movie num
        if self.test_info_key('movie_path','Path of directory for movie files for this run') == -1:
            print 'Necesarry Path for the Movie.log File not Set!!! ABORTING!!!'
            return -1    
        print self.run_info_dict['movie_path']
        if not os.path.isdir(self.run_info_dict['movie_path']): 
            print 'Dir %s not found!!!'%self.run_info_dict['movie_path']
            self.change_info_val('movie_path','Path for the current set of movie files')


        if not (hasattr(self,'param_dict')): self.load_param()


        self.movie = p3d_movie.p3d_movie(self.run_info_dict['movie_path'],self.param_dict,movie_num)
        


    def get_info(self):
        """ A Method that returns all of the run information that the object has
        """

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%                                                                                        %%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Colby: We need to think of a smart way to let the user easly change the info values    %%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%                                                                                        %%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        #self.movie_log_dict ={} 
        #self.movie_dict= {} 
        #self.movie_arr = []
        #self.dump_field_dict = {}




#---------------------------------------------------------------------------------------------------------------
#   Method: mk_restore_file
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
#!Code this next
    #def load_movie(self,movie_num,movie_var,movie_time):
    def load_movie_all(self,arg_list):
        if len(arg_list) < 2: 
            print 'ERROR: Wrong number of arguments. load_movie() accepts a list of 3 args:'
            print '       [Movie_number, Movie_Variable, Moive_time'
            return -1
        else:
            movie_num = arg_list[0]
            movie_time= arg_list[1]
        self.load_movie_log(movie_num)
        for key in self.movie_arr:
            print 'Restoring Movie File: movie.'+key+'.'+str(movie_num)
            self.movie_dict[key] = self.load_movie([movie_num,key,movie_time])
            print 'NOT CODED'
            return -1

#---------------------------------------------------------------------------------------------------------------
#   Method: restore_idl
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
#!Code this next
    #def load_movie(self,movie_num,movie_var,movie_time):
    def restore_idl(self,arg_list=''):
        if len(arg_list) == 0: 
            print 'You using the default restore value wirting in run_list.dat file'
            print 'But I think that this value should really be for non idl save files, so this is most likely a bad message'
            restore_path = self.run_id_dict['restore_path']
        else:
            restore_path = arg_list
        print 'Restoreing IDL file "'+restore_path+'"'
        return_data = readsav(restore_path)
        return return_data
#---------------------------------------------------------------------------------------------------------------
#   Method: load_movie_all
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
    #def load_movie(self,movie_num,movie_var,movie_time):
    def load_movie_all(self,arg_list):
        if len(arg_list) < 2: 
            print 'ERROR: Wrong number of arguments. load_movie() accepts a list of 3 args:'
            print '       [Movie_number, Movie_Variable, Moive_time'
            return -1
        else:
            movie_num = arg_list[0]
            movie_time= arg_list[1]
        self.load_movie_log(movie_num)
        for key in self.movie_arr:
            print 'Restoring Movie File: movie.'+key+'.'+str(movie_num)
            self.movie_dict[key] = self.load_movie([movie_num,key,movie_time])
        return 0




#---------------------------------------------------------------------------------------------------------------
#   Method: load_movie
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_var (to identify which varible you want to read)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
    #def load_movie(self,movie_num,movie_var,movie_time):
    def load_movie(self,arg_list):
        if len(arg_list) < 3: 
            print 'ERROR: Wrong number of arguments. load_movie() accepts a list of 3 args:'
            print '       [Movie_number, Movie_Variable, Moive_time'
            return -1
        else:
            movie_num = arg_list[0]
            movie_var = arg_list[1]
            movie_time= arg_list[2]

        self.load_movie_log(movie_num)
        
        #movie_log_arr = self.read_movie_log(movie_num)
        #param_dict = read_param(runnum)

        
        fname = self.run_id_dict['movie_path']+'/movie.'+movie_var+'.'+str(movie_num)
        fname = os.path.expanduser(fname)
        #NOTE: Changing Dir give factor of 2 time incresse
        #We are changing path to try to speed things up
        working_dir = os.getcwd()
        os.chdir(os.path.expanduser(self.run_id_dict['movie_path']))

        #NOTE: we are reading the whole movie file in one shot!
        # this seems wastefull
        print "Restoring Varible '"+movie_var+"' From File '"+fname+"'"
        byte_movie = np.fromfile(fname,dtype=np.dtype('int8'))
        arr_size = [self.param_dict['pex']*self.param_dict['nx'],self.param_dict['pey']*self.param_dict['ny']]
        #num_time_steps = len(byte_movie)/arr_size[0]/arr_size[1]

        working_dir
        os.chdir(working_dir)

# This seems to be working but we need to generalize for any file
# Also It would be good to have some kinda of print out talkting about
# How many movies there are and all that non sence.
        
#This is just doing it for the first time step, we can generlize later
        lmin = self.movie_log_dict[movie_var][movie_time][0]
        lmax = self.movie_log_dict[movie_var][movie_time][1]
        byte_ip1 = movie_time*arr_size[0]*arr_size[1]
        byte_ip2 = byte_ip1 + arr_size[0]*arr_size[1]

        print 'There are '+str(len(byte_movie)/arr_size[0]/arr_size[1])+ \
        ' movie files and you loaded number ' +str(movie_time+1)

        real_arr_1 = byte_movie[byte_ip1:byte_ip2]*(lmax-lmin)/255.0+ lmin


        return real_arr_1.reshape(arr_size[1],arr_size[0])
        



    def set_movie_arr(self):
        #Check the moive header type
        if self.param_dict['movie_header'] == '"movie2dC.h"':
            self.movie_arr = ['rho',
                              'jx','jy','jz',
                              'bx','by','bz',
                              'ex','ey','ez',
                              'ne',
                              'jex','jey','jez',
                              'pexx','peyy','pezz','pexy','peyz','pexz',
                              'ni',
                              'pixx','piyy','pizz','pixy','piyz','pixz']
        elif self.param_dict['movie_header'] == '"movie2dD.h"':
            self.movie_arr = ['rho',
                              'jx','jy','jz',
                              'bx','by','bz',
                              'ex','ey','ez',
                              'ne',
                              'jex','jey','jez',
                              'pexx','peyy','pezz','pexy','peyz','pexz',
                              'ni',
                              'jix','jiy','jiz',
                              'pixx','piyy','pizz','pixy','piyz','pixz']
        else:
            print 'This particular moive headder has not been coded! Fix it or talk to colby'

########################################################################################################################################################
##                                                                                                                                                     #
##     These following methods really dont need to be in this object. They could easly be classless or form an object of their own.                    #
##     It would be smart to seperate theses out from the run object. Please ocnsider doing this if you have free time colby.                           #
##     -Colby 2014.03.21                                                                                                                               #
##                                                                                                                                                     #
########################################################################################################################################################

#---------------------------------------------------------------------------------------------------------------
#   Method      : read_dump_file
# 
#   Args        : dump_index (is the middle 3 digets of the dump file. This corseponds to the processors)
#               : dump_num (is the last 3 digets of the dump file. This spesifies which run)
# 
#   BIG NOTE    : This assumes that we are looking at 2 D dump files! so file 1 is field file 
# 
#   Comment     : 
#---------------------------------------------------------------------------------------------------------------
    #def read_dump_file(self,dump_num,verbose):
    def read_dump_file(self,arg_list):

        if len(arg_list) < 2: 
            print 'ERROR: Wrong number of arguments. read_dump_file() accepts a list of 2 args:'
            print '       [dump_num, dump_index]'
            return -1
        else:
            dump_index = arg_list[0]
            dump_num = arg_list[1]
        if len(arg_list) > 2 and arg_list[2].lower() == 'v':
            verbose = 1
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
# Print each argument separately so caller doesn't need to
# stuff everything to be printed into a single string
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Right now we dont have somthing that points to where these are loacated, This should be coded in eventualy
# But conviently we can just use where the param is and go form there
        fname = os.path.expanduser(self.run_id_dict['param_path']).strip()
        scratch_sub = "/glade/scratch/colbyh"
        if fname.find("$SCRATCH") > -1:
            fname = fname[0:fname.find("$SCRATCH")]+scratch_sub+fname[fname.find("$SCRATCH")+8:]
        if fname[-1] == '/':
            fname=fname[0:-1]
# Colby this should likely be padded for entering numbers that do not have to be in 00X format
# Consider padding 1 method layer up
        fname = fname[0:fname.rfind('/')+1] + 'p3d-' + dump_index +'.' + dump_num
# Make sure that the file exsists and suguset alternetives to fix it
        try:
            f = open(fname, "rb")
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            print "ERROR: Could not open file. " + fname
            print "Possible Reasons:"
            print "     File does not exist"
            print "     File extention is wrong"
            print "     run_list.dat is not set properly (i.e. looking in the wrong directory)"
            return -1


# First we need to deal with special case of if it is a field file
# If the dump file we are trying to read is the first, we need to first read the fields and then the particles 
        if dump_index == '001':
            print 'NOT CODED YET'
            print "Reading Dump File '"+fname+"'"
            print "Reading Header: "
            header_chunksize=44 # Size of the header in bytes
            header_binary = f.read(header_chunksize)
            header = struct.unpack('<idd6i', header_binary)
            print "              : "+str(header)
            px = header[3]
            py = header[4]
            bufsize = header[-3]
            number_of_pey = header[-2]
            print 'bufsize = '+str(bufsize)
            print 'px = '+str(px)
            print 'py = '+str(py)

            dump_field_dict={}
            for field_var in ['ex','ey','ez','bx','by','bz']:
                dump_dat=[]
                for pey_current in range(py):
                    pad_head = struct.unpack('<i',f.read(4))[0]
                    dump_dat.append(np.fromfile(f,dtype='float64',count=pad_head/8)) # Float size times number of floats
                    pad_butt = struct.unpack('<i',f.read(4))[0]
                dump_dat = np.concatenate(dump_dat)
                dump_dat.shape = (py,px)
                self.dump_field_dict[field_var] = dump_dat
# You should relly wtright in a check to compare pex from param to what you find here
# Like they do in p3d

# Now we open 
        else:
            verboseprint("Reading Dump File '"+fname+"'")
            verboseprint("Reading Header: ")
            header_chunksize=44 # Size of the header in bytes
            header_binary = f.read(header_chunksize)
            header = struct.unpack('<idd6i', header_binary)
            verboseprint("              : "+str(header))
            bufsize = header[-3]
            number_of_pey = self.param_dict['pey']#header[-2]
            verboseprint('bufsize = '+str(bufsize))
            verboseprint('number of pey = '+str(number_of_pey))
            
        dt = np.dtype([('x', 'float32'), ('y', 'float32'), ('z', 'float32'),('vx', 'float32'), ('vy', 'float32'), ('vz', 'float32')])
        all_particles = [] 
        for species in range(2): 
            pad_head = struct.unpack('<i',f.read(4))[0]
            verboseprint('Note sure about the point of this number? ' +str(struct.unpack('<i',f.read(4))[0]))
            pad_butt = struct.unpack('<i',f.read(4))
            all_sub_species = []
            for current_sub_proc in range(number_of_pey):
                pad_head = struct.unpack('<i',f.read(4))[0]
                number_of_part_on_pe = struct.unpack('<i',f.read(4))[0]
                pad_butt = struct.unpack('<i',f.read(4))
                dump_dat=[]
                bufsize_lastcase = number_of_part_on_pe % bufsize
                verboseprint('Reading from proc number: '+str(current_sub_proc)+' Number of part on sub proc: '+str(number_of_part_on_pe))
                for current_sub_buffer in range(number_of_part_on_pe/bufsize): 
                    pad_head = struct.unpack('<i',f.read(4))[0]
                    #print 'Reading Buffer number: '+str(current_sub_buffer)+' Size of next set of bytes: '+str(pad_head)
# Colby Maybe try switching these two to see if it runs faster. The two should be Equivelent
#   1:
#;#                all_particles_from_file = np.append(all_particles_from_file,np.fromfile(f,dtype=dt,count=pad_head/(4*6))) # Float size times number of floats
#   2:
#;#                dump_dat = np.fromfile(f,dtype=dt,count=pad_head/(4*6)) # Float size times number of floats
#;#                all_particles_from_file = np.append(all_particles_from_file,dump_dat)
#   3:
                    dump_dat.append(np.fromfile(f,dtype=dt,count=pad_head/(4*6))) # Float size times number of floats
#   end
                    pad_butt = struct.unpack('<i',f.read(4))
                    pad_head = struct.unpack('<i',f.read(4))[0]
                    #print 'Reading Buffer number: '+str(current_sub_buffer)+' Size of next set of bytes: '+str(pad_head)+' !SKIPPED!'
                    np.fromfile(f,dtype='int64',count=pad_head/(8)) # 1 int8 and we probobly dont need the tag
                    pad_butt = struct.unpack('<i',f.read(4))
                # Special Case of the particles left over
                #   If you are looking hear to figure out an issue it could be that we do not check to make sure that
                #   this happens in reading the dump file. It is possible that the number of particles excatly fills
                #   up the buffer and you dont have this extra case. But I dont think this is likly to happen (1/ bufsize)
                #   First read the number of total particles on this PE, This will tell us how much our next byte size should be
                #print 'Number of particles in the final buffer: '+str(bufsize_lastcase)
                #   Next we read the data with the special size. NOTE this could be done in a cleaner way
                pad_head = struct.unpack('<i',f.read(4))[0]
                #print 'Reading Buffer number: '+str(number_of_part_on_pe/bufsize+1)+' Size of next set of bytes: '+str(pad_head)
                temp_dat = np.fromfile(f,dtype=dt,count=pad_head/(4*6)) # Float size times number of floats
                pad_butt = struct.unpack('<i',f.read(4))[0]
# Trim all of the extra zeros
                dump_dat.append(temp_dat[0:bufsize_lastcase])
# Appending temp dump_dat to all_particles
                #all_particles_from_file = np.append(all_particles_from_file,dump_dat)
# Now skip over the tags
                pad_head = struct.unpack('<i',f.read(4))[0]
                #print 'Reading Buffer number: '+str(number_of_part_on_pe/bufsize+1)+' Size of next set of bytes: '+str(pad_head)+' !SKIPPED!'
                np.fromfile(f,dtype='int64',count=pad_head/(8)) # 1 int8 and we probobly dont need the tag
                pad_butt = struct.unpack('<i',f.read(4))
                all_sub_species.append(np.concatenate(dump_dat))
            all_particles.append(all_sub_species)
        return all_particles

#---------------------------------------------------------------------------------------------------------------
#   Method      : read_fields_from_dump
# 
#   Args        : dump_index (is the middle 3 digets of the dump file. This corseponds to the processors)
#               : dump_num (is the last 3 digets of the dump file. This spesifies which run)
# 
#   BIG NOTE    : This assumes that we are looking at 2 D dump files! so file 1 is field file 
# 
#   Comment     : 
#---------------------------------------------------------------------------------------------------------------
    #def read_fields_from_dump(self,dump_num,verbose):
    def read_fields_from_dump(self,arg_list):

        if len(arg_list) < 1: 
            print 'ERROR: Wrong number of arguments. read_dump_file() accepts a list of 2 args:'
            print '       [dump_num, dump_index]'
            return -1
        else:
            dump_num = arg_list[0]
            dump_index = '001'
        if len(arg_list) > 2 and arg_list[2].lower() == 'v':
            verbose = 1
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
# Print each argument separately so caller doesn't need to
# stuff everything to be printed into a single string
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Right now we dont have somthing that points to where these are loacated, This should be coded in eventualy
# But conviently we can just use where the param is and go form there
        fname = os.path.expanduser(self.run_id_dict['param_path']).strip()
        scratch_sub = "/glade/scratch/colbyh"
        if fname.find("$SCRATCH") > -1:
            fname = fname[0:fname.find("$SCRATCH")]+scratch_sub+fname[fname.find("$SCRATCH")+8:]
        if fname[-1] == '/':
            fname=fname[0:-1]
# Colby this should likely be padded for entering numbers that do not have to be in 00X format
# Consider padding 1 method layer up
        fname = fname[0:fname.rfind('/')+1] + 'p3d-' + dump_index +'.' + dump_num
# Make sure that the file exsists and suguset alternetives to fix it
        try:
            f = open(fname, "rb")
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            print "ERROR: Could not open file. " + fname
            print "Possible Reasons:"
            print "     File does not exist"
            print "     File extention is wrong"
            print "     run_list.dat is not set properly (i.e. looking in the wrong directory)"
            return -1


# First we need to deal with special case of if it is a field file
# If the dump file we are trying to read is the first, we need to first read the fields and then the particles 
        print "Reading Dump File '"+fname+"'"
        print "Reading Header: "
        header_chunksize=44 # Size of the header in bytes
        header_binary = f.read(header_chunksize)
        header = struct.unpack('<idd6i', header_binary)
        print "              : "+str(header)
        px = header[3]
        py = header[4]
        bufsize = header[-3]
        number_of_pey = self.param_dict['pey'] #header[-2]
        print 'bufsize = '+str(bufsize)
        print 'px = '+str(px)
        print 'py = '+str(py)

        dump_field_dict={}
        for field_var in ['ex','ey','ez','bx','by','bz']:
            dump_dat=[]
            for pey_current in range(py):
                pad_head = struct.unpack('<i',f.read(4))[0]
                dump_dat.append(np.fromfile(f,dtype='float64',count=pad_head/8)) # Float size times number of floats
                pad_butt = struct.unpack('<i',f.read(4))[0]
            dump_dat = np.concatenate(dump_dat)
            dump_dat.shape = (py,px)
            dump_field_dict[field_var] = dump_dat
# Now we open 
        return dump_field_dict


#---------------------------------------------------------------------------------------------------------------
#   Method      : get_part_in_box
#
#   Discription : This method accepts a point and a width in simulation units (c/wpi) to define a box.
#               : In that box we bin all of the particles to form the effective distrobution function
#
#   Args        : location [x,y] ( where you want the center of you box to be located at)
#               : width [x,y] (the width of the box to bin particles 
#               : dump_num (This spesifies the particular runs dump file 
#
#   Comments    : It would be pretty easy and potential usefull to allow this to wrap around the edges
#               : so we can pick zero as a boundry and the code will know what todo.
#---------------------------------------------------------------------------------------------------------------
    #def get_part_in_box([location, width]):
    def get_part_in_box(self,arg_list):
# First we handel the input
        if len(arg_list) < 2: 
            print 'ERROR: Wrong number of arguments. read_dump_file() accepts a list of 2 args:'
            print '       [location, width,dump id, ?verbose?]'
            return -1
        else:
            if len(arg_list[0]) < 2: 
                print 'ERROR: location set wrong: should be arg[0] = [x,y]'
                return -1
            else:
                x_simUnit = arg_list[0][0]
                y_simUnit = arg_list[0][1]
            if isinstance(arg_list[1],float): # Square box is assumed
                x_width_simUnit = arg_list[1]
                y_width_simUnit = arg_list[1]
            else:
                x_width_simUnit = arg_list[1][0]
                y_width_simUnit = arg_list[1][1]
            dump_num = arg_list[2]
        if len(arg_list) > 3 and len(arg_list[3]) > 0:
            if arg_list[3][0].lower() == 'v':
                verbose = 1
                vflag = arg_list[3][1:]
        else: 
            verbose = 0
            vflag = ''
        if verbose:
            def verboseprint(*args):
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Load the param, because we want to know which dump file will have which xvalues
        self.load_param()
        number_of_xprocs = self.param_dict['pex']
        number_of_yprocs = self.param_dict['pey']
        lx_simUnit = self.param_dict['lx']
        ly_simUnit = self.param_dict['ly']
# Figure out which set of processors we are on
        x_lowerbound = x_simUnit - x_width_simUnit/2.
        x_upperbound = x_simUnit + x_width_simUnit/2.
        y_lowerbound = y_simUnit - y_width_simUnit/2.
        y_upperbound = y_simUnit + y_width_simUnit/2.

# BIGNOTE: This seems iffy you should come back and double check this colby. It doesnt make sence that we should have to add 1
        x_proc_lowerbound = int(np.floor(1.0*number_of_xprocs*x_lowerbound/lx_simUnit))+1
        y_proc_lowerbound = int(np.floor(1.0*number_of_yprocs*y_lowerbound/ly_simUnit))
        x_proc_upperbound = int(np.floor(1.0*number_of_xprocs*x_upperbound/lx_simUnit))+1
        y_proc_upperbound = int(np.floor(1.0*number_of_yprocs*y_upperbound/ly_simUnit))

        if x_proc_lowerbound > x_proc_upperbound:
            verboseprint('Lower Bound greater than upper bound! That is obviously an issue!')
            return -1

        xprocs_2load = range(x_proc_lowerbound,x_proc_upperbound+1)
        yprocs_2load = range(y_proc_lowerbound,y_proc_upperbound+1)
        
        verboseprint('The x processors we will be loading (i.e. the dump files) are: {}'.format(xprocs_2load))
        verboseprint('The y processors we will be loading (i.e. the sub arrays) are: {}'.format(yprocs_2load))
        verboseprint('That means we have {} processors to load and you can expect an aprox. {:.2f} min wait time'.format(
              len(xprocs_2load)*len(yprocs_2load),1.41*len(xprocs_2load)*len(yprocs_2load)*4./60.))
# Load in the appropriate Processors
        temp_dump_pruned =[[],[]] # List to hold all the particles
        #first for loop over px
        for xprocs_index in xprocs_2load:
            dump_dat_dict = {}
            dump_index = str(xprocs_index)
# Assigen the correct string format for the dump file
            if len(dump_index) < 3:
                if len(dump_index) < 2:
                    dump_index = '00'+dump_index
                else:
                    dump_index = '0'+dump_index
            verboseprint('Loading in xproc number '+dump_index)
            temp_dump_dat = self.read_dump_file([dump_index,dump_num,vflag])
# We need to looop over Ions and Electrons
            for species in range(2):
                if species ==0:
                    verboseprint('\tSelecting Ions')
                else:
                    verboseprint('\tSelecting Electrons')
# second for loop over the py
# also just doing electron for right now
                for yprocs_index in yprocs_2load:

                    temp_dump_yproc = temp_dump_dat[species][yprocs_index]
# You only need to sort if you are on the edge processors
                    if yprocs_index == yprocs_2load[0] or yprocs_index == yprocs_2load[-1]: 
                        verboseprint('\t\tSorting yproc number '+str(yprocs_index))
                        sorted_index = temp_dump_dat[species][yprocs_index].argsort(order='y')
                        temp_dump_yproc = temp_dump_dat[species][yprocs_index][sorted_index]
# Here we need kind of a complecated if structure to get all the poible cases since
# we are scaning over muliple processors.
# If you are on your first y processor then you need to find a lower boundry
                    if yprocs_index == yprocs_2load[0]: 
                        verboseprint('\t\t\tFinding lower yboundry index ')
                        lower_yboundry_index = np.searchsorted(temp_dump_yproc['y'],y_lowerbound)
                    else:
                        lower_yboundry_index = 0#np.searchsorted(temp_dump_yproc['y'],y_lowerbound)
# If you are on your last y processor then you need to find a upper boundry
                    if yprocs_index == yprocs_2load[-1]: 
                        verboseprint('\t\t\tFinding upper yboundry index ')
                        upper_yboundry_index = np.searchsorted(temp_dump_yproc['y'],y_upperbound)
                    else:
                        upper_yboundry_index = -1#np.searchsorted(temp_dump_yproc['y'],y_upperbound)
                    # You only need to sort if you are on the edge processors
                    temp_dump_xproc = temp_dump_yproc[lower_yboundry_index:upper_yboundry_index]
                    if xprocs_index == xprocs_2load[0] or xprocs_index == xprocs_2load[-1]: 
                        verboseprint('\t\tNow sorting x values for remaing data')
                        sorted_index = temp_dump_xproc.argsort(order='x')
                        temp_dump_xproc = temp_dump_xproc[sorted_index] 
# If you are on your first x processor then you need to find a lower boundry
                    if xprocs_index == xprocs_2load[0]: 
                        verboseprint('\t\t\tFinding lower xboundry index ')
                        lower_xboundry_index = np.searchsorted(temp_dump_xproc['x'],x_lowerbound)
                    else:
                        lower_xboundry_index = 0#np.searchsorted(temp_dump_xproc['x'],x_lowerbound)
# If you are on your last x processor then you need to find a upper boundry
                    if xprocs_index == xprocs_2load[-1]: 
                        verboseprint('\t\t\tFinding upper xboundry index ')
                        upper_xboundry_index = np.searchsorted(temp_dump_xproc['x'],x_upperbound)
                    else: 
                        upper_xboundry_index = -1#np.searchsorted(temp_dump_xproc['x'],x_upperbound)
                    temp_dump_pruned[species].append(temp_dump_xproc[lower_xboundry_index:upper_xboundry_index])

        temp_dump_pruned[0] = np.concatenate(temp_dump_pruned[0])
        temp_dump_pruned[1] = np.concatenate(temp_dump_pruned[1])
        verboseprint('Total particles in box are: ' + str(len(temp_dump_pruned[0])))
        return temp_dump_pruned

#---------------------------------------------------------------------------------------------------------------
#   Method      : vdist_1d
#
#   Discription : This method accepts a point and a width in simulation units (c/wpi) to define a box.
#               : In that box we bin all of the particles to form the effective distrobution function
#
#   Args        : location [x,y] ( where you want the center of you box to be located at)
#               : width [x,y] (the width of the box to bin particles 
#               : dump_num (This spesifies the particular runs dump file 
#
#   Comments    : It would be pretty easy and potential usefull to allow this to wrap around the edges
#               : so we can pick zero as a boundry and the code will know what todo.
#---------------------------------------------------------------------------------------------------------------
    #def vdist_1d([location, width,dump_index]):
    def vdist_1d(self,r_simUnit=[76.8,76.8],x_width_simUnit=1.0,dump_num='000',bins=200,vflag=''):
# First we handel the input
        x_simUnit = r_simUnit[0]
        y_simUnit = r_simUnit[0]
        if isinstance(x_width_simUnit,list): # Square box is assumed
            y_width_simUnit = x_width_simUnit[1]
            x_width_simUnit = x_width_simUnit[0]
        else:
            y_width_simUnit = x_width_simUnit
        if len(vflag) > 0 and vflag[0].lower() == 'v':
            verbose = 1
            vflag = vflag[1:]
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Calling get particles in box to make the vdist
        verboseprint('Reading Ions and Electrons from the Dump File')
        particles = self.get_part_in_box([r_simUnit,[x_width_simUnit,y_width_simUnit],dump_num,vflag])

# Here we are generating 3 histograms from the particles we read
        verboseprint('Generating Histograms')
        return_histx=[0.,0.]
        return_histy=[0.,0.]
        return_histz=[0.,0.]
        return_hist_dict={}
        centerx=[0.,0.]
        centery=[0.,0.]
        centerz=[0.,0.]

# the vx hist
        return_histx[0],centerx[0] = np.histogram(particles[0]['vx'], bins=bins)
        return_histx[1],centerx[1] = np.histogram(particles[1]['vx'], bins=bins)
        centerx[0] = (centerx[0][1:]+centerx[0][:-1])/2.
        centerx[1] = (centerx[1][1:]+centerx[1][:-1])/2.
        return_hist_dict['vx'] = [return_histx,centerx]
# the vy hist
        return_histy[0],centery[0] = np.histogram(particles[0]['vy'], bins=bins)
        return_histy[1],centery[1] = np.histogram(particles[1]['vy'], bins=bins)
        centery[0] = (centery[0][1:]+centery[0][:-1])/2.
        centery[1] = (centery[1][1:]+centery[1][:-1])/2.
        return_hist_dict['vy'] = [return_histy,centery]
# the vz hist
        return_histz[0],centerz[0] = np.histogram(particles[0]['vz'], bins=bins)
        return_histz[1],centerz[1] = np.histogram(particles[1]['vz'], bins=bins)
        centerz[0] = (centerz[0][1:]+centerz[0][:-1])/2.
        centerz[1] = (centerz[1][1:]+centerz[1][:-1])/2.
        return_hist_dict['vz'] = [return_histz,centerz]

        return return_hist_dict

#---------------------------------------------------------------------------------------------------------------
#   Method      : vdist_1d_par
#
#   Discription : This method accepts a point and a width in simulation units (c/wpi) to define a box.
#               : In that box we bin all of the particles to form the effective distrobution function
#
#   Args        : location [x,y] ( where you want the center of you box to be located at)
#               : width [x,y] (the width of the box to bin particles 
#               : dump_num (This spesifies the particular runs dump file 
#
#   Comments    : It would be pretty easy and potential usefull to allow this to wrap around the edges
#               : so we can pick zero as a boundry and the code will know what todo.
#---------------------------------------------------------------------------------------------------------------
    #def vdist_1d_par([location, width,dump_index]):
    def vdist_1d_par(self,r_simUnit=[76.8,76.8],x_width_simUnit=1.0,dump_num='000',bins=51,vflag=''):
# First we handel the input
        x_simUnit = r_simUnit[0]
        y_simUnit = r_simUnit[0]
        if isinstance(x_width_simUnit,list): # Square box is assumed
            y_width_simUnit = x_width_simUnit[1]
            x_width_simUnit = x_width_simUnit[0]
        else:
            y_width_simUnit = x_width_simUnit
        if len(vflag) > 0 and vflag[0].lower() == 'v':
            verbose = 1
            vflag = vflag[1:]
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Calling get particles in box to make the vdist
        verboseprint('Reading Ions and Electrons from the Dump File')
        particles = self.get_part_in_box([r_simUnit,[x_width_simUnit,y_width_simUnit],dump_num,vflag])
# Reading in fields to calculate vpar
        verboseprint('Reading in the Fields form the Dump File')
        dump_field_dict = self.read_fields_from_dump([dump_num])
# Now there are two ways to do this, a faster and a slower
# Faster: just take the average B field and and use that
#         for every particle
# Slower: Use an interpolated Bfield for each point
#
# Right now im only coding the faster one
        verboseprint('Calculating B field')
        
        bx_interp = interp_field(dump_field_dict['bx'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        by_interp = interp_field(dump_field_dict['by'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        bz_interp = interp_field(dump_field_dict['bz'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        bmag_interp = (bx_interp**2+by_interp**2+bz_interp**2)**(.5)

        b_perp1y = -1.*bz_interp/(by_interp**2+bz_interp**2)**(.5)
        b_perp1z = by_interp/(by_interp**2+bz_interp**2)**(.5)

        b_perp2x = (by_interp*b_perp1z - bz_interp*b_perp1y)
        b_perp2y = (-1.*bx_interp*b_perp1z)
        b_perp2z = (bx_interp*b_perp1y)
        b_perpmag = ((by_interp*b_perp1z - bz_interp*b_perp1y)**2+(bx_interp*b_perp1z)**2+(bx_interp*b_perp1y)**2)**(.5)
        b_perp2x = b_perp2x/b_perpmag
        b_perp2y = b_perp2y/b_perpmag
        b_perp2z = b_perp2z/b_perpmag
        
        verboseprint('Rotating Velocties')
# Also just doing the electons to start off with 
        vpar = (bx_interp*particles[1]['vx']+by_interp*particles[1]['vy']+bz_interp*particles[1]['vz'])/bmag_interp
        vperp1 = particles[1]['vy']*b_perp1y+particles[1]['vz']*b_perp1z
        vperp2 = particles[1]['vx']*b_perp2x+particles[1]['vy']*b_perp2y+particles[1]['vz']*b_perp2z

        verboseprint('Generating Histograms')

        return_hist_dict = {}
        return_hist = [0.,0.]
        extent = [[0.,0.,0.,0.],[0.,0.,0.,0.]]
        return_hist[0],xedge,yedge = np.histogram2d(particles[0]['vx'], particles[0]['vy'], bins=bins)
        extent[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_hist[1],extent[1] = np.histogram(vpar,bins=bins)
        #extent[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_hist_dict = [return_hist[1],(extent[1][1:]+extent[1][:-1])/2.]
#@# # the vx vs vy hist
#@#         return_hist[0],xedge,yedge = np.histogram2d(particles[0]['vx'], particles[0]['vy'], bins=bins)
#@#         extent[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist[1],xedge,yedge = np.histogram2d(particles[1]['vx'], particles[1]['vy'], bins=bins)
#@#         extent[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist_dict['vxy'] = [return_hist,extent]
#@# # the vx vs vz hist
#@#         return_hist[0],xedge,yedge = np.histogram2d(particles[0]['vx'], particles[0]['vz'], bins=bins)
#@#         extent[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist[1],xedge,yedge = np.histogram2d(particles[1]['vx'], particles[1]['vz'], bins=bins)
#@#         extent[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist_dict['vxz'] = [return_hist,extent]
#@# # the vy vs vz hist
#@#         return_hist[0],xedge,yedge = np.histogram2d(particles[0]['vy'], particles[0]['vz'], bins=bins)
#@#         extent[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist[1],xedge,yedge = np.histogram2d(particles[1]['vy'], particles[1]['vz'], bins=bins)
#@#         extent[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
#@#         return_hist_dict['vyz'] = [return_hist,extent]

        return return_hist_dict

#---------------------------------------------------------------------------------------------------------------
#   Method      : vdist_2d
#
#   Discription : This method accepts a point and a width in simulation units (c/wpi) to define a box.
#               : In that box we bin all of the particles to form the effective distrobution function
#
#   Args        : location [x,y] ( where you want the center of you box to be located at)
#               : width [x,y] (the width of the box to bin particles 
#               : dump_num (This spesifies the particular runs dump file 
#
#   Comments    : It would be pretty easy and potential usefull to allow this to wrap around the edges
#               : so we can pick zero as a boundry and the code will know what todo.
#---------------------------------------------------------------------------------------------------------------
    #def vdist_2d([location, width,dump_index]):
    def vdist_2d(self,r_simUnit=[76.8,76.8],x_width_simUnit=1.0,dump_num='000',bins=51,vflag=''):
# First we handel the input
        x_simUnit = r_simUnit[0]
        y_simUnit = r_simUnit[0]
        if isinstance(x_width_simUnit,list): # Square box is assumed
            y_width_simUnit = x_width_simUnit[1]
            x_width_simUnit = x_width_simUnit[0]
        else:
            y_width_simUnit = x_width_simUnit
        if len(vflag) > 0 and vflag[0].lower() == 'v':
            verbose = 1
            vflag = vflag[1:]
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Calling get particles in box to make the vdist
        verboseprint('Reading Ions and Electrons from the Dump File')
        particles = self.get_part_in_box([r_simUnit,[x_width_simUnit,y_width_simUnit],dump_num,vflag])

# Here we are generating 3 histograms from the particles we read
        verboseprint('Generating Histograms')
        return_hist_dict = {}
        return_histxy = [0.,0.]
        extentxy = [[0.,0.,0.,0.],[0.,0.,0.,0.]]
        return_histxz = [0.,0.]
        extentxz = [[0.,0.,0.,0.],[0.,0.,0.,0.]]
        return_histyz = [0.,0.]
        extentyz = [[0.,0.,0.,0.],[0.,0.,0.,0.]]

# the vx vs vy hist
        return_histxy[0],xedge,yedge = np.histogram2d(particles[0]['vx'], particles[0]['vy'], bins=bins)
        extentxy[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_histxy[1],xedge,yedge = np.histogram2d(particles[1]['vx'], particles[1]['vy'], bins=bins)
        extentxy[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_hist_dict['vxy'] = [return_histxy,extentxy]
# the vx vs vz hist
        return_histxz[0],xedge,yedge = np.histogram2d(particles[0]['vx'], particles[0]['vz'], bins=bins)
        extentxz[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_histxz[1],xedge,yedge = np.histogram2d(particles[1]['vx'], particles[1]['vz'], bins=bins)
        extentxz[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_hist_dict['vxz'] = [return_histxz,extentxz]
# the vy vs vz hist
        return_histyz[0],xedge,yedge = np.histogram2d(particles[0]['vy'], particles[0]['vz'], bins=bins)
        extentyz[0] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_histyz[1],xedge,yedge = np.histogram2d(particles[1]['vy'], particles[1]['vz'], bins=bins)
        extentyz[1] = [xedge[0],xedge[-1],yedge[0],yedge[-1]]
        return_hist_dict['vyz'] = [return_histyz,extentyz]

        return return_hist_dict

#---------------------------------------------------------------------------------------------------------------
#   Method      : vdist_2d_par
#
#   Discription : This method accepts a point and a width in simulation units (c/wpi) to define a box.
#               : In that box we bin all of the particles to form the effective distrobution function
#
#   Args        : location [x,y] ( where you want the center of you box to be located at)
#               : width [x,y] (the width of the box to bin particles 
#               : dump_num (This spesifies the particular runs dump file 
#
#   Returns     : return_hist_dict['axis'][i/e][hist_array]
#               :   'axis'  slecets the data for the 2d projection of the distabution function 
#                   'axis' = 'parperp1', 'parperp1', 'perp1perp2'
#                   i/e is an int that selects either the electron or ion data. i = 0, e = 1
#                   The rest is just an object that is returned directly from the histogram2d method
#
#
#   Comments    : It would be pretty easy and potential usefull to allow this to wrap around the edges
#               : so we can pick zero as a boundry and the code will know what todo.
#---------------------------------------------------------------------------------------------------------------
    #def vdist_2d_par([location, width,dump_index]):
    def vdist_2d_par(self,r_simUnit=[76.8,76.8],x_width_simUnit=1.0,dump_num='000',bins=51,vflag=''):
# First we handel the input
        x_simUnit = r_simUnit[0]
        y_simUnit = r_simUnit[0]
        if isinstance(x_width_simUnit,list): # Square box is assumed
            y_width_simUnit = x_width_simUnit[1]
            x_width_simUnit = x_width_simUnit[0]
        else:
            y_width_simUnit = x_width_simUnit
        if len(vflag) > 0 and vflag[0].lower() == 'v':
            verbose = 1
            vflag = vflag[1:]
        else: 
            verbose = 0
        if verbose:
            def verboseprint(*args):
                for arg in args:
                    print arg,
                print
        else:   
            verboseprint = lambda *a: None      # do-nothing

# Calling get particles in box to make the vdist
        verboseprint('Reading Ions and Electrons from the Dump File')
        particles = self.get_part_in_box([r_simUnit,[x_width_simUnit,y_width_simUnit],dump_num,vflag])
# Reading in fields to calculate vpar
        verboseprint('Reading in the Fields form the Dump File')
        dump_field_dict = self.read_fields_from_dump([dump_num])
# Now there are two ways to do this, a faster and a slower
# Faster: just take the average B field and and use that
#         for every particle
# Slower: Use an interpolated Bfield for each point
#
# Right now im only coding the faster one
        verboseprint('Calculating B field')
        
        bx_interp = interp_field(dump_field_dict['bx'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        by_interp = interp_field(dump_field_dict['by'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        bz_interp = interp_field(dump_field_dict['bz'],self.param_dict['lx'],self.param_dict['ly'],r_simUnit[0],r_simUnit[1])
        bmag_interp = (bx_interp**2+by_interp**2+bz_interp**2)**.5

        if by_interp > 0.:
            b_perp1x = 0.
            b_perp1y = -1.*bz_interp/(bz_interp**2 + by_interp**2)**(.5)
            b_perp1z = by_interp/(bx_interp**2 + by_interp**2)**(.5)
        else:
            b_perp1x = 0.
            b_perp1y = bz_interp/(bz_interp**2 + by_interp**2)**(.5)
            b_perp1z = -1.*by_interp/(bx_interp**2 + by_interp**2)**(.5)

        b_perp2x = (by_interp*b_perp1z - bz_interp*b_perp1y)
        b_perp2y = (bz_interp*b_perp1x - bx_interp*b_perp1z)
        b_perp2z = (bx_interp*b_perp1y - by_interp*b_perp1x)
        b_perpmag = (b_perp2x**2+b_perp2y**2+b_perp2z**2)**.5
        b_perp2x = b_perp2x/b_perpmag
        b_perp2y = b_perp2y/b_perpmag
        b_perp2z = b_perp2z/b_perpmag

        verboseprint('Rotating Velocties')
# Also just doing the electons to start off with 
        vpar_i = (bx_interp*particles[0]['vx']+by_interp*particles[0]['vy']+bz_interp*particles[0]['vz'])/bmag_interp
        vperp1_i = particles[0]['vx']*b_perp1x+particles[0]['vy']*b_perp1y+particles[0]['vz']*b_perp1z
        vperp2_i = particles[0]['vx']*b_perp2x+particles[0]['vy']*b_perp2y+particles[0]['vz']*b_perp2z

        vpar_e = (bx_interp*particles[1]['vx']+by_interp*particles[1]['vy']+bz_interp*particles[1]['vz'])/bmag_interp
        vperp1_e = particles[1]['vx']*b_perp1x+particles[1]['vy']*b_perp1y+particles[1]['vz']*b_perp1z
        vperp2_e = particles[1]['vx']*b_perp2x+particles[1]['vy']*b_perp2y+particles[1]['vz']*b_perp2z

        verboseprint('Generating Histograms')

        return_hist_dict = {}
        
        return_hist_dict['parperp1'] = [np.histogram2d(vperp1_i,vpar_i, bins=bins),np.histogram2d(vperp1_e,vpar_e, bins=bins)]
        return_hist_dict['parperp2'] = [np.histogram2d(vperp2_i,vpar_i, bins=bins),np.histogram2d(vperp2_e,vpar_e, bins=bins)]
        return_hist_dict['perp1perp2'] = [np.histogram2d(vperp2_i,vperp1_i, bins=bins),np.histogram2d(vperp2_e,vperp1_e, bins=bins)]

        return return_hist_dict



#---------------------------------------------------------------------------------------------------------------
#   Method      : interp_field
#
#   Discription : This method takes a field and a floating point, and returns the linear fit value 
#               : between the grid points
#
#   Args        : field  The field you are interpolating
#               : xpoint The xpoint to interpolate at
#               : ypoint The ypoint to interpolate at
#
#   Comments    : I think this is working ok? It would be smart to make this an object method that just reads
#               : the internally saved field. so CODE IN THE FUTURE
#---------------------------------------------------------------------------------------------------------------
def interp_field(field,lx,ly,xpoint,ypoint):
    nx = len(field[0,:])
    ny = len(field[:,0])
    ip = int(np.floor(1.0*xpoint/lx*nx))
    jp = int(np.floor(1.0*ypoint/ly*ny))
    weight_x = 1.0*xpoint/lx*nx - np.floor(1.0*xpoint/lx*nx)
    weight_y = 1.0*ypoint/ly*ny - np.floor(1.0*ypoint/ly*ny)
    return np.array([(1.-weight_x)*(1.-weight_y)*field[jp,ip] + (weight_x)*(1.-weight_y)*field[jp+1,ip] \
           + (1.-weight_x)*(weight_y)*field[jp,ip+1]+ (weight_x)*(weight_y)*field[jp+1,ip+1]])
    


#Orphaned method that I use in load param but not quite sure how to fit it in
def convert(val):
    constructors = [int, float, str]
    for c in constructors:
        try:
            return c(val)
        except ValueError:
            pass
def load_pat_ct():
    cdict3 = {'red':  ((0.0, 0.0, 0.0),
                       (0.25,0.0, 0.0),
                       (0.5, 0.8, 1.0),
                       (0.75,1.0, 1.0),
                       (1.0, 0.4, 1.0)),
             'green': ((0.0, 0.0, 0.0),
                       (0.25,0.0, 0.0),
                       (0.5, 0.9, 0.9),
                       (0.75,0.0, 0.0),
                       (1.0, 0.0, 0.0)),
             'blue':  ((0.0, 0.0, 0.4),
                       (0.25,1.0, 1.0),
                       (0.5, 1.0, 0.8),
                       (0.75,0.0, 0.0),
                       (1.0, 0.0, 0.0))
    }

# set_local()
#This Method should take all of the items in the dictonary
# and set them as actual varibles. Note that this is redudant
# and does not fit well with the genral structural idea of the
# code, but it is a convention that I picked up from idl and
# I would like it in this

def set_local(run): 
#God bless python and how powerfull it is
    #This is easy to code just go through every key in your movie_dict
    # and use locals()[key] = movie_dict[key]
    # and your done. Note we are waiting to better implement other parts
    # Note we should just adda new variable to movie_dict when we create it
    return 'not coded'


#NOTE: I do not what to have to retype this if I decide to sue this later!
###            self.movie_dict= {'rho':0,
###                              'jx':1,'jy':2,'jz':3,
###                              'bx':4,'by':5,'bz':4,
###                              'ex':7,'ey':8,'ez':9,
###                              'ne':10,
###                              'jex':11,'jey':12,'jez':13,
###                              'pexx':14,'peyy':15,'pezz':16,'pexy':17,'peyz':18,'pexz':19,
###                              'ni':20,
###                              'pixx':21,'piyy':22,'pizz':23,'pixy':24,'piyz':25,'pixz':26}

###        elif param_dict['movie_header'] == '"movie2dD.h"':
###            self.movie_dict= {'rho':0,
###                              'jx':1,'jy':2,'jz':3,
###                              'bx':4,'by':5,'bz':4,
###                              'ex':7,'ey':8,'ez':9,
###                              'ne':10,
###                              'jex':11,'jey':12,'jez':13,
###                              'pexx':14,'peyy':15,'pezz':16,'pexy':17,'peyz':18,'pexz':19,
###                              'ni':20,
###                              'jix':21,'jiy':22,'jiz':23,
###                              'pixx':24,'piyy':25,'pizz':26,'pixy':27,'piyz':28,'pixz':29}
