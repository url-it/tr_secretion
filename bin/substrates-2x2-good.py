# substrates.py - code for the 'Out: Plots' tab of the GUI.
#
# Contains visualization for: Cells and substrates, possibly overlaid (on the left); Extra analysis (2D line plots; on the right)
#
# Author: Randy Heiland, with contributions from many students and collaborators
#

import os, math
from pathlib import Path
from ipywidgets import Layout, Label, Text, Checkbox, Button, BoundedIntText, HBox, VBox, Box, \
    FloatText, Dropdown, SelectMultiple, RadioButtons, interactive
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.colors as mplc
from matplotlib import gridspec
from collections import deque
from pyMCDS import pyMCDS
import numpy as np
import scipy.io
import xml.etree.ElementTree as ET  # https://docs.python.org/2/library/xml.etree.elementtree.html
import glob
import platform
import zipfile
from debug import debug_view 
import warnings
import traceback
import sys

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import Download
    except:
        hublib_flag = False
else:
    hublib_flag = False

#warnings.warn(message, mplDeprecation, stacklevel=1)
warnings.filterwarnings("ignore")

class SubstrateTab(object):

    def __init__(self):
        
        self.tb_count = 0

        self.output_dir = '.'
        # self.output_dir = 'tmpdir'

        # These are recomputed below 
        # basic_length = 12.5
        basic_length = 12.0
        self.figsize_width_substrate = 15.0  # allow extra for colormap
        self.figsize_height_substrate = basic_length

        self.figsize_width_2Dplot = basic_length
        self.figsize_height_2Dplot = basic_length

        # self.width_substrate = basic_length  # allow extra for colormap
        # self.height_substrate = basic_length

        self.figsize_width_svg = basic_length
        self.figsize_height_svg = basic_length
        # self.width_svg = basic_length
        # self.height_svg = basic_length

        self.figsize_width_substrate = 15.0  # allow extra for colormap
        self.figsize_height_substrate = 12.0
        self.figsize_width_svg = 12.0
        self.figsize_height_svg = 12.0

        self.axis_label_fontsize = 15

        self.ax0 = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None
        self.ax4 = None
        self.ax5 = None
        self.ax1_lymph_TC = None
        self.ax1_lymph_TH2 = None

        self.updated_analysis_flag = True
        self.analysis_data_plotted = False
        self.analysis_data_set1 = False  # live, infected, dead
        self.analysis_data_set2 = False  # Mac, Neut, CD8, 
        self.analysis_data_set3 = False  
        self.analysis_data_set4 = False  

        # colors of plots for extra analysis (line ~1100)
        self.mac_color = 'lime'
        self.neut_color = 'cyan'
        self.cd8_color = 'red'
        self.dc_color = 'fuchsia'
        self.cd4_color = 'orange'
        self.fib_color = 'blueviolet'

        self.lymph_DC_color = 'black'
        self.lymph_TC_color = 'red'
        self.viral_load_color = 'black'


        # self.fig = plt.figure(figsize=(7.2,6))  # this strange figsize results in a ~square contour plot

        self.first_time = True
        self.modulo = 1

        self.use_defaults = True

        self.svg_delta_t = 1
        self.substrate_delta_t = 1
        self.svg_frame = 1
        self.substrate_frame = 1

        self.customized_output_freq = False
        self.therapy_activation_time = 1000000
        self.max_svg_frame_pre_therapy = 1000000
        self.max_substrate_frame_pre_therapy = 1000000

        self.svg_xmin = 0

        # Probably don't want to hardwire these if we allow changing the domain size
        # self.svg_xrange = 2000
        # self.xmin = -1000.
        # self.xmax = 1000.
        # self.ymin = -1000.
        # self.ymax = 1000.
        # self.x_range = 2000.
        # self.y_range = 2000.

        self.show_nucleus = False
        self.show_edge = True
        self.alpha = 1.0   # 0.7 is partially transparent (all cells)

        substrates_default_disabled_flag = True  # True = disable them by default; False=enable them

        # initial value
        self.field_index = 4
        # self.field_index = self.substrate_choice.value + 4

        self.skip_cb = True

        # define dummy size of mesh (set in the tool's primary module)
        self.numx = 0
        self.numy = 0

        # ------- custom data for cells ----------
        self.xval = np.empty([1])
        # print('sub, init: len(self.xval) = ',len(self.xval))
        self.yval1 = np.empty([1]) # live, infected, dead
        self.yval2 = np.empty([1])
        self.yval3 = np.empty([1])

        self.yval4 = np.empty([1]) # Mac,Neut,CD8,DC,CD4,Fib
        self.yval5 = np.empty([1])
        self.yval6 = np.empty([1])
        self.yval7 = np.empty([1])
        self.yval8 = np.empty([1])
        self.yval9 = np.empty([1])

        self.yval10 = np.empty([1]) # viral load

        self.yval11 = np.empty([1])  # lymph node dynamics: DC,TC,TH1,TH2
        self.yval12 = np.empty([1])
        self.yval13 = np.empty([1])
        self.yval14 = np.empty([1])

        self.tname = "time"
        self.yname = 'Y'
        # self.num_2D_plots = 1



        self.title_str = ''

        tab_height = '600px'
        tab_height = '500px'
        tab_height = '1000px'
        constWidth = '180px'
        constWidth2 = '150px'
        tab_layout = Layout(width='900px',   # border='2px solid black',
                            height=tab_height, ) #overflow_y='scroll')

        max_frames = 1   
        # NOTE: The "interactive" widget contains the plot(s). Whenever any plot needs to be updated,
        # its "update" method needs to be invoked. So, if you notice multiple, flashing 
        # plot updates occuring, you can search for all instances of "self.i_plot.update()" and do
        # a debug print to see where they occur.

        # self.mcds_plot = interactive(self.plot_substrate, frame=(0, max_frames), continuous_update=False)  
        # self.i_plot = interactive(self.plot_plots, frame=(0, max_frames), continuous_update=False)  
        self.i_plot = interactive(self.plot_substrate, frame=(0, max_frames), continuous_update=False)  

        # "plot_size" controls the size of the tab height, not the plot (rf. figsize for that)
        # NOTE: the Substrates Plot tab has an extra row of widgets at the top of it (cf. Cell Plots tab)
        svg_plot_size = '700px'
        svg_plot_size = '900px'
        plot_area_width = '1500px'
        plot_area_height = '900px'
        plot_area_height = '1000px'
        self.i_plot.layout.width = plot_area_width 
        self.i_plot.layout.height = plot_area_height 

        self.fontsize = 20
        # self.fontsize = 30


        #============  new GUI =================
        self.max_frames = BoundedIntText(value=0,description='# cell frames',min=0,max=999999,layout=Layout(width='160px'))  # border='1px solid black',
        self.cells_toggle = Checkbox(description='Cells',value=True, style = {'description_width': 'initial'}, layout=Layout(width='110px', )) #border='1px solid black'))
        self.cell_edges_toggle = Checkbox(description='edge',value=self.show_edge, style = {'description_width': 'initial'}, layout=Layout(width='110px',))  #   align_items='stretch',
            

        layout1 = Layout(display='flex',
                            flex_flow='row',
                            align_items='center',
                            width='25%', )  #border='1px solid black')
        hb1=HBox([self.cells_toggle,self.cell_edges_toggle ])  # layout=layout1)
        # cells_vbox=VBox([self.max_frames, hb1], layout=Layout(width='350px',border='1px solid black',))
        cells_vbox=VBox([self.max_frames, hb1], layout=Layout(width='320px'))
        #--------------------------
        self.substrates_toggle = Checkbox(description='Substrates', style = {'description_width': 'initial'})

        # self.field_min_max = {'assembled_virion':[0.,1.,False]  }
        # hacky I know, but make a dict that's got (key,value) reversed from the dict in the Dropdown below

        # ipywidgets 8 docs: Selection widgets no longer accept a dictionary of options. Pass a list of key-value pairs instead.
        self.field_dict = {0:'director signal', 1:'cargo signal'}

        # self.substrate_choice = Dropdown(options={'assembled_virion': 0},layout=Layout(width='150px'))
        # options will be replaced below, based on initial.xml
        self.substrate_choice = Dropdown(
            options={'director signal': 0, 'cargo signal':1},
            value=0,
            disabled = substrates_default_disabled_flag,
            #     description='Field',
           layout=Layout(width='150px')
        )
        self.colormap_dd = Dropdown(options=['viridis', 'jet', 'YlOrRd'],value='YlOrRd',layout=Layout(width='200px'))
        # self.colormap_dd.observe(self.mcds_field_cb)
        self.colormap_dd.observe(self.substrate_field_cb)
        hb2 = HBox([self.substrates_toggle,self.substrate_choice,self.colormap_dd], layout=Layout(width='350px', )) # border='1px solid black',))

        self.colormap_fixed_toggle = Checkbox(description='Fix',style = {'description_width': 'initial'}, layout=Layout(width='60px'))
        constWidth2 = '160px'
        self.colormap_min = FloatText(
                    description='Min',
                    value=0,
                    step = 0.1, 
                    layout=Layout(width=constWidth2),)
        self.colormap_max = FloatText(
                    description='Max',
                    value=38,
                    step = 0.1,
                    layout=Layout(width=constWidth2),)
        # hb3=HBox([colormap_fixed_toggle,colormap_min,colormap_max], layout=Layout(width='500px',justify_content='flex-start'))
        hb3=HBox([self.colormap_fixed_toggle,self.colormap_min,self.colormap_max], layout=Layout(justify_content='flex-start'))  # border='1px solid black',

        substrate_vbox=VBox([hb2, hb3], layout=Layout(width='500px'))

        #--------------------------
        # analysis_label = Label(value='--Extra analysis--')

        self.analysis_data_toggle = Checkbox(
            description='Extra analysis',
            disabled=False,
            style = {'description_width': 'initial'},
            layout=Layout(width='130px', )  #  border='1px solid black',)
        #           layout=Layout(width=constWidth2),
            )

        self.analysis_data_update_button = Button(
            description='Update',
            disabled=True,
            style = {'description_width': 'initial'},
            layout=Layout(width='130px', )  #  border='1px solid black',)
        #           layout=Layout(width=constWidth2),
            )
        self.analysis_data_update_button.style.button_color = 'lightgreen'


        #--------------
        # self.analysis_data_update_button= Button(
        #     description='Update', 
        #     disabled=True,)
        #     # layout=Layout(width='120px',) ,style = {'description_width': 'initial'})
        # self.analysis_data_update_button.style.button_color = 'lightgreen'

        # analysis_data_vbox1 = VBox([self.analysis_data_toggle, ], layout=Layout(justify_content='center'))  # ,border='1px solid black',  width='330px',
        # analysis_data_vbox1 = VBox([analysis_label, self.analysis_data_update_button, ], layout=Layout(justify_content='center'))  # ,border='1px solid black',  width='330px',
        analysis_data_vbox1 = VBox([self.analysis_data_toggle, self.analysis_data_update_button], layout=Layout(justify_content='center'))  # ,border='1px solid black',))  # width='330px',

        # self.analysis_data_choice = SelectMultiple(
        #     # options=['assembled_virion','susceptible','infected', 'dead'],
        #     options=['live','infected', 'dead'],
        #     disabled=True,
        #     value=['live'], 
        #     rows=3,  
        #     layout=Layout(width='160px', ) )

        self.analysis_data_choice = Dropdown(
            options={'cells 1-3':0},
            # options={'live,infected,dead':0, 'Mac,Neut,CD8,DC,CD4,Fib':1, 'viral load':2, 'lymph:DC,TC':3, 'lymph:Th1,Th2':4},
            # options=['live,infected,dead', 'Mac,Neut,CD8,DC,CD4,Fib', 'viral load', 'lymph:DC,TC', 'lymph:Th1,Th2'],
            value=0,
            disabled = True,
            #     description='Field',
        #    layout=Layout(width='150px')
        )
        # self.analysis_data_choice_y = {0:[False,0.,1.], 1:[False,0.,1.], 2:[False,0.,1.], 3:[False,0.,1.], 4:[False,0.,1.]} 
        self.analysis_data_choice_y = {0:[False,0.,1.]} 

