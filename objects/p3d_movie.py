########################################################################################################################################################
########################################################################################################################################################
#                                                                                                                                                      #
#                                                 Python Progs :  p3d_movie.py                                                                         #
#                                                 Aruthor      :  Colby Haggerty                                                                       #
#                                                 Date         :  2014.05.08                                                                           #
#                                                                                                                                                      #
#                                                                                                                                                      #
########################################################################################################################################################
### Discription:
#
#       p3d_movie class is a movie object to be handled by p3d_run. This object keeps all of the information for a  
#       given movie. We have seperated this from the p3d_object to keep things neatter and cleaner. The plan is then
#       apply this same idea to the dump files. NOTE there may be a time trade off issue between this and doing every
#       thing together, but i dont think that will be an issue.
#

import os
import datetime
import numpy as np
import struct
from scipy.io.idl import readsav

class p3d_movie(object):
    """p3d_run object """

    def __init__(self, movie_path, movie_num, param_dict): 
        """ Initilazition Routine for the p3d_run object

        Fill in method discription

        @param movie_path   : the path to the set of movies you are interested in
        @param movie_num    : The number identive which set of movies you want to look at (which restart of the run)
        @param param_dict   : The dictonary of the param file associated with this run. It should be passed from the p3d_run object

        @return: @todo

        Example  :

        Creation
        :
        2013-05-08
        11:21:19.671182
        """

        if movie_num/10 > 1:
            if movie_num/100 > 1:
                self.movie_num_str = str(movie_num)
            else: self.movie_num_str = '0'+str(movie_num)
        else:  self.movie_num_str = '00'+str(movie_num)

        self.movie_path = movie_path
        self.movie_num = movie_num
        self.param_dict = param_dict

        self.set_movie_arr()

        self.movie_log_dict = {}
        self.num_of_times = -1
        self.load_movie_log()

#Colby you need to figure out a way to make sure that
# the path is ok this should likly be done one level up.

    def load_movie_log(self):
#OK So they new way we are doing runs is that each run will be as follows:
#       reconnNUM_L
# Where NUM is the run number and L coresponds to the restarts
# So we are going to need a way to distinguish how many sets of dump files
# come from a run. Right now lets only assume there is one and we can expand
# this at a later time


        #Set moive.log path

        fname = self.movie_path+'/movie.log.'+self.movie_num_str
        fname = os.path.expanduser(fname)
        print "Loading movie.log file '%s'"%fname
        #Read moive.log
        movie_log_arr = np.loadtxt(fname) 
        self.num_of_times = len(movie_log_arr)/len(self.movie_arr)
        print "movie.log '%s' has %i time slices"%(fname,self.num_of_times)
        
        for n in range(len(self.movie_arr)):
            self.movie_log_dict[self.movie_arr[n]] = []
        for n in range(len(movie_log_arr)):
            self.movie_log_dict[self.movie_arr[n%len(self.movie_arr)]].append(movie_log_arr[n,:]) 

# STRUCTURE OF movie_log_dict{}
#   movie_log_dict is a dictionary of all the of the varibles that could be read in a movie file
#   you pass the standered name of the varible as a string and you get back an array.
#   in the array each element coresponds to a diffrent time slice
#   so      movie.movie_log_dict['bz'] = [


    def set_movie_arr(self):
        #Check the moive header type
        if self.param_dict['movie_header'] == '"movie2dC.h"':
# Please NOTE, These are in an order, please do not switch around unless you want bugs
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
        

#---------------------------------------------------------------------------------------------------------------
#   Method: load_movie
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_var (to identify which varible you want to read)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
    #def load_movie(self,movie_num,movie_var,movie_time):
    def load_movie(self,time=0,var='bz'):
        """ A method to load a particular value for a given time 

        Fill in method discription

        @return: @todo

        Exemple  :

        Creation
        :
        2014-06-16
        """
       
        if (var not in self.movie_arr): 
            'Varable %s not found in movie_arr. Nothing was loaded!'%var
            return -1
        fname = self.movie_path+'/movie.'+var+'.'+self.movie_num_str
        fname = os.path.expanduser(fname)
        print "Loading movie.log file '%s'"%fname

        #Read moive.log
        #working_dir = os.getcwd()
        #os.chdir(os.path.expanduser(self.run_id_dict['movie_path']))

        nex = self.param_dict['pex']*self.param_dict['nx']
        ney = self.param_dict['pey']*self.param_dict['ny']

        #NOTE: we are reading the whole movie file in one shot!
        # this seems wastefull
        print "Restoring Varible '"+var+"' From File '"+fname+"'"


        fp = np.memmap(fname, dtype='int8', mode='r',shape=(self.num_of_times,ney,nex)) 
        byte_arr = np.fromfile(fname,dtype='int8')
        byte_arr = byte_arr.reshape(self.num_of_times,ney,nex) 


        #byte_movie = np.fromfile(fname,dtype=np.dtype('int8'))
        #arr_size = [self.param_dict['pex']*self.param_dict['nx'],self.param_dict['pey']*self.param_dict['ny']]
        #num_time_steps = len(byte_movie)/arr_size[0]/arr_size[1]
        #working_dir
        #os.chdir(working_dir)

# This seems to be working but we need to generalize for any file
# Also It would be good to have some kinda of print out talkting about
# How many movies there are and all that non sence.
        
#This is just doing it for the first time step, we can generlize later
        lmin = np.array(self.movie_log_dict[var])[:,0]
        lmax = np.array(self.movie_log_dict[var])[:,1]
        #byte_ip1 = movie_time*arr_size[0]*arr_size[1]
        #byte_ip2 = byte_ip1 + arr_size[0]*arr_size[1]

        #print 'There are '+str(len(byte_movie)/arr_size[0]/arr_size[1])+ \
        #' movie files and you loaded number ' +str(movie_time+1)

        return_arr = fp[time]*(lmax[time]-lmin[time])/255.0+ lmin[time]


        #return real_arr_1.reshape(arr_size[1],arr_size[0])
        #return np.transpose(return_arr)
        #return return_arr
        return byte_arr
        


