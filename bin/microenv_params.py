 
# This file is auto-generated from a Python script that parses a PhysiCell configuration (.xml) file.
#
# Edit at your own risk.
#
import os
from ipywidgets import Label,Text,Checkbox,Button,HBox,VBox,FloatText,IntText,BoundedIntText,BoundedFloatText,Layout,Box
    
class MicroenvTab(object):

    def __init__(self):
        
        micron_units = Label('micron')   # use "option m" (Mac, for micro symbol)

        constWidth = '180px'
        tab_height = '500px'
        stepsize = 10

        #style = {'description_width': '250px'}
        style = {'description_width': '25%'}
        layout = {'width': '400px'}

        name_button_layout={'width':'25%'}
        widget_layout = {'width': '15%'}
        widget2_layout = {'width': '10%'}
        units_button_layout ={'width':'15%'}
        desc_button_layout={'width':'45%'}


        menv_var1 = Button(description='chemical_A (mmol)', disabled=True, layout=name_button_layout)
        menv_var1.style.button_color = 'tan'

        param_name1 = Button(description='diffusion_coefficient', disabled=True, layout=name_button_layout)

        self.chemical_A_diffusion_coefficient = FloatText(value=1000.0,
          step=100,style=style, layout=widget_layout)

        param_name2 = Button(description='decay_rate', disabled=True, layout=name_button_layout)

        self.chemical_A_decay_rate = FloatText(value=0.0,
          step=0.01,style=style, layout=widget_layout)
        param_name3 = Button(description='initial_condition', disabled=True, layout=name_button_layout)

        self.chemical_A_initial_condition = FloatText(value=1.0,style=style, layout=widget_layout)
        param_name4 = Button(description='Dirichlet_boundary_condition', disabled=True, layout=name_button_layout)

        self.chemical_A_Dirichlet_boundary_condition = FloatText(value=0.0,style=style, layout=widget_layout)
        self.chemical_A_Dirichlet_boundary_condition_toggle = Checkbox(description='on/off', disabled=False,style=style, layout=widget_layout)

        menv_var2 = Button(description='chemical_B (mmol)', disabled=True, layout=name_button_layout)
        menv_var2.style.button_color = 'lightgreen'

        param_name5 = Button(description='diffusion_coefficient', disabled=True, layout=name_button_layout)

        self.chemical_B_diffusion_coefficient = FloatText(value=1000.0,
          step=100,style=style, layout=widget_layout)

        param_name6 = Button(description='decay_rate', disabled=True, layout=name_button_layout)

        self.chemical_B_decay_rate = FloatText(value=0.0,
          step=0.01,style=style, layout=widget_layout)
        param_name7 = Button(description='initial_condition', disabled=True, layout=name_button_layout)

        self.chemical_B_initial_condition = FloatText(value=0.0,style=style, layout=widget_layout)
        param_name8 = Button(description='Dirichlet_boundary_condition', disabled=True, layout=name_button_layout)

        self.chemical_B_Dirichlet_boundary_condition = FloatText(value=0.0,style=style, layout=widget_layout)
        self.chemical_B_Dirichlet_boundary_condition_toggle = Checkbox(description='on/off', disabled=False,style=style, layout=widget_layout)

        menv_var3 = Button(description='chemical_C (mmol)', disabled=True, layout=name_button_layout)
        menv_var3.style.button_color = 'tan'

        param_name9 = Button(description='diffusion_coefficient', disabled=True, layout=name_button_layout)

        self.chemical_C_diffusion_coefficient = FloatText(value=1000.0,
          step=100,style=style, layout=widget_layout)

        param_name10 = Button(description='decay_rate', disabled=True, layout=name_button_layout)

        self.chemical_C_decay_rate = FloatText(value=0.0,
          step=0.01,style=style, layout=widget_layout)
        param_name11 = Button(description='initial_condition', disabled=True, layout=name_button_layout)

        self.chemical_C_initial_condition = FloatText(value=0.5,style=style, layout=widget_layout)
        param_name12 = Button(description='Dirichlet_boundary_condition', disabled=True, layout=name_button_layout)

        self.chemical_C_Dirichlet_boundary_condition = FloatText(value=0.0,style=style, layout=widget_layout)
        self.chemical_C_Dirichlet_boundary_condition_toggle = Checkbox(description='on/off', disabled=False,style=style, layout=widget_layout)
        self.calculate_gradient = Checkbox(description='calculate_gradients', disabled=False, layout=desc_button_layout)
        self.track_internal = Checkbox(description='track_in_agents', disabled=False, layout=desc_button_layout)


         #  ------- micronenv info
        menv_units_button1 = Button(description='micron^2/min', disabled=True, layout=units_button_layout) 
        menv_units_button2 = Button(description='1/min', disabled=True, layout=units_button_layout) 
        menv_units_button3 = Button(description='mmol', disabled=True, layout=units_button_layout) 
        menv_units_button4 = Button(description='mmol', disabled=True, layout=units_button_layout) 
        menv_units_button5 = Button(description='micron^2/min', disabled=True, layout=units_button_layout) 
        menv_units_button6 = Button(description='1/min', disabled=True, layout=units_button_layout) 
        menv_units_button7 = Button(description='mmol', disabled=True, layout=units_button_layout) 
        menv_units_button8 = Button(description='mmol', disabled=True, layout=units_button_layout) 
        menv_units_button9 = Button(description='micron^2/min', disabled=True, layout=units_button_layout) 
        menv_units_button10 = Button(description='1/min', disabled=True, layout=units_button_layout) 
        menv_units_button11 = Button(description='mmol', disabled=True, layout=units_button_layout) 
        menv_units_button12 = Button(description='mmol', disabled=True, layout=units_button_layout) 




        row_chemical_A = [menv_var1,  ] 
        row1 = [param_name1, self.chemical_A_diffusion_coefficient, menv_units_button1]
        row2 = [param_name2, self.chemical_A_decay_rate, menv_units_button2]
        row3 = [param_name3, self.chemical_A_initial_condition, menv_units_button3]
        row4 = [param_name4, self.chemical_A_Dirichlet_boundary_condition, menv_units_button4, self.chemical_A_Dirichlet_boundary_condition_toggle]
        row_chemical_B = [menv_var2,  ] 
        row5 = [param_name5, self.chemical_B_diffusion_coefficient, menv_units_button5]
        row6 = [param_name6, self.chemical_B_decay_rate, menv_units_button6]
        row7 = [param_name7, self.chemical_B_initial_condition, menv_units_button7]
        row8 = [param_name8, self.chemical_B_Dirichlet_boundary_condition, menv_units_button8, self.chemical_B_Dirichlet_boundary_condition_toggle]
        row_chemical_C = [menv_var3,  ] 
        row9 = [param_name9, self.chemical_C_diffusion_coefficient, menv_units_button9]
        row10 = [param_name10, self.chemical_C_decay_rate, menv_units_button10]
        row11 = [param_name11, self.chemical_C_initial_condition, menv_units_button11]
        row12 = [param_name12, self.chemical_C_Dirichlet_boundary_condition, menv_units_button12, self.chemical_C_Dirichlet_boundary_condition_toggle]
        row13 = [self.calculate_gradient,]
        row14 = [self.track_internal,]


        box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')
        box_chemical_A = Box(children=row_chemical_A, layout=box_layout)
        box1 = Box(children=row1, layout=box_layout)
        box2 = Box(children=row2, layout=box_layout)
        box3 = Box(children=row3, layout=box_layout)
        box4 = Box(children=row4, layout=box_layout)
        box_chemical_B = Box(children=row_chemical_B, layout=box_layout)
        box5 = Box(children=row5, layout=box_layout)
        box6 = Box(children=row6, layout=box_layout)
        box7 = Box(children=row7, layout=box_layout)
        box8 = Box(children=row8, layout=box_layout)
        box_chemical_C = Box(children=row_chemical_C, layout=box_layout)
        box9 = Box(children=row9, layout=box_layout)
        box10 = Box(children=row10, layout=box_layout)
        box11 = Box(children=row11, layout=box_layout)
        box12 = Box(children=row12, layout=box_layout)
        box13 = Box(children=row13, layout=box_layout)
        box14 = Box(children=row14, layout=box_layout)

        self.tab = VBox([
          box_chemical_A,
          box1,
          box2,
          box3,
          box4,
          box_chemical_B,
          box5,
          box6,
          box7,
          box8,
          box_chemical_C,
          box9,
          box10,
          box11,
          box12,
          box13,
          box14,
        ])

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point

        self.chemical_A_diffusion_coefficient.value = float(vp[0].find('.//diffusion_coefficient').text)
        self.chemical_A_decay_rate.value = float(vp[0].find('.//decay_rate').text)
        self.chemical_A_initial_condition.value = float(vp[0].find('.//initial_condition').text)
        self.chemical_A_Dirichlet_boundary_condition.value = float(vp[0].find('.//Dirichlet_boundary_condition').text)
        if vp[0].find('.//Dirichlet_boundary_condition').attrib['enabled'].lower() == 'true':
          self.chemical_A_Dirichlet_boundary_condition_toggle.value = True
        else:
          self.chemical_A_Dirichlet_boundary_condition_toggle.value = False

        self.chemical_B_diffusion_coefficient.value = float(vp[1].find('.//diffusion_coefficient').text)
        self.chemical_B_decay_rate.value = float(vp[1].find('.//decay_rate').text)
        self.chemical_B_initial_condition.value = float(vp[1].find('.//initial_condition').text)
        self.chemical_B_Dirichlet_boundary_condition.value = float(vp[1].find('.//Dirichlet_boundary_condition').text)
        if vp[1].find('.//Dirichlet_boundary_condition').attrib['enabled'].lower() == 'true':
          self.chemical_B_Dirichlet_boundary_condition_toggle.value = True
        else:
          self.chemical_B_Dirichlet_boundary_condition_toggle.value = False

        self.chemical_C_diffusion_coefficient.value = float(vp[2].find('.//diffusion_coefficient').text)
        self.chemical_C_decay_rate.value = float(vp[2].find('.//decay_rate').text)
        self.chemical_C_initial_condition.value = float(vp[2].find('.//initial_condition').text)
        self.chemical_C_Dirichlet_boundary_condition.value = float(vp[2].find('.//Dirichlet_boundary_condition').text)
        if vp[2].find('.//Dirichlet_boundary_condition').attrib['enabled'].lower() == 'true':
          self.chemical_C_Dirichlet_boundary_condition_toggle.value = True
        else:
          self.chemical_C_Dirichlet_boundary_condition_toggle.value = False

        if uep.find('.//options//calculate_gradients').text.lower() == 'true':
          self.calculate_gradient.value = True
        else:
          self.calculate_gradient.value = False
        if uep.find('.//options//track_internalized_substrates_in_each_agent').text.lower() == 'true':
          self.track_internal.value = True
        else:
          self.track_internal.value = False
        


    # Read values from the GUI widgets to enable editing XML
    def fill_xml(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp[0].find('.//diffusion_coefficient').text = str(self.chemical_A_diffusion_coefficient.value)
        vp[0].find('.//decay_rate').text = str(self.chemical_A_decay_rate.value)
        vp[0].find('.//initial_condition').text = str(self.chemical_A_initial_condition.value)
        vp[0].find('.//Dirichlet_boundary_condition').text = str(self.chemical_A_Dirichlet_boundary_condition.value)
        vp[0].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(self.chemical_A_Dirichlet_boundary_condition_toggle.value).lower()

        vp[1].find('.//diffusion_coefficient').text = str(self.chemical_B_diffusion_coefficient.value)
        vp[1].find('.//decay_rate').text = str(self.chemical_B_decay_rate.value)
        vp[1].find('.//initial_condition').text = str(self.chemical_B_initial_condition.value)
        vp[1].find('.//Dirichlet_boundary_condition').text = str(self.chemical_B_Dirichlet_boundary_condition.value)
        vp[1].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(self.chemical_B_Dirichlet_boundary_condition_toggle.value).lower()

        vp[2].find('.//diffusion_coefficient').text = str(self.chemical_C_diffusion_coefficient.value)
        vp[2].find('.//decay_rate').text = str(self.chemical_C_decay_rate.value)
        vp[2].find('.//initial_condition').text = str(self.chemical_C_initial_condition.value)
        vp[2].find('.//Dirichlet_boundary_condition').text = str(self.chemical_C_Dirichlet_boundary_condition.value)
        vp[2].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(self.chemical_C_Dirichlet_boundary_condition_toggle.value).lower()


        uep.find('.//options//calculate_gradients').text = str(self.calculate_gradient.value)
        uep.find('.//options//track_internalized_substrates_in_each_agent').text = str(self.track_internal.value)