#         self.analysis_data_choice = RadioButtons(
#             options=['live,infected,dead', 'Mac,Neut,CD8,DC,CD4,Fib', 'viral load', 'lymph node dynamics'],
#             value='live,infected,dead', 
# #           layout={'width': 'max-content'}, # If the items' names are long
#             disabled=True
#         )

        # called when a user selects another choice in the custom data radio buttons
        def analysis_data_choice_cb(b):
            idx = self.analysis_data_choice.value
            if idx > 2:
                self.fixed_yrange.disabled = True
                self.y_min.disabled = True
                self.y_max.disabled = True
            else:
                self.fixed_yrange.disabled = False
                self.y_min.disabled = False
                self.y_max.disabled = False

            self.fixed_yrange.value = self.analysis_data_choice_y[idx][0]
            self.y_min.value = self.analysis_data_choice_y[idx][1]
            # print('idx,y_min=',idx,self.y_min.value)
            self.y_max.value = self.analysis_data_choice_y[idx][2]
            # self.update_analysis_data()
            self.i_plot.update()

        self.analysis_data_choice.observe(analysis_data_choice_cb)


        self.analysis_data_wait = Label('',color = 'red')
        # self.analysis_data_wait = Label('Will be available after simulation completes.')
        # self.analysis_data_wait = Label('Wait for 1st time processing...')  




        def analysis_data_toggle_cb(b):
            # self.update()
            if (self.analysis_data_toggle.value):  
                self.analysis_data_wait.value = 'Press Update to analyze available data.'
                self.analysis_data_choice.disabled = False
                self.analysis_data_update_button.disabled = False
                # self.update_analysis_data()
            else:
                self.analysis_data_wait.value = ''
                self.analysis_data_choice.disabled = True
                self.analysis_data_update_button.disabled = True
            self.i_plot.update()
            # self.analysis_data_wait.value = ''

        self.analysis_data_toggle.observe(analysis_data_toggle_cb)

        def analysis_data_update_cb(b):
            # self.update()
            self.analysis_data_wait.value = 'Updating analysis data...'
            self.update_analysis_data()

            self.i_plot.update()
            self.analysis_data_wait.value = ''

        self.analysis_data_update_button.on_click(analysis_data_update_cb)


        #----------------------------
        self.fixed_yrange = Checkbox(description='Fix',style = {'description_width': 'initial'}, layout=Layout(width='60px'))
        constWidth3 = '120px'
        self.y_min = FloatText(
                    description='Ymin',
                    value=0,
                    step = 1.0, 
                    style = {'description_width': 'initial'},
                    layout=Layout(width=constWidth3),)
        self.y_max = FloatText(
                    description='Ymax',
                    value=1.0,
                    step = 1.0,
                    style = {'description_width': 'initial'},
                    layout=Layout(width=constWidth3),)

        def fixed_yrange_cb(b):
            idx = self.analysis_data_choice.value 
            self.analysis_data_choice_y[idx][0] = self.fixed_yrange.value
            if self.fixed_yrange.value:
                self.y_min.disabled = False
                self.y_max.disabled = False
            else:
                self.y_min.disabled = True
                self.y_max.disabled = True

        # self.fixed_yrange.observe(fixed_yrange_cb)

        def analysis_yrange_cb(b):
            idx = self.analysis_data_choice.value 
            self.analysis_data_choice_y[idx][1] = self.y_min.value
            self.analysis_data_choice_y[idx][2] = self.y_max.value
            print('dict=',self.analysis_data_choice_y)

        # self.y_min.observe(analysis_yrange_cb)
        # self.y_max.observe(analysis_yrange_cb)


        # hb3=HBox([colormap_fixed_toggle,colormap_min,colormap_max], layout=Layout(width='500px',justify_content='flex-start'))
        y_range_box = HBox([self.fixed_yrange,self.y_min,self.y_max]) # layout=Layout(justify_content='flex-start'))  # border='1px solid black',

        #gui=HBox([cells_vbox, substrate_vbox, analysis_data_hbox], justify_content='center')  # vs. 'flex-start   , layout=Layout(width='900px'))

        #==========================================================================

        # ------- "observe" functionality (callbacks)
        self.max_frames.observe(self.update_max_frames)

        # self.field_min_max = {'dummy': [0., 1., False]}
        # NOTE: manually setting these for now (vs. parsing them out of data/initial.xml)

        # print("substrate __init__: self.substrate_choice.value=",self.substrate_choice.value)
#        self.substrate_choice.observe(self.mcds_field_cb)
        # self.substrate_choice.observe(self.mcds_field_changed_cb)
        self.substrate_choice.observe(self.substrate_field_changed_cb)

        # self.field_colormap = Dropdown(
        #     options=['viridis', 'jet', 'YlOrRd'],
        #     value='YlOrRd',
        #     #     description='Field',
        #    layout=Layout(width=constWidth)
        # )

        # rwh2
#        self.field_cmap.observe(self.plot_substrate)
        # self.field_colormap.observe(self.substrate_field_cb)

        self.colormap_min.observe(self.substrate_field_cb)
        self.colormap_max.observe(self.substrate_field_cb)

#         self.cmap_fixed_toggle = Checkbox(
#             description='Fix',
#             disabled=False,
# #           layout=Layout(width=constWidth2),
#         )
        # self.colormap_fixed_toggle.observe(self.mcds_field_cb)

        # self.cmap_min = FloatText(
        #     description='Min',
        #     value=0,
        #     step = 0.1,
        #     disabled=True,
        #     layout=Layout(width=constWidth2),
        # )

        # self.cmap_max = FloatText(
        #     description='Max',
        #     value=38,
        #     step = 0.1,
        #     disabled=True,
        #     layout=Layout(width=constWidth2),
        # )

        def colormap_fixed_toggle_cb(b):
            field_name = self.field_dict[self.substrate_choice.value]
            # print(self.cmap_fixed_toggle.value)
            if (self.colormap_fixed_toggle.value):  # toggle on fixed range
                self.colormap_min.disabled = False
                self.colormap_max.disabled = False
                self.field_min_max[field_name][0] = self.colormap_min.value
                self.field_min_max[field_name][1] = self.colormap_max.value
                self.field_min_max[field_name][2] = True
                # self.save_min_max.disabled = False
            else:  # toggle off fixed range
                self.colormap_min.disabled = True
                self.colormap_max.disabled = True
                self.field_min_max[field_name][2] = False
                # self.save_min_max.disabled = True
