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
import glob
from scipy.io.idl import readsav

class p3d_movie(object):
    """p3d_run object """

    def __init__(self, movie_path, param_dict, movie_num=-1): 
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
        self._set_local_flag = False

        if movie_path.strip()[-1] == '/': self.movie_path = movie_path[:-1].strip()
        else: self.movie_path = movie_path
        self.movie_num = movie_num
        self.param_dict = param_dict

        if movie_num < 0: movie_num = self._movie_num_options()

        if movie_num/10 > 0:
            if movie_num/100 > 0:
                self.movie_num_str = str(movie_num)
            else: 
                self.movie_num_str = '0'+str(movie_num)
        else:  self.movie_num_str = '00'+str(movie_num)


        self._set_movie_arr()

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



#---------------------------------------------------------------------------------------------------------------
#   Method: load_movie
#   Args  : movie_num (to identify which of the posible several movie files to read from)
#         : movie_var (to identify which varible you want to read)
#         : movie_time (to identify which slice of time should be read)
#       This accepts the run name idetifies the coresponding
#       information in the run_list.dat file.
#---------------------------------------------------------------------------------------------------------------
    #def load_movie(self,movie_num,movie_var,movie_time):
    def load_movie(self,time=-1,var='NOT_SET',local=False):
        """ A method to load a particular value for a given time 

        Load movie files for a given set of varibles.
        You can pass as a list, or a single string, or a keyword all

        @return: @todo

        Exemple  :

        Creation
        :
        2014-06-16
        """
        
        if type(var) is not list: 
            if var.lower() == 'all': var_arr = self.movie_arr
            else: var_arr = [var]
        else: var_arr = var
        return_dict = {}
        for cosa in var_arr:
            if (cosa not in self.movie_arr): 
                print 'Varable %s not found in movie_arr. Nothing was loaded!'%cosa
                cosa = raw_input('Please Enter a Varible: ')
            if (cosa not in self.movie_arr): 
                print 'Varable %s not found in movie_arr. Nothing was loaded!'%cosa
                print 'You dont get a second try!'
                return -1
            if (time < 0 or time > self.num_of_times - 1):
                print 'Time %s out of range. [0,%i]'%(time,self.num_of_times-1)
                time = int(raw_input('Please Enter a time: '))
            if (time < 0 or time > (self.num_of_times - 1)):
                print 'Time %s out of range. [0,%i]'%(time,self.num_of_times-1)
                print 'You dont get a second try!'
                return -1
                
            fname = self.movie_path+'/movie.'+cosa+'.'+self.movie_num_str
            fname = os.path.abspath(fname)
            print "Loading movie.log file '%s'"%fname

            nex = self.param_dict['pex']*self.param_dict['nx']
            ney = self.param_dict['pey']*self.param_dict['ny']

            #NOTE: we are reading the whole movie file in one shot!
            # this seems wastefull
            print "Restoring Varible '"+cosa+"' From File '"+fname+"'"


            fp = np.memmap(fname, dtype='int8', mode='r',shape=(self.num_of_times,ney,nex)) 
            byte_arr = np.frombuffer(fp[time],dtype='int8')
            byte_arr = byte_arr.reshape(ney,nex).transpose()

# This seems to be working but we need to generalize for any file
# Also It would be good to have some kinda of print out talkting about
# How many movies there are and all that non sence.
            
#This is just doing it for the first time step, we can generlize later
            lmin = np.array(self.movie_log_dict[cosa])[:,0]
            lmax = np.array(self.movie_log_dict[cosa])[:,1]

            #byte_ip1 = movie_time*arr_size[0]*arr_size[1]
            #byte_ip2 = byte_ip1 + arr_size[0]*arr_size[1]

            #print 'There are '+str(len(byte_movie)/arr_size[0]/arr_size[1])+ \
            #' movie files and you loaded number ' +str(movie_time+1)

            return_dict[cosa] = byte_arr*(lmax[time]-lmin[time])/255.0+ lmin[time]


        #return real_arr_1.reshape(arr_size[1],arr_size[0])
        #return np.transpose(return_arr)
        #return return_arr
        return return_dict
        #return byte_arr
        

    def _movie_num_options(self):
        choices = glob.glob(self.movie_path+'/movie.bz.*')
        if len(choices) == 0: 
            print '!!! WARNING: the direcotry we are looking in does not have any moive.bz.XXX so we are crashing'
            return -1
        for var in range(np.size(choices)):
            choices[var] = choices[var][-3:]
        print 'Select from the following possible moive numbers: \n'+str(choices),
        movie_num_int = raw_input()
        return int(movie_num_int)
            
        
    def _set_movie_arr(self):
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
        elif self.param_dict['movie_header'] == '"movie_pic3.0.h"':
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
            print '!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!!@!@!@!@!@!@!@!@!@!@!@!@!@!@@!@!@!@!@!@!@!@!@!@!@!@!@!@'
            print 'This particular moive headder has not been coded! Fix it or talk to colby, or fix it yourself I dont care, Im a computer not a cop'
            print '!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@!@'
        
    def rotate_temp(self,Te):
        print 'Not Rotating Temperature'
        return -1

    #def _set_local(self,dict_for_local):
    def _set_local(self,dict_to_local):
        #c# exe_command = "global bx; bx = dict_to_local['bx']"
        #c# exe_command = "bx = dict_to_local['bx']"
        #c# global foobar
        #c# foobar=42
        #c# print exe_command
        #c# eval(exe_command)
        return 'Not coded !!!'
            




        

