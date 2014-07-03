########################################################################################################################################################
########################################################################################################################################################
#                                                                                                                                                      #
#                                                 Python Progs :  vdist.py                                                                             #
#                                                 Aruthor      :  Colby Haggerty                                                                       #
#                                                 Date         :  2014.03.25                                                                           #
#                                                                                                                                                      #
#                                                                                                                                                      #
########################################################################################################################################################
### Discription:
#
#   
#   
#   
#   
#
########################################################################################################################################################
########################################################################################################################################################


import os
import numpy as np
import struct
from scipy.io.idl import readsav
class vdist(object):
    """vdist object"""
    dump_path=''
    p3d_run_flag = False

#---------------------------------------------------------------------------------------------------------------
#   Method      : init
#
#   Discription : 
#               :
#
#   Args        :  
#               : 
#               : 
#
#   Comments    :
#               :
#---------------------------------------------------------------------------------------------------------------
    def __init__(self, arg='no_path'): 
# arg will either be a path or a p3d_run object
# we need a set of code for the path and a set for the object
# Here we parce which of the three cases inits we want to use. 
#   A run object in given
#   A path is given
#   Nothing is given
        if isinstance(arg,p3d_run):
            self.p3d_run_flag = True
            self.p3d_run = arg
            self.p3d_run.load_param()
            print 'Using data from p3d_run object '+arg.run_id_dict['run_name']
        elif isinstance(arg,str) and arg != 'no_path':
            print 'No p3d_run object given, using path '+arg
            self.dump_path = arg
        else:
            print 'We need a path to proceed with this class (./ for current)'
            self.dump_path = rawinput()
            print 'No p3d_run object given, using path '+self.dump_path
# We should realy have a check to make sure these open, and then handel the error
# Colby please code later


#---------------------------------------------------------------------------------------------------------------
#   Method      : handle_no_p3d_run 
#
#   Discription : a method to handel setting up this object for 
#               :
#
#   Args        :  
#               : 
#               : 
#
#   Comments    :
#               :
#---------------------------------------------------------------------------------------------------------------

    def set_box(self,r_simUnit=[0.0,0.0],width_simUnit=1.0,dump_ext='000'):
        print 'Setting the box to read the particles from.'

        print 'First we need the path where the dump file and param file stored:'
        if self.p3d_run_flag:
            self.dump_path = self.p3d_run.param_path
        print 'Path in use: "'+self.dump_path+'"'

        print 'Next we need to know what set of dump files you want to look at.'
        print 'Please enter the dump file extension (this can be changed later with dump_ext_set): '
        read_success_flag = False
        for tries in range(5):
            self.dump_ext =  raw_input()
            fname = self.dump_path + '/p3d-001.'+self.dump_ext
            try
                f = open(fname, "rb")
                read_success_flag = True
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
                print "Please re-enter the correct path extension "
            if read_success_flag == True:
                break
        if read_success_flag == False:
            print 'File could not be found'
            return -1



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
# You need to code this to get rid of the param_dict call
# or aleat put in an if statment to differentiate
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

#Colby employ a sign type thing here so that the axises work out right
        b_perp1x = 0.
        b_perp1y = -1.*bz_interp/(bz_interp**2 + by_interp**2)**(.5)
        b_perp1z = by_interp/(bx_interp**2 + by_interp**2)**(.5)

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
        
        return_hist_dict['parperp1'] = [np.histogram2d(vpar_i,vperp1_i, bins=bins),np.histogram2d(vpar_e,vperp1_e, bins=bins)]
        return_hist_dict['parperp2'] = [np.histogram2d(vpar_i,vperp2_i, bins=bins),np.histogram2d(vpar_e,vperp2_e, bins=bins)]
        return_hist_dict['perp1perp2'] = [np.histogram2d(vperp1_i,vperp2_i, bins=bins),np.histogram2d(vperp1_e,vperp2_e, bins=bins)]

        return return_hist_dict


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