#            self.mcds_field_cb()

            if not self.skip_cb:
                # print("colormap_fixed_toggle_cb():  i_plot.update")
                self.i_plot.update()

        # self.colormap_fixed_toggle.observe(colormap_fixed_toggle_cb)
        self.colormap_fixed_toggle.observe(self.substrate_field_cb)

        def cell_edges_toggle_cb(b):
            # self.update()
            if (self.cell_edges_toggle.value):  
                self.show_edge = True
            else:
                self.show_edge = False
            # print("cell_edges_toggle_cb():  i_plot.update")
            self.i_plot.update()

        self.cell_edges_toggle.observe(cell_edges_toggle_cb)

        def cells_toggle_cb(b):
            # self.update()
            self.skip_cb = True
            if self.cells_toggle.value:
                self.cell_edges_toggle.disabled = False
                # self.cell_nucleus_toggle.disabled = False
            else:
                self.cell_edges_toggle.disabled = True
                # self.cell_nucleus_toggle.disabled = True
            self.skip_cb = False

            # print("cells_toggle_cb():  i_plot.update")
            self.i_plot.update()

        self.cells_toggle.observe(cells_toggle_cb)

        def substrates_toggle_cb(b):
            self.skip_cb = True
            if self.substrates_toggle.value:  # seems bass-ackwards, but makes sense
                self.colormap_fixed_toggle.disabled = False
                self.colormap_min.disabled = False
                self.colormap_max.disabled = False
                self.substrate_choice.disabled = False
                # self.field_colormap.disabled = False
                self.colormap_dd.disabled = False
            else:
                self.colormap_fixed_toggle.disabled = True
                self.colormap_min.disabled = True
                self.colormap_max.disabled = True
                self.substrate_choice.disabled = True
                # self.field_colormap.disabled = True
                self.colormap_dd.disabled = True
            self.skip_cb = False

            # print("substrates_toggle_cb:  i_plot.update")
            self.i_plot.update()

        self.substrates_toggle.observe(substrates_toggle_cb)

        #---------------------
        # def analysis_data_toggle_cb(b):
        #     # print("analysis_data_toggle_cb()")
        #     self.skip_cb = True
        #     if (self.analysis_data_toggle.value):  # seems bass-ackwards
        #         self.analysis_data_choice.disabled = False
        #         self.analysis_data_update_button.disabled = False
        #     else:
        #         self.analysis_data_choice.disabled = True
        #         self.analysis_data_update_button.disabled = True
        #     self.skip_cb = False

        #     # print("analysis_data_toggle_cb():  i_plot.update")
        #     self.i_plot.update()

        # self.analysis_data_toggle.observe(analysis_data_toggle_cb)
        # self.analysis_data_update_button.on_click(self.update_analysis_data)

        #---------------------
        help_label = Label('select slider: drag or left/right arrows')

        # analysis_data_hbox = HBox([analysis_data_vbox1, VBox([self.analysis_data_choice, y_range_box, self.analysis_data_wait]), ])
        analysis_data_hbox = HBox([analysis_data_vbox1, VBox([self.analysis_data_choice,  self.analysis_data_wait]), ])

        controls_box = HBox([cells_vbox, substrate_vbox, analysis_data_hbox], justify_content='center')  # vs. 'flex-start   , layout=Layout(width='900px'))

        if (hublib_flag):
            self.download_button = Download('mcds.zip', style='warning', icon='cloud-download', 
                                                tooltip='Download MCDS data', cb=self.download_cb)

            self.download_svg_button = Download('svg.zip', style='warning', icon='cloud-download', 
                                            tooltip='Download cells SVG', cb=self.download_svg_cb)
            # config_file = Path(os.path.join(self.output_dir, 'config.xml'))
            # config_file = self.output_dir + '/config.xml'
            self.download_config_button = Download('config.zip', style='warning', icon='cloud-download', 
                                            tooltip='Download the config params', cb=self.download_config_cb)
            download_row = HBox([self.download_button.w, self.download_svg_button.w, self.download_config_button.w, Label("Download data (browser must allow pop-ups).")])

            # box_layout = Layout(border='0px solid')
            # controls_box = VBox([row1, row2])  # ,width='50%', layout=box_layout)
            # controls_box = HBox([cells_vbox, substrate_vbox, analysis_data_hbox], justify_content='center')  # vs. 'flex-start   , layout=Layout(width='900px'))

            self.tab = VBox([controls_box, self.i_plot, download_row, debug_view])
        else:
            # self.tab = VBox([row1, row2])
            # self.tab = VBox([row1, row2, self.i_plot])
            self.tab = VBox([controls_box, self.i_plot])

    #---------------------------------------------------
    def reset_analysis_data_plotting(self, bool_val):
        # self.analysis_data_toggle.disabled = bool_val
        self.analysis_data_plotted = False

        if (bool_val == True):
            self.analysis_data_toggle.value = False
            self.xval = np.empty([1])

            self.yval1 = np.empty([1])
            self.yval2 = np.empty([1])
            self.yval3 = np.empty([1])

            self.yval4 = np.empty([1])
            self.yval5 = np.empty([1])
            self.yval6 = np.empty([1])
            self.yval7 = np.empty([1])
            self.yval8 = np.empty([1])
            self.yval9 = np.empty([1])

            self.yval10 = np.empty([1])

            self.yval11 = np.empty([1])
            self.yval12 = np.empty([1])
            self.yval13 = np.empty([1])
            self.yval14 = np.empty([1])

            # No longer used(?) since the manual 'Update' of analyses
            self.analysis_data_set1 = False  # live, infected, dead
            self.analysis_data_set2 = False  # Mac, Neut, CD8, etc
            self.analysis_data_set3 = False  # viral load
            self.analysis_data_set4 = False  # lymph node dynamics

            self.analysis_data_toggle.value = False
        self.analysis_data_choice.disabled = bool_val
        self.analysis_data_update_button.disabled = bool_val

    #---------------------------------------------------
    def update_dropdown_fields(self, data_dir):
        self.output_dir = data_dir
        # print('!! update_dropdown_fields() called: self.output_dir = ', self.output_dir)
        tree = None
        try:
            fname = os.path.join(self.output_dir, "initial.xml")
            tree = ET.parse(fname)
            xml_root = tree.getroot()
        except:
            print("Cannot open ",fname," to read info, e.g., names of substrate fields.")
            return

        # No longer used since 'Update' button (I think)
        self.analysis_data_set1 = False  # cells 1-3
        # self.analysis_data_set1 = False  # live, infected, dead
        # self.analysis_data_set2 = False  # mac, neut, cd8
        # self.analysis_data_set3 = False  # viral load
        # self.analysis_data_set4 = False  # lymph node dynamics

        xml_root = tree.getroot()
        self.field_min_max = {}
        self.field_dict = {}
        dropdown_options = {}
        uep = xml_root.find('.//variables')
        comment_str = ""
        field_idx = 0

        if (uep):
            for elm in uep.findall('variable'):
                # print("-----> ",elm.attrib['name'])
                field_name = elm.attrib['name']
                if ('assembled' not in field_name):
                    self.field_min_max[field_name] = [0., 1., False]
                    self.field_dict[field_idx] = field_name
                    dropdown_options[field_name] = field_idx

                    self.field_min_max[field_name][0] = 0   
                    self.field_min_max[field_name][1] = 1

                    # self.field_min_max[field_name][0] = field_idx   #rwh: helps debug
                    # self.field_min_max[field_name][1] = field_idx+1   
                    self.field_min_max[field_name][2] = False
                field_idx += 1

#        constWidth = '180px'
        # print('options=',dropdown_options)
        # print(self.field_min_max)  # debug
        self.substrate_choice.value = 0
        self.substrate_choice.options = dropdown_options

        # print("----- update_dropdown_fields(): self.field_dict= ", self.field_dict) 
#         self.mcds_field = Dropdown(
# #            options={'oxygen': 0, 'glucose': 1},
#             options=dropdown_options,
#             value=0,
#             #     description='Field',
#            layout=Layout(width=constWidth)
#         )

    # def update_max_frames_expected(self, value):  # called when beginning an interactive Run
    #     self.max_frames.value = value  # assumes naming scheme: "snapshot%08d.svg"
    #     self.mcds_plot.children[0].max = self.max_frames.value

