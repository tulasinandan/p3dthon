
from scipy.io.idl import readsav
filename = '/glade/p/work/colbyh/2014.Winter.electron.heating.paper/dat_files/reconn621_lower_timeave.dat'
CR = readsav(filename)

global extent; extent = [CR['xx'][0],CR['xx'][-1], CR['yy'][0], CR['yy'][-1] ]

argdict = {'npart':1,
           'charge':-1.,
           'mass':0.04,
           'run':000,
           'tstart':0,
           'tend':5.,
           't0':.0,
           'r0':[130.,30.0],
           'dr0':[0.1,0.1],
           'v0':[0.,0.,0.],
           'dv0':[0.1,0.1],
           'dt':.001}

