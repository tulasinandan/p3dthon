p3dthon
=======

Data Analysis Software built with python/scipy to handle the data output from P3D plasma pic simulations 
########################################################################################################################################################
########################################################################################################################################################
#                                                                                                                                                      #
#                                                 Python Progs :  README                                                                               # 
#                                                 Aruthor      :  Colby Haggerty                                                                       #                     
#                                                 Date         :  2013.10.30                                                                           #
#                                                                                                                                                      #
########################################################################################################################################################
########################################################################################################################################################

####################### Starters-Colby #####################################

All of our pythong programs will be making use of SciPy and NumPy
If you are unfamilar with these, it might be good to go and read 
about them. Currently I am using this on yellowstone, hopefully 
nothing will change between super computers. So to use python on
yellowstone first you need to load the modules with;

module load python
module load all-python-libs

This will load all the nessesarty libraries
Then you can enter the interactive python front end
and run your scripts, with

ipython --pylab

Good luck!

########################### HOW-TO ########################################
First you need to tell python to look at the code we are going to be using 
to create the run object this is done with the folowing:

    from p3d_runs import p3d_run
    reconn331 = p3d_run('reconn331')




####################### Edit: 2013.10.30 -Colby ############################
I am tring to slowly move from IDL to python and so this diretory is my scratch work for this.
I am hoping to talk to danial about making this a repository, but since I am currently the only
one who uses this, perhaps I will wait. It seems like the best play to start is with code
that can read the movie files from p3d. Although I am thinking that somthing analgous to
sub.pro will need to come about for all of this to work. 

####################### Edit: 2013.11.13 -Colby ############################
I made a p3d_sub.pro and I am just going to build up some function in this python program.
I am hoping that as sub.py improves I can port it over to some kind of object...
Right now I am thinking that I will need some kind of table that hold relevent information
about every run. so you say load up reconn621 and it reads the table and then you can call
atributes of it to see what you are intrested in.

####################### Edit: 2014.03.24 -Colby ############################
I have made a lot of changes! I will have to go back and document progress better.
But for right now just remeber these points you should code:
1- Seperate the vdist stuff into its own class!
    This class should accept a run object as an agument and then be able to do all the same stuff
2- Fix the run_list loading system!
    It makes more sence (I think) to have a run_list that points to files with all of the run data.
    So each run can have its own set of things.
3- Implement a loading system that is more robust!
    Eventualy what I want is to check to see if a run exists, and if it doesnt, offer the option
    to write in all the important quantities
Please colby! document what you are doing

4- You should be able to use these methods even if you dont have a run object so i should create a special instance
    that justs asks you to enter the relavent quantitys.

####################### Edit: 2014.04.26 -Colby ############################
Ok so most of this code is going to be pretty flexable, but when we start wrighing scripts
It is going to be usefull to have some kind of reffrence table so that somone who is
just starting to use this can know what kind of key values shuold be in the info file
So below is a working list of some of thoes values

run_dir path/where/all/data/is/stored
param_name param_typeXXX