#------------------------------------------------------------------------------
    # called from pc4covid19 module when user selects new cache dir in 'Load Config'
    def update_params(self, config_tab, user_params_tab):

        self.reset_analysis_data_plotting(True)

        # xml_root.find(".//x_min").text = str(self.xmin.value)
        # xml_root.find(".//x_max").text = str(self.xmax.value)
        # xml_root.find(".//dx").text = str(self.xdelta.value)
        # xml_root.find(".//y_min").text = str(self.ymin.value)
        # xml_root.find(".//y_max").text = str(self.ymax.value)
        # xml_root.find(".//dy").text = str(self.ydelta.value)
        # xml_root.find(".//z_min").text = str(self.zmin.value)
        # xml_root.find(".//z_max").text = str(self.zmax.value)
        # xml_root.find(".//dz").text = str(self.zdelta.value)

        self.xmin = config_tab.xmin.value 
        self.xmax = config_tab.xmax.value 
        self.x_range = self.xmax - self.xmin
        self.svg_xrange = self.xmax - self.xmin
        self.ymin = config_tab.ymin.value
        self.ymax = config_tab.ymax.value 
        self.y_range = self.ymax - self.ymin

        self.numx =  math.ceil( (self.xmax - self.xmin) / config_tab.xdelta.value)
        self.numy =  math.ceil( (self.ymax - self.ymin) / config_tab.ydelta.value)

        # if (self.x_range > self.y_range):  
        #     ratio = self.y_range / self.x_range
        #     self.figsize_width_substrate = self.width_substrate  # allow extra for colormap
        #     self.figsize_height_substrate = self.height_substrate * ratio
        #     self.figsize_width_svg = self.width_svg
        #     self.figsize_height_svg = self.height_svg * ratio
        # else:   # x < y
        #     ratio = self.x_range / self.y_range
        #     self.figsize_width_substrate = self.width_substrate * ratio 
        #     self.figsize_height_substrate = self.height_substrate
        #     self.figsize_width_svg = self.width_svg * ratio
        #     self.figsize_height_svg = self.height_svg

        if (self.x_range > self.y_range):  
            ratio = self.y_range / self.x_range
            self.figsize_width_substrate = 15.0  # allow extra for colormap
            self.figsize_height_substrate = 12.0 * ratio
            self.figsize_width_svg = 12.0
            self.figsize_height_svg = 12.0 * ratio
        else:   # x < y
            ratio = self.x_range / self.y_range
            self.figsize_width_substrate = 15.0 * ratio 
            self.figsize_height_substrate = 12.0
            self.figsize_width_svg = 12.0 * ratio
            self.figsize_height_svg = 12.0 
        # print('update_params():  sub w,h= ',self.figsize_width_substrate,self.figsize_height_substrate,' , svg w,h= ',self.figsize_width_svg,self.figsize_height_svg)

        self.svg_flag = config_tab.toggle_svg.value
        self.substrates_flag = config_tab.toggle_mcds.value
        # print("substrates: update_params(): svg_flag, toggle=",self.svg_flag,config_tab.toggle_svg.value)        
        # print("substrates: update_params(): self.substrates_flag = ",self.substrates_flag)
        self.svg_delta_t = config_tab.svg_interval.value
        self.substrate_delta_t = config_tab.mcds_interval.value
        self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
        # print("substrates: update_params(): modulo=",self.modulo)        

        if self.customized_output_freq:
#            self.therapy_activation_time = user_params_tab.therapy_activation_time.value   # NOTE: edit for user param name
            # print("substrates: update_params(): therapy_activation_time=",self.therapy_activation_time)
            self.max_svg_frame_pre_therapy = int(self.therapy_activation_time/self.svg_delta_t)
            self.max_substrate_frame_pre_therapy = int(self.therapy_activation_time/self.substrate_delta_t)

#------------------------------------------------------------------------------
#    def update(self, rdir):
#   Called from driver module (e.g., pc4*.py) (among other places?)
    def update(self, rdir=''):
        # with debug_view:
        #     print("substrates: update rdir=", rdir)        
        # print("substrates: update rdir=", rdir)        

        if rdir:
            self.output_dir = rdir

        # print('update(): self.output_dir = ', self.output_dir)

        if self.first_time:
        # if True:
            self.first_time = False
            full_xml_filename = Path(os.path.join(self.output_dir, 'config.xml'))
            # print("substrates: update(), config.xml = ",full_xml_filename)        
            # self.num_svgs = len(glob.glob(os.path.join(self.output_dir, 'snap*.svg')))
            # self.num_substrates = len(glob.glob(os.path.join(self.output_dir, 'output*.xml')))
            # print("substrates: num_svgs,num_substrates =",self.num_svgs,self.num_substrates)        
            # argh - no! If no files created, then denom = -1
            # self.modulo = int((self.num_svgs - 1) / (self.num_substrates - 1))
            # print("substrates: update(): modulo=",self.modulo)        
            if full_xml_filename.is_file():
                tree = ET.parse(full_xml_filename)  # this file cannot be overwritten; part of tool distro
                xml_root = tree.getroot()
                # print("substrates.py: updates(): full_xml_filename = ", full_xml_filename )
                # print('   xml_root.find(".//SVG//interval").text) = ', xml_root.find(".//SVG//interval").text)
                tmpval = float(xml_root.find(".//SVG//interval").text)
                # self.svg_delta_t = int(xml_root.find(".//SVG//interval").text)
                self.svg_delta_t = int(tmpval)

                tmpval = float(xml_root.find(".//full_data//interval").text)
                # self.substrate_delta_t = int(xml_root.find(".//full_data//interval").text)
                self.substrate_delta_t = int(tmpval)
                # print("substrates: svg,substrate delta_t values=",self.svg_delta_t,self.substrate_delta_t)        

                self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
                # print("substrates-2: update(): modulo=",self.modulo)        


        # all_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*.xml')))  # if the substrates/MCDS

        all_files = sorted(glob.glob(os.path.join(self.output_dir, 'snap*.svg')))   # if .svg
        if len(all_files) > 0:
            last_file = all_files[-1]
            # print("substrates.py/update(): len(snap*.svg) = ",len(all_files)," , last_file=",last_file)
            self.max_frames.value = int(last_file[-12:-4])  # assumes naming scheme: "snapshot%08d.svg"
        else:
            substrate_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*.xml')))
            if len(substrate_files) > 0:
                last_file = substrate_files[-1]
                self.max_frames.value = int(last_file[-12:-4])

    def download_config_cb(self):
        file_str = os.path.join(self.output_dir, 'config.xml')
        with zipfile.ZipFile('config.zip', 'w') as myzip:
            myzip.write(file_str, os.path.basename(file_str))   # 2nd arg avoids full filename path in the archive

    def download_svg_cb(self):
        file_str = os.path.join(self.output_dir, '*.svg')
        # print('zip up all ',file_str)
        with zipfile.ZipFile('svg.zip', 'w') as myzip:
            for f in glob.glob(file_str):
                myzip.write(f, os.path.basename(f))   # 2nd arg avoids full filename path in the archive

    def download_cb(self):
        file_xml = os.path.join(self.output_dir, '*.xml')
        file_mat = os.path.join(self.output_dir, '*.mat')
        # print('zip up all ',file_str)
        with zipfile.ZipFile('mcds.zip', 'w') as myzip:
            for f in glob.glob(file_xml):
                myzip.write(f, os.path.basename(f)) # 2nd arg avoids full filename path in the archive
            for f in glob.glob(file_mat):
                myzip.write(f, os.path.basename(f))

    def update_max_frames(self,_b):
        self.i_plot.children[0].max = self.max_frames.value

    # called if user selected different substrate in dropdown
    # @debug_view.capture(clear_output=True)
    def substrate_field_changed_cb(self, b):
        if (self.substrate_choice.value == None):
            return

        # self.tb_count += 1
        # print('substrate_field_changed_cb(): tb_count=',self.tb_count,', options= ',self.substrate_choice.options)

        if self.tb_count == 25:  # originally checked == 5 (I don't remember why I did this)
            # foo = 1/0  # force an exception for a traceback
            try:
                raise NameError('HiThere')
            except:
                with debug_view:
                    # print("substrates: update rdir=", rdir)        
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback, limit=None, file=sys.stdout)
                # sys.exit(-1)

        # print('substrate_field_changed_cb: self.field_index=', self.field_index)
        # print('substrate_field_changed_cb: self.substrate_choice.value=', self.substrate_choice.value)
        # if (self.field_index == self.substrate_choice.value + 4):
            # return

        self.field_index = self.substrate_choice.value + 4

        field_name = self.field_dict[self.substrate_choice.value]
        # print('substrate_field_changed_cb: field_name='+ field_name)
        # print(self.field_min_max[field_name])

        # BEWARE of these triggering the substrate_field_cb() callback! Hence, the "skip_cb"
        self.skip_cb = True
        self.colormap_min.value = self.field_min_max[field_name][0]
        self.colormap_max.value = self.field_min_max[field_name][1]
        self.colormap_fixed_toggle.value = bool(self.field_min_max[field_name][2])
        self.skip_cb = False

        # if not self.skip_cb:
        # print("substrate_field_changed_cb: i_plot.update")
        self.i_plot.update()

    # called if user provided different min/max values for colormap, or a different colormap
    def substrate_field_cb(self, b):
        # # if self.skip_cb:
        #     return

        self.field_index = self.substrate_choice.value + 4

        field_name = self.field_dict[self.substrate_choice.value]
        # print('substrate_field_cb: field_name='+ field_name)

        # print('substrate_field_cb: '+ field_name)
        self.field_min_max[field_name][0] = self.colormap_min.value 
        self.field_min_max[field_name][1] = self.colormap_max.value
        self.field_min_max[field_name][2] = self.colormap_fixed_toggle.value
        # print('rwh: substrate_field_cb: ',self.field_min_max)

#        self.field_index = self.substrate_choice.value + 4
#        print('field_index=',self.field_index)
        if not self.skip_cb:
            # print("substrate_field_cb: i_plot.update,  field_index=",self.field_index)
            self.i_plot.update()

    #------------------------------------------------------------
    # Should be called only when we need to *compute* analysis_data
    # def update_analysis_data(self,b):
    def update_analysis_data(self):
        # print('----- update_analysis_data')
        # print('update_analysis_data(): self.output_dir = ', self.output_dir)

        # If we've already computed the plots being requested, just return.
        # if ('live' in self.analysis_data_choice.value) and self.analysis_data_set1:
        #     return
        # elif ('Mac' in self.analysis_data_choice.value) and self.analysis_data_set2:
        #     return
        # elif ('load' in self.analysis_data_choice.value) and self.analysis_data_set3:
        #     return
        # elif ('lymph' in self.analysis_data_choice.value) and self.analysis_data_set4:
        #     return

        # self.analysis_data_wait.value = 'Wait for update...'
        # self.analysis_data_wait.value = 'compute 1st of 4 sets...'

        # self.updated_analysis_flag = True
        self.analysis_data_plotted = True

        cwd = os.getcwd()
        # print("----- cwd(1)=",cwd)
        data_dir = cwd
        # print("----- data_dir(1)=",cwd)

        if 'cache' in self.output_dir:
            data_dir = self.output_dir
            # print("----- chdir to data_dir(2)=",data_dir, " --> chdir to there")
            # os.chdir(data_dir)
        else:
            # print('update_analysis_data: cwd=',cwd)
            if not 'tmpdir' in cwd:
                data_dir = os.path.abspath('tmpdir')
                # print("----- data_dir(3)=",cwd)

        os.chdir(data_dir)

        xml_files = glob.glob('output*.xml')
        # xml_files = glob.glob(os.path.join('tmpdir', 'output*.xml'))
        xml_files.sort()
        # print('update_analysis_data(): len(xml_files)=',len(xml_files))
        # print('xml_files = ',xml_files)
        # print("----- chdir back to cwd=",cwd)
        # os.chdir(cwd)

        ds_count = len(xml_files)
        # print("----- ds_count = ",ds_count)
        mcds = [pyMCDS(xml_files[i], '.') for i in range(ds_count)]  # optimize eventually?
        # # mcds = [pyMCDS(xml_files[i], 'tmpdir') for i in range(ds_count)]
        # # mcds = [pyMCDS(xml_files[i], data_dir) for i in range(ds_count)]
        # print("----- mcds = ",mcds)
        # print(mcds[0].data['discrete_cells'].keys())
#        dict_keys(['ID', 'position_x', 'position_y', 'position_z', 'total_volume', 'cell_type', 'cycle_model', 'current_phase', 'elapsed_time_in_phase', 'nuclear_volume', 'cytoplasmic_volume', 'fluid_fraction', 'calcified_fraction', 'orientation_x', 'orientation_y', 'orientation_z', 'polarity', 'migration_speed', 'motility_vector_x', 'motility_vector_y', 'motility_vector_z', 'migration_bias', 'motility_bias_direction_x', 'motility_bias_direction_y', 'motility_bias_direction_z', 'persistence_time', 'motility_reserved', 'unbound_external_ACE2', 'bound_external_ACE2', 'unbound_internal_ACE2', 'bound_internal_ACE2', 'ACE2_binding_rate', 'ACE2_endocytosis_rate', 'ACE2_cargo_release_rate', 'ACE2_recycling_rate', 'virion', 'uncoated_virion', 'viral_RNA', 'viral_protein', 'assembled_virion', 'virion_uncoating_rate', 'uncoated_to_RNA_rate', 'protein_synthesis_rate', 'virion_assembly_rate', 'virion_export_rate', 'max_infected_apoptosis_rate', 'max_apoptosis_half_max', 'apoptosis_hill_power'])

        # def cell_data_plot(xname, yname_list, t):
        # discrete_cells_names = ['virion', 'assembled_virion']  # not used now
        tval = np.linspace(0, mcds[-1].get_time(), len(xml_files))
        # return

        # if all selected:  ('assembled_virion', 'susceptible', 'infected', 'dead')
        # print('analysis_data_choice = ', self.analysis_data_choice.value)  # get RadioButton selection
        # self.num_2D_plots = len(self.analysis_data_choice.value)
        # print('num_2D_plots = ', self.num_2D_plots)

        xname = 'time'
        if xname == self.tname:
            self.xval = tval
            # print("xname == self.tname")
            # print("#1 self.xval=",self.xval)
        else:
            print("Warning: xname != self.tname")
        # elif xname in discrete_cells_names:
        #     self.xval = np.array([mcds[i].data['discrete_cells'][xname].sum() for i in range(ds_count)])
        # else:
        #     if xname == 'susceptible_cells':
        #         self.xval = np.array([(mcds[i].data['discrete_cells']['assembled_virion'] <= 1).sum() for i in range(ds_count)])
        #         + np.array([(mcds[i].data['discrete_cells']['cycle_model'] < 6).sum() for i in range(ds_count)])
        #     elif xname == 'infected_cells':
        #         self.xval = np.array([(mcds[i].data['discrete_cells']['assembled_virion'] > 1).sum() for i in range(ds_count)]) \
        #         + np.array([(mcds[i].data['discrete_cells']['cycle_model'] < 6).sum() for i in range(ds_count)])
        #     elif xname == 'dead_cells':
        #         self.xval = np.array([len(mcds[0].data['discrete_cells']['ID']) - len(mcds[i].data['discrete_cells']['ID']) for i in range(ds_count)]) \
        #         + np.array([(mcds[i].data['discrete_cells']['cycle_model'] >= 6).sum() for i in range(ds_count)])


        # print('analysis_data_choice = ',self.analysis_data_choice.value)

        # if 'live' in self.analysis_data_choice.value:  # live,infected,dead
        #     if (self.analysis_data_set1 == False):

        self.analysis_data_wait.value = 'compute 1-3...'

        # self.yval1 = np.array( [np.floor(mcds[idx].data['discrete_cells']['internal_chemical_A']).sum()  for idx in range(ds_count)] ).astype(int)
        self.yval1 = np.array( [np.floor(mcds[idx].data['discrete_cells']['internal_chemical_A']).sum()  for idx in range(ds_count)] ).astype(float)
        self.analysis_data_set1 = True 

        self.yval2 = np.array( [np.floor(mcds[idx].data['discrete_cells']['internal_chemical_B']).sum()  for idx in range(ds_count)] ).astype(float)
        self.analysis_data_set2 = True 

        self.yval3 = np.array( [np.floor(mcds[idx].data['discrete_cells']['internal_chemical_C']).sum()  for idx in range(ds_count)] ).astype(float)
        self.analysis_data_set3 = True 

        # self.analysis_data_wait.value = ''
        self.i_plot.update()

    #------------------------------------------------------------
    # def plot_analysis_data_dummy(self):
    #     print('----- plot_analysis_data()')
    #     x = np.linspace(0, 2*np.pi, 400)
    #     y = np.sin(x**2)
    #     # self.i_plot.update()
    #     self.ax1.plot(x, y)

    #------------------------------------------------------------
    # Performed when the "Extra analysis" is toggled off
    def plot_empty_analysis_data(self):
        self.ax1.plot([0.], [0.], color='white',marker='.')  # hack empty
        # self.ax1.clf()
        self.ax1.get_xaxis().set_visible(False)
        self.ax1.get_yaxis().set_visible(False)
        self.ax1.axis('off')

        self.ax2.plot([0.], [0.], color='white',marker='.')  # hack empty
        self.ax3.plot([0.], [0.], color='white',marker='.')  # hack empty

    #------------------------------------------------------------
    # Called from 'plot_substrate' if the checkbox is ON
    # def plot_analysis_data(self, xname, yname_list, t):
    def plot_analysis_data(self, xname, yname_list, substrate_frame_num):
        # print("---------- plot_analysis_data()")
        # global current_idx, axes_max
        global current_frame
        # current_frame = frame
        # fname = "snapshot%08d.svg" % frame
        # full_fname = os.path.join(self.output_dir, fname)
        # print('plot_analysis_data: self.output_dir=',self.output_dir)

        #-----------  line plots for extra analysis ---------------------
        self.ax1_lymph_TC.get_yaxis().set_visible(False)
        self.ax1_lymph_TC.axis('off')

        self.ax1_lymph_TH2.get_yaxis().set_visible(False)
        self.ax1_lymph_TH2.axis('off')

        if self.analysis_data_choice.value == 0:  # live,infected,dead
            p1 = self.ax1.plot(self.xval, self.yval1, label='chem A', linewidth=3)
            p2 = self.ax2.plot(self.xval, self.yval2, label='chem B', linewidth=3)
            p3 = self.ax3.plot(self.xval, self.yval3, label='chem C', linewidth=3)

        # elif self.analysis_data_choice.value == 1:  # Mac,Neut,CD8,DC,CD4,Fib
        #     p1 = self.ax1.plot(self.xval, self.yval4, label='Mac', linewidth=3, color=self.mac_color)
        #     p2 = self.ax1.plot(self.xval, self.yval5, linestyle='dashed', label='Neut', linewidth=3, color=self.neut_color)
        #     p3 = self.ax1.plot(self.xval, self.yval6, label='CD8', linewidth=3, color=self.cd8_color)
        #     p4 = self.ax1.plot(self.xval, self.yval7, linestyle='dashed', label='DC', linewidth=3, color=self.dc_color)
        #     # print('plot_analysis_data(): yval6=',self.yval6)
        #     # print('plot_analysis_data(): yval7=',self.yval7)
        #     p5 = self.ax1.plot(self.xval, self.yval8, label='CD4', linewidth=3, color=self.cd4_color)
        #     p6 = self.ax1.plot(self.xval, self.yval9, linestyle='dashed',  label='Fib', linewidth=3, color=self.fib_color) # dashes=[6,2],
            # print('plot_analysis_data(): yval9=',self.yval9)


        #-----------  markers (circles) on top of line plots: tracking Cells/Substrates plots ---------------------
        # if (t >= 0):
        xoff= self.xval.max() * .01   # should be a % of axes range
        fsize=12
        # kdx = self.substrate_frame
        kdx = substrate_frame_num
        # kdx = len(self.xval) - 1
        # if (kdx >= len(self.xval)):
            # kdx = len(self.xval) - 1
        # print("plot_analysis_data(): t=",t,", kdx=",kdx,", len(self.xval)=",len(self.xval))

        # if (t >= 0 and len(self.xval) > 1):
        # if (substrate_frame_num >= len(self.xval)):
        if (kdx >= len(self.xval)):
            pass
        elif (substrate_frame_num >= 0 and len(self.xval) > 1):
            # print('self.xval=',self.xval)  # [   0.   60.  120. ...

            if self.analysis_data_choice.value == 0:   # live,infected,dead
                self.ax1.plot(self.xval[kdx], self.yval1[kdx], p1[-1].get_color(), marker='o', markersize=12)
                self.ax2.plot(self.xval[kdx], self.yval2[kdx], p2[-1].get_color(), marker='o', markersize=12)
                self.ax3.plot(self.xval[kdx], self.yval3[kdx], p3[-1].get_color(), marker='o', markersize=12)

                # label = "{:d}".format(self.yval1[self.substrate_frame]), 
                # self.ax1.annotate(str(self.yval1[self.substrate_frame]), (self.xval[self.substrate_frame]+xoff,self.yval1[self.substrate_frame]+yoff) )
                ymax= max(int(self.yval1.max()),int(self.yval2.max()),int(self.yval3.max())) # should be a % of axes range
                yoff= ymax * .01   # should be a % of axes range

                # self.ax1.text( self.xval[kdx]+xoff, self.yval1[kdx]+yoff, str(self.yval1[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval2[kdx]+yoff, str(self.yval2[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval3[kdx]+yoff, str(self.yval3[kdx]), fontsize=fsize)
                 
            # elif self.analysis_data_choice.value == 1:  # Mac,Neut,CD8,DC,CD4,Fib
            #     self.ax1.plot(self.xval[kdx], self.yval4[kdx], p1[-1].get_color(), marker='o', markersize=12)
            #     self.ax1.plot(self.xval[kdx], self.yval5[kdx], p2[-1].get_color(), marker='o', markersize=12)
            #     self.ax1.plot(self.xval[kdx], self.yval6[kdx], p3[-1].get_color(), marker='o', markersize=12)
            #     self.ax1.plot(self.xval[kdx], self.yval7[kdx], p4[-1].get_color(), marker='o', markersize=12)
            #     self.ax1.plot(self.xval[kdx], self.yval8[kdx], p5[-1].get_color(), marker='o', markersize=12)
            #     self.ax1.plot(self.xval[kdx], self.yval9[kdx], p6[-1].get_color(), marker='o', markersize=12)

                # label markers
                # ymax= max(int(self.yval4.max()), int(self.yval5.max()), int(self.yval6.max()), int(self.yval7.max()), int(self.yval8.max()), int(self.yval9.max()) ) # should be a % of axes range
                # yoff= ymax * .01   # should be a % of axes range
                # self.ax1.text( self.xval[kdx]+xoff, self.yval4[kdx]+yoff, str(self.yval4[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval5[kdx]+yoff, str(self.yval5[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval6[kdx]+yoff, str(self.yval6[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval7[kdx]+yoff, str(self.yval7[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval8[kdx]+yoff, str(self.yval8[kdx]), fontsize=fsize)
                # self.ax1.text( self.xval[kdx]+xoff, self.yval9[kdx]+yoff, str(self.yval9[kdx]), fontsize=fsize)


        #-------- Provide a legend if necessary
        # if 'load' in self.analysis_data_choice.value:  # no legend for viral load
        if self.analysis_data_choice.value == 2:  # no legend for viral load
            pass
        # elif 'lymph' in self.analysis_data_choice.value:  
        elif (self.analysis_data_choice.value == 3) or (self.analysis_data_choice.value == 4):  
            pass
        else:  
            self.ax1.legend(loc='center left', prop={'size': 15})

        if xname == self.tname:
            self.ax1.set_xlabel('time (min)', fontsize=self.axis_label_fontsize)
        else:
            self.ax1.set_xlabel('total ' * (xname != self.tname) + xname)
#        self.ax1.set_ylabel('total ' + (yname_list[0] if len(yname_list) == 1 else ', '.join(yname_list)))

        # if self.analysis_data_choice.value == 0:   # cells 1-3
        #     self.ax1.set_ylabel('chem A', fontsize=self.axis_label_fontsize)
        # elif self.analysis_data_choice.value == 1:   # Mac, Neut, etc
        #     self.ax1.set_ylabel('# of cells', fontsize=self.axis_label_fontsize)
        # # elif 'load' in self.analysis_data_choice.value:  # viral load
        # elif self.analysis_data_choice.value == 2:  # viral load 
        #     self.ax1.set_ylabel('viral load', fontsize=self.axis_label_fontsize)

        max_time_min = int(self.xval[-1])
        # print('self.xval =',self.xval)
        # print('max_time_min =',max_time_min)
        num_days = int(max_time_min/1440.)
        num_hours = int((max_time_min - num_days*1440.)/60.)
        num_min = int(max_time_min % 60)
        title_str = 'Updated to ' + '%dd, %dh %dm'%(num_days,num_hours,num_min)
        if (self.analysis_data_plotted):
            self.ax1.set_title("Left cell: internal_chemical_A")
            self.ax2.set_title("Middle cell: internal_chemical_B")
            self.ax3.set_title("Right cell: internal_chemical_C")
        else:
            self.ax1.set_xticklabels([])
            self.ax1.set_yticklabels([])
        # p = self.ax1.plot(xval, yval, label=yname)
        # self.ax1.set_legend()
        # self.ax1.tight_layout()
        # self.ax1.show()

    #---------------------------------------------------------------------------
    def circles(self, x, y, s, c='b', vmin=None, vmax=None, **kwargs):
        """
        See https://gist.github.com/syrte/592a062c562cd2a98a83 

        Make a scatter plot of circles. 
        Similar to plt.scatter, but the size of circles are in data scale.
        Parameters
        ----------
        x, y : scalar or array_like, shape (n, )
            Input data
        s : scalar or array_like, shape (n, ) 
            Radius of circles.
        c : color or sequence of color, optional, default : 'b'
            `c` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs.
            Note that `c` should not be a single numeric RGB or RGBA sequence 
            because that is indistinguishable from an array of values
            to be colormapped. (If you insist, use `color` instead.)  
            `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.
        kwargs : `~matplotlib.collections.Collection` properties
            Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
            norm, cmap, transform, etc.
        Returns
        -------
        paths : `~matplotlib.collections.PathCollection`
        Examples
        --------
        a = np.arange(11)
        circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
        plt.colorbar()
        License
        --------
        This code is under [The BSD 3-Clause License]
        (http://opensource.org/licenses/BSD-3-Clause)
        """

        if np.isscalar(c):
            kwargs.setdefault('color', c)
            c = None

        if 'fc' in kwargs:
            kwargs.setdefault('facecolor', kwargs.pop('fc'))
        if 'ec' in kwargs:
            kwargs.setdefault('edgecolor', kwargs.pop('ec'))
        if 'ls' in kwargs:
            kwargs.setdefault('linestyle', kwargs.pop('ls'))
        if 'lw' in kwargs:
            kwargs.setdefault('linewidth', kwargs.pop('lw'))
        # You can set `facecolor` with an array for each patch,
        # while you can only set `facecolors` with a value for all.

        zipped = np.broadcast(x, y, s)
        patches = [Circle((x_, y_), s_)
                for x_, y_, s_ in zipped]
        collection = PatchCollection(patches, **kwargs)
        if c is not None:
            c = np.broadcast_to(c, zipped.shape).ravel()
            collection.set_array(c)
            collection.set_clim(vmin, vmax)

        # ax = plt.gca()
        # ax.add_collection(collection)
        # ax.autoscale_view()
        self.ax0.add_collection(collection)
        self.ax0.autoscale_view()
        # plt.draw_if_interactive()
        if c is not None:
            # plt.sci(collection)
            self.ax0.sci(collection)
        # return collection

    #------------------------------------------------------------
    # def plot_svg(self, frame, rdel=''):
    def plot_svg(self, frame):
        # global current_idx, axes_max
        global current_frame
        current_frame = frame
        fname = "snapshot%08d.svg" % frame
        full_fname = os.path.join(self.output_dir, fname)
        # with debug_view:
            # print("plot_svg:", full_fname) 
        # print("-- plot_svg:", full_fname) 
        if not os.path.isfile(full_fname):
            print("Once output files are generated, click the slider.")   
            return

        xlist = deque()
        ylist = deque()
        rlist = deque()
        rgb_list = deque()

        #  print('\n---- ' + fname + ':')
#        tree = ET.parse(fname)
        tree = ET.parse(full_fname)
        root = tree.getroot()
        #  print('--- root.tag ---')
        #  print(root.tag)
        #  print('--- root.attrib ---')
        #  print(root.attrib)
        #  print('--- child.tag, child.attrib ---')
        numChildren = 0
        for child in root:
            #    print(child.tag, child.attrib)
            #    print("keys=",child.attrib.keys())
            if self.use_defaults and ('width' in child.attrib.keys()):
                self.axes_max = float(child.attrib['width'])
                # print("debug> found width --> axes_max =", axes_max)
            if child.text and "Current time" in child.text:
                svals = child.text.split()
                # remove the ".00" on minutes
                self.title_str += "   cells: " + svals[2] + "d, " + svals[4] + "h, " + svals[7][:-3] + "m"

                # self.cell_time_mins = int(svals[2])*1440 + int(svals[4])*60 + int(svals[7][:-3])
                # self.title_str += "   cells: " + str(self.cell_time_mins) + "m"   # rwh

            # print("width ",child.attrib['width'])
            # print('attrib=',child.attrib)
            # if (child.attrib['id'] == 'tissue'):
            if ('id' in child.attrib.keys()):
                # print('-------- found tissue!!')
                tissue_parent = child
                break

        # print('------ search tissue')
        cells_parent = None

        for child in tissue_parent:
            # print('attrib=',child.attrib)
            if (child.attrib['id'] == 'cells'):
                # print('-------- found cells, setting cells_parent')
                cells_parent = child
                break
            numChildren += 1

        num_cells = 0
        #  print('------ search cells')
        for child in cells_parent:
            #    print(child.tag, child.attrib)
            #    print('attrib=',child.attrib)
            for circle in child:  # two circles in each child: outer + nucleus
                #  circle.attrib={'cx': '1085.59','cy': '1225.24','fill': 'rgb(159,159,96)','r': '6.67717','stroke': 'rgb(159,159,96)','stroke-width': '0.5'}
                #      print('  --- cx,cy=',circle.attrib['cx'],circle.attrib['cy'])
                xval = float(circle.attrib['cx'])

                # map SVG coords into comp domain
                # xval = (xval-self.svg_xmin)/self.svg_xrange * self.x_range + self.xmin
                xval = xval/self.x_range * self.x_range + self.xmin

                s = circle.attrib['fill']
                # print("s=",s)
                # print("type(s)=",type(s))
                if (s[0:3] == "rgb"):  # if an rgb string, e.g. "rgb(175,175,80)" 
                    rgb = list(map(int, s[4:-1].split(",")))  
                    rgb[:] = [x / 255. for x in rgb]
                else:     # otherwise, must be a color name
                    rgb_tuple = mplc.to_rgb(mplc.cnames[s])  # a tuple
                    rgb = [x for x in rgb_tuple]

                # test for bogus x,y locations (rwh TODO: use max of domain?)
                too_large_val = 10000.
                if (np.fabs(xval) > too_large_val):
                    print("bogus xval=", xval)
                    break
                yval = float(circle.attrib['cy'])
                # yval = (yval - self.svg_xmin)/self.svg_xrange * self.y_range + self.ymin
                yval = yval/self.y_range * self.y_range + self.ymin
                if (np.fabs(yval) > too_large_val):
                    print("bogus xval=", xval)
                    break

                rval = float(circle.attrib['r'])
                # if (rgb[0] > rgb[1]):
                #     print(num_cells,rgb, rval)
                xlist.append(xval)
                ylist.append(yval)
                rlist.append(rval)
                rgb_list.append(rgb)

                # For .svg files with cells that *have* a nucleus, there will be a 2nd
                if (not self.show_nucleus):
                #if (not self.show_nucleus):
                    break

            num_cells += 1

            # if num_cells > 3:   # for debugging
            #   print(fname,':  num_cells= ',num_cells," --- debug exit.")
            #   sys.exit(1)
            #   break

            # print(fname,':  num_cells= ',num_cells)

        xvals = np.array(xlist)
        yvals = np.array(ylist)
        rvals = np.array(rlist)
        rgbs = np.array(rgb_list)
        # print("xvals[0:5]=",xvals[0:5])
        # print("rvals[0:5]=",rvals[0:5])
        # print("rvals.min, max=",rvals.min(),rvals.max())

        # rwh - is this where I change size of render window?? (YES - yipeee!)
        #   plt.figure(figsize=(6, 6))
        #   plt.cla()
        # if (self.substrates_toggle.value):
        self.title_str += " (" + str(num_cells) + " agents)"
            # title_str = " (" + str(num_cells) + " agents)"
        # else:
            # mins= round(int(float(root.find(".//current_time").text)))  # TODO: check units = mins
            # hrs = int(mins/60)
            # days = int(hrs/24)
            # title_str = '%dd, %dh, %dm' % (int(days),(hrs%24), mins - (hrs*60))
        # plt.title(self.title_str)
        self.ax0.set_title(self.title_str)

        # plt.xlim(self.xmin, self.xmax)
        # plt.ylim(self.ymin, self.ymax)
        self.ax0.set_xlim(self.xmin, self.xmax)
        self.ax0.set_ylim(self.ymin, self.ymax)

        # self.ax0.colorbar(collection)

        #   plt.xlim(axes_min,axes_max)
        #   plt.ylim(axes_min,axes_max)
        #   plt.scatter(xvals,yvals, s=rvals*scale_radius, c=rgbs)

        # TODO: make figsize a function of plot_size? What about non-square plots?
        # self.fig = plt.figure(figsize=(9, 9))

#        axx = plt.axes([0, 0.05, 0.9, 0.9])  # left, bottom, width, height
#        axx = fig.gca()
#        print('fig.dpi=',fig.dpi) # = 72

        #   im = ax.imshow(f.reshape(100,100), interpolation='nearest', cmap=cmap, extent=[0,20, 0,20])
        #   ax.xlim(axes_min,axes_max)
        #   ax.ylim(axes_min,axes_max)

        # convert radii to radii in pixels
        # ax1 = self.fig.gca()
        # N = len(xvals)
        # rr_pix = (ax1.transData.transform(np.vstack([rvals, rvals]).T) -
        #             ax1.transData.transform(np.vstack([np.zeros(N), np.zeros(N)]).T))
        # rpix, _ = rr_pix.T

        # markers_size = (144. * rpix / self.fig.dpi)**2   # = (2*rpix / fig.dpi * 72)**2
        # markers_size = markers_size/4000000.
        # print('max=',markers_size.max())

        #rwh - temp fix - Ah, error only occurs when "edges" is toggled on
        if (self.show_edge):
            try:
                # plt.scatter(xvals,yvals, s=markers_size, c=rgbs, edgecolor='black', linewidth=0.5)
                self.circles(xvals,yvals, s=rvals, color=rgbs, alpha=self.alpha, edgecolor='black', linewidth=0.5)
                # cell_circles = self.circles(xvals,yvals, s=rvals, color=rgbs, edgecolor='black', linewidth=0.5)
                # plt.sci(cell_circles)
            except (ValueError):
                pass
        else:
            # plt.scatter(xvals,yvals, s=markers_size, c=rgbs)
            self.circles(xvals,yvals, s=rvals, color=rgbs, alpha=self.alpha)

        # im = ax.imshow(np.arange(100).reshape((10, 10)))   # rwh: dummy, for future testing
        # cbar = self.fig.colorbar(substrate_plot, ax=self.ax0)
        # plt.colorbar(im, cax=cax)

        # x = np.linspace(0, 2*np.pi, 100)
        # y = np.sin(x**2)
        # self.i_plot.update()
        # self.ax1.plot(x, y)
        # self.plot_analysis_data_0("time", ["assembled_virion"], 20)

        # if (self.show_tracks):
        #     for key in self.trackd.keys():
        #         xtracks = self.trackd[key][:,0]
        #         ytracks = self.trackd[key][:,1]
        #         plt.plot(xtracks[0:frame],ytracks[0:frame],  linewidth=5)


    #---------------------------------------------------------------------------
    # assume "frame" is cell frame #, unless Cells is togggled off, then it's the substrate frame #
    # def plot_substrate(self, frame, grid):
    def plot_substrate(self, frame):

        # print("plot_substrate(): frame*self.substrate_delta_t  = ",frame*self.substrate_delta_t)
        # print("plot_substrate(): frame*self.svg_delta_t  = ",frame*self.svg_delta_t)
        # print("plot_substrate(): fig width: SVG+2D = ",self.figsize_width_svg + self.figsize_width_2Dplot)  # 24
        # print("plot_substrate(): fig width: substrate+2D = ",self.figsize_width_substrate + self.figsize_width_2Dplot)  # 27

        self.title_str = ''

        # Recall:
        # self.svg_delta_t = config_tab.svg_interval.value
        # self.substrate_delta_t = config_tab.mcds_interval.value
        # self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
        # self.therapy_activation_time = user_params_tab.therapy_activation_time.value

        # print("plot_substrate(): pre_therapy: max svg, substrate frames = ",max_svg_frame_pre_therapy, max_substrate_frame_pre_therapy)

        # Assume: # .svg files >= # substrate files
#        if (self.cells_toggle.value):

        if self.substrates_toggle.value:
            # maybe only show 2nd plot if self.analysis_data_toggle is True
            # if self.analysis_data_toggle.value:  # substrates and 2D plots 
            if True:  # substrates and 2D plots 
                # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(30, 12))
                # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(self.figsize_width_substrate + self.figsize_width_2Dplot, self.figsize_height_substrate))
                # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(31, self.figsize_height_substrate), gridspec_kw={'width_ratios': [1.35, 1]})
                # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(31, 13), gridspec_kw={'width_ratios': [1.35, 1]})

                # Instead of the typical 'plt.figure()', do this for a multi-plot arrangement:
                #   plt.subplots(# rows, # cols, ...)

                #  -- following used by pc4covid19:
                # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(34, 15), gridspec_kw={'width_ratios': [1.5, 1]})


                # Furkan?
                # self.fig, (self.ax0, self.ax1, self.ax2, self.ax3) = plt.subplots(2, 2, figsize=(34, 34), gridspec_kw={'width_ratios': [1.,1.,1.,1.]})

                self.fig = plt.figure(figsize=(12, 12), constrained_layout=True)
                widths = [1, 1]
                heights = [1, 1]
                spec5 = self.fig.add_gridspec(ncols=2, nrows=2, width_ratios=widths,
                                        height_ratios=heights)
                self.ax0 = self.fig.add_subplot(spec5[0, 0])
                # label = 'Width: {}\nHeight: {}'.format(widths[col], heights[row])
                label = 'yipeee  ax0'
                self.ax0.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                self.ax1 = self.fig.add_subplot(spec5[0, 1])
                label = 'yipeee  ax1'
                self.ax1.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                self.ax2 = self.fig.add_subplot(spec5[1, 0])
                label = 'yipeee  ax2'
                self.ax2.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                self.ax3 = self.fig.add_subplot(spec5[1, 1])
                label = 'yipeee  ax3'
                self.ax3.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')
                # self.fig, (self.ax0, self.ax1, self.ax2, self.ax3, self.ax4, self.ax5) = plt.subplots(3, 2, figsize=(34, 34), gridspec_kw={'width_ratios': [1.,1.,1.,1.,1.,1.]})

                # Specify 2 different y-axes ranges for the lymph node data plot:
                self.ax1_lymph_TC = self.ax1.twinx()
                self.ax1_lymph_TH2 = self.ax1.twinx()

            # else:  # substrates plot, but no 2D plot
            #     print('plot sub:  sub w,h= ',self.figsize_width_substrate,self.figsize_height_substrate)
            #     self.fig, (self.ax0) = plt.subplots(1, 1, figsize=(self.figsize_width_substrate, self.figsize_height_substrate))
            #     # self.fig, (self.ax0) = plt.subplots(1, 1, figsize=(12, 12))


            if (self.customized_output_freq and (frame > self.max_svg_frame_pre_therapy)):
                self.substrate_frame = self.max_substrate_frame_pre_therapy + (frame - self.max_svg_frame_pre_therapy)
            else:
                self.substrate_frame = int(frame / self.modulo)

            fname = "output%08d_microenvironment0.mat" % self.substrate_frame
            xml_fname = "output%08d.xml" % self.substrate_frame
            # fullname = output_dir_str + fname

    #        fullname = fname
            full_fname = os.path.join(self.output_dir, fname)
            # print("--- plot_substrate(): full_fname=",full_fname)
            full_xml_fname = os.path.join(self.output_dir, xml_fname)
    #        self.output_dir = '.'

    #        if not os.path.isfile(fullname):
            if not os.path.isfile(full_fname):
                print("Once output files are generated, click the slider.")  # No:  output00000000_microenvironment0.mat
                return

    #        tree = ET.parse(xml_fname)
            tree = ET.parse(full_xml_fname)
            xml_root = tree.getroot()
            mins = round(int(float(xml_root.find(".//current_time").text)))  # TODO: check units = mins
            self.substrate_mins= round(int(float(xml_root.find(".//current_time").text)))  # TODO: check units = mins

            hrs = int(mins/60)
            days = int(hrs/24)
            self.title_str = 'substrate: %dd, %dh, %dm' % (int(days),(hrs%24), mins - (hrs*60))
            # self.title_str = 'substrate: %dm' % (mins )   # rwh

            info_dict = {}
            scipy.io.loadmat(full_fname, info_dict)
            M = info_dict['multiscale_microenvironment']
            f = M[self.field_index, :]   # 4=tumor cells field, 5=blood vessel density, 6=growth substrate

            try:
                xgrid = M[0, :].reshape(self.numy, self.numx)
                ygrid = M[1, :].reshape(self.numy, self.numx)
            except:
                print("substrates.py: mismatched mesh size for reshape: numx,numy=",self.numx, self.numy)
                pass
#                xgrid = M[0, :].reshape(self.numy, self.numx)
#                ygrid = M[1, :].reshape(self.numy, self.numx)

            num_contours = 15
            levels = MaxNLocator(nbins=num_contours).tick_values(self.colormap_min.value, self.colormap_max.value)
            contour_ok = True
            if (self.colormap_fixed_toggle.value):
                try:
                    substrate_plot = self.ax0.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy, self.numx), levels=levels, extend='both', cmap=self.colormap_dd.value, fontsize=self.fontsize)
                except:
                    contour_ok = False
                    # print('got error on contourf 1.')
            else:    
                try:
                    substrate_plot = self.ax0.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy,self.numx), num_contours, cmap=self.colormap_dd.value)
                except:
                    contour_ok = False
                    # print('got error on contourf 2.')

            if (contour_ok):
                self.ax0.set_title(self.title_str, fontsize=self.fontsize)
                cbar = self.fig.colorbar(substrate_plot, ax=self.ax0)
                cbar.ax.tick_params(labelsize=self.fontsize)

            self.ax0.set_xlim(self.xmin, self.xmax)
            self.ax0.set_ylim(self.ymin, self.ymax)

        # Now plot the cells (possibly on top of the substrate)
        if self.cells_toggle.value:
            if not self.substrates_toggle.value:
                if True:  # cells (SVG), but no 2D plot (and no substrate)
                    # self.fig, (self.ax0, self.ax1) = plt.subplots(1, 2, figsize=(25, self.figsize_height_substrate), gridspec_kw={'width_ratios': [1.1, 1]})

                    # Furkan?
                    self.fig = plt.figure(figsize=(12, 12), constrained_layout=True)
                    widths = [1, 1]
                    heights = [1, 1]
                    spec5 = self.fig.add_gridspec(ncols=2, nrows=2, width_ratios=widths,
                                            height_ratios=heights)
                    self.ax0 = self.fig.add_subplot(spec5[0, 0])
                    # label = 'Width: {}\nHeight: {}'.format(widths[col], heights[row])
                    label = 'yipeee  ax0'
                    self.ax0.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                    self.ax1 = self.fig.add_subplot(spec5[0, 1])
                    label = 'yipeee  ax1'
                    self.ax1.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                    self.ax2 = self.fig.add_subplot(spec5[1, 0])
                    label = 'yipeee  ax2'
                    self.ax2.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                    self.ax3 = self.fig.add_subplot(spec5[1, 1])
                    label = 'yipeee  ax3'
                    self.ax3.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')
                    # for row in range(2):
                    #     for col in range(2):
                    #         ax = self.fig.add_subplot(spec5[row, col])
                    #         label = 'Width: {}\nHeight: {}'.format(widths[col], heights[row])
                    #         ax.annotate(label, (0.1, 0.5), xycoords='axes fraction', va='center')

                    # self.fig = plt.figure(constrained_layout=False)
                    # gs1 = self.fig.add_gridspec(nrows=2, ncols=2, left=0.05, right=0.48, wspace=0.05)
                    # self.ax0 = self.fig.add_subplot(gs1[:-1, 0])
                    # self.ax1 = self.fig.add_subplot(gs1[-1, :-1])
                    # self.ax2 = self.fig.add_subplot(gs1[-1, -1])
                    # self.ax3 = self.fig.add_subplot(gs1[-1, -1])

                    # self.fig, (self.ax0, self.ax1, self.ax2, self.ax3) = plt.subplots(2, 2, figsize=(34, 34))
                    # self.fig, (self.ax0, self.ax1, self.ax2, self.ax3) = plt.subplots(2, 2, figsize=(34, 34), gridspec_kw={'width_ratios': [1.,1.,1.,1.]})
                        # plt.subplots(nrows=3, ncols=2, 
                    # self.fig, (self.ax0, self.ax1, self.ax2, self.ax3 , self.ax4, self.ax5) = \
                    # self.fig, (self.ax0, self.ax1, self.ax2) = \
                    #     plt.subplots(nrows=2, ncols=2, 
                    #     figsize=(25, self.figsize_height_substrate) ,
                    #     gridspec_kw={'width_ratios': [0.5,0.5]} )
                    
                    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
                    # x = np.linspace(0, 2 * np.pi, 100)
                    # y = np.sin(x ** 2)
                    # self.fig, axs = plt.subplots(2, 2)
                    # axs[0, 0].plot(x, y)
                    # axs[0, 1].plot(x, y, 'tab:orange')
                    # axs[1, 0].plot(x, -y, 'tab:green')
                    # axs[1, 1].plot(x, -y, 'tab:red')


                    self.ax1_lymph_TC = self.ax1.twinx()
                    self.ax1_lymph_TH2 = self.ax1.twinx()


            self.svg_frame = frame
            # print('plot_svg with frame=',self.svg_frame)
            self.plot_svg(self.svg_frame)
            # cbar = self.fig.colorbar(substrate_plot, ax=self.ax0)

        if (self.analysis_data_toggle.value):
        # if (self.substrate_frame > 0):  # rwh: when to plot extra analysis (custom data)?
            # print('analysis_data_toggle.value =',self.analysis_data_toggle.value )
            # self.plot_analysis_data("time", ["assembled_virion"], -1)
            # print('self.substrate_frame = ',self.substrate_frame)
            self.substrate_frame = int(frame / self.modulo)
            self.plot_analysis_data("time", ["assembled_virion"], self.substrate_frame)
        else:
            self.plot_empty_analysis_data()