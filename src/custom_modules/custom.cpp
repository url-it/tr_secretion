/*
###############################################################################
# If you use PhysiCell in your project, please cite PhysiCell and the version #
# number, such as below:                                                      #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1].    #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# See VERSION.txt or call get_PhysiCell_version() to get the current version  #
#     x.y.z. Call display_citations() to get detailed information on all cite-#
#     able software used in your PhysiCell application.                       #
#                                                                             #
# Because PhysiCell extensively uses BioFVM, we suggest you also cite BioFVM  #
#     as below:                                                               #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1],    #
# with BioFVM [2] to solve the transport equations.                           #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# [2] A Ghaffarizadeh, SH Friedman, and P Macklin, BioFVM: an efficient para- #
#     llelized diffusive transport solver for 3-D biological simulations,     #
#     Bioinformatics 32(8): 1256-8, 2016. DOI: 10.1093/bioinformatics/btv730  #
#                                                                             #
###############################################################################
#                                                                             #
# BSD 3-Clause License (see https://opensource.org/licenses/BSD-3-Clause)     #
#                                                                             #
# Copyright (c) 2015-2018, Paul Macklin and the PhysiCell Project             #
# All rights reserved.                                                        #
#                                                                             #
# Redistribution and use in source and binary forms, with or without          #
# modification, are permitted provided that the following conditions are met: #
#                                                                             #
# 1. Redistributions of source code must retain the above copyright notice,   #
# this list of conditions and the following disclaimer.                       #
#                                                                             #
# 2. Redistributions in binary form must reproduce the above copyright        #
# notice, this list of conditions and the following disclaimer in the         #
# documentation and/or other materials provided with the distribution.        #
#                                                                             #
# 3. Neither the name of the copyright holder nor the names of its            #
# contributors may be used to endorse or promote products derived from this   #
# software without specific prior written permission.                         #
#                                                                             #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE   #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE  #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE   #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR         #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF        #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS    #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN     #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)     #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE  #
# POSSIBILITY OF SUCH DAMAGE.                                                 #
#                                                                             #
###############################################################################
*/

#include "./custom.h"

// declare cell definitions here 

//rwh - this may have caused original problemss??
// Cell_Definition first_cell;
// Cell_Definition second_cell;
// Cell_Definition third_cell;

void create_cell_types( void )
{
	cell_defaults.functions.volume_update_function = standard_volume_update_function;
	cell_defaults.functions.update_velocity = standard_update_cell_velocity;

	cell_defaults.functions.update_migration_bias = NULL; 
	cell_defaults.functions.update_phenotype = NULL;   
	cell_defaults.functions.custom_cell_rule = NULL; 
	
	cell_defaults.functions.add_cell_basement_membrane_interactions = NULL; 
	cell_defaults.functions.calculate_distance_to_membrane = NULL; 
	
	/*
	   This parses the cell definitions in the XML config file. 
	*/
	
	initialize_cell_definitions_from_pugixml(); 
	
	/* 
	   Put any modifications to individual cell definitions here. 
	   
	   This is a good place to set custom functions. 
	*/ 

	cell_defaults.phenotype.mechanics.attachment_elastic_constant = parameters.doubles( "elastic_coefficient" );
	
	// static int first_ID = find_cell_definition( "first cell" )->type; 
	// static int second_ID = find_cell_definition( "second cell" )->type; 
	// static int third_ID = find_cell_definition( "third cell" )->type; 

	static int chemical_A_substrate_index = microenvironment.find_density_index( "chemical_A" );
	static int chemical_B_substrate_index = microenvironment.find_density_index( "chemical_B" ); 
    static int chemical_C_substrate_index = microenvironment.find_density_index( "chemical_C");

    //rwh: note that now we use a pointer, pCD, not an instance, to the object.
	Cell_Definition* pCD = find_cell_definition( "first cell" ); 

	/*
	   This builds the map of cell definitions and summarizes the setup. 
	*/
		
	build_cell_definitions_maps(); 
	display_cell_definitions( std::cout ); 
	
	return; 
}

void setup_microenvironment( void )
{
	// make sure to override and go back to 2D 
	if( default_microenvironment_options.simulate_2D == false )
	{
		std::cout << "Warning: overriding XML config option and setting to 2D!" << std::endl; 
		default_microenvironment_options.simulate_2D = true; 
	}
	
	initialize_microenvironment(); 

/* 
    for( int n = 0; n < microenvironment.mesh.voxels.size() ; n++ )	
    {
        std::vector<double> dc_conditions(3);
        dc_conditions[0]=1.0;
        dc_conditions[1]=0.0;
        dc_conditions[2]=0.0;
		microenvironment.add_dirichlet_node( n,dc_conditions);
    }
    microenvironment.set_substrate_dirichlet_activation(0,true);
    microenvironment.set_substrate_dirichlet_activation(1,true);
    microenvironment.set_substrate_dirichlet_activation(2,true); */
	return; 
}

void setup_tissue( void )
{
    // load cells from your CSV file (if enabled)
	if (load_cells_from_pugixml())
    {
        std::cout << __FUNCTION__ << ": finished loading cells from .csv file in /config" << std::endl;
    }

    else {
        std::cout << __FUNCTION__ << ": ERROR - need to supply .csv in /config" << std::endl;
        std::exit(-1);

	// create some cells near the origin
        // Cell* pC;

        // static int chemical_A_substrate_index = microenvironment.find_density_index( "chemical_A" );
        // static int chemical_B_substrate_index = microenvironment.find_density_index( "chemical_B" ); 
        // static int chemical_C_substrate_index = microenvironment.find_density_index( "chemical_C");
        // std::cout << "----- setup_tissue: chem A,B,C indices= " << chemical_A_substrate_index <<", "<< chemical_B_substrate_index <<", "<< chemical_C_substrate_index << std::endl;  // = 0,1,2

        // pC = create_cell(first_cell); 
        // pC->assign_position( -50.0, 0.0, 0.0 );
        // // pC->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index] = parameters.doubles( "internal_chemical_A" );
        // pC->phenotype.molecular.internalized_total_substrates[chemical_B_substrate_index] = parameters.doubles( "internal_chemical_A" );
        
        // pC = create_cell(second_cell); 
        // pC->assign_position( 0.0, 0.0, 0.0 );
        // pC->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index] = parameters.doubles( "internal_chemical_B" );
        
        // pC = create_cell(third_cell); 
        // pC->assign_position( 50.0, 0.0, 0.0 );
        // pC->phenotype.molecular.internalized_total_substrates[chemical_C_substrate_index] = parameters.doubles( "internal_chemical_C" );
    }
	return; 
}


std::vector<std::string> my_coloring_function( Cell* pCell )
{

	std::vector<std::string> output = false_cell_coloring_cytometry(pCell);
	double internalization_flag = parameters.bools( "internalization_color" );
	
	//bookkeeping
	static int chemical_A_substrate_index = microenvironment.find_density_index( "chemical_A" );
	static int chemical_B_substrate_index = microenvironment.find_density_index( "chemical_B" ); 
    static int chemical_C_substrate_index = microenvironment.find_density_index( "chemical_C");
    std::cout << "----- my_coloring_function: chem A,B,C indices= " << chemical_A_substrate_index <<", "<< chemical_B_substrate_index <<", "<< chemical_C_substrate_index << std::endl;  // = 0,1,2
    
    
    //std::cout<<  "chem A" << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
    //std::cout<<  "chem B" << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
    //std::cout<<  "chem C" << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
    
    
    if (pCell->phenotype.death.dead == false && pCell->type == 1)
    {
        std::cout << "cell 1" << std::endl;
        std::cout<<  "chem A = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
        //std::cout<<  "chem B = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_B_substrate_index]<<std::endl;
        //std::cout<<  "chem C = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_C_substrate_index]<<std::endl;
    }
    
    if (pCell->phenotype.death.dead == false && pCell->type == 2)
    {
        std::cout << "cell 2" << std::endl;
        //std::cout<<  "chem A = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
        std::cout<<  "chem B = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_B_substrate_index]<<std::endl;
        //std::cout<<  "chem C = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_C_substrate_index]<<std::endl;
    }    
    
    
    if (pCell->phenotype.death.dead == false && pCell->type == 3)
    {
        std::cout << "cell 3" << std::endl;
        //std::cout<<  "chem A = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_A_substrate_index]<<std::endl;
        //std::cout<<  "chem B = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_B_substrate_index]<<std::endl;
        std::cout<<  "chem C = " << pCell->phenotype.molecular.internalized_total_substrates[chemical_C_substrate_index]<<std::endl;
        std::cout<<  "chem C sat density = " << pCell->phenotype.secretion.saturation_densities[chemical_C_substrate_index] << std::endl;
    }    
    
    
	if (internalization_flag == false)
    {	
	if( pCell->phenotype.death.dead == false && pCell->type == 0 )
	{
		 output[0] = "red"; 
		 output[2] = "red"; 
	}
	}
	
    //Blue
    double Ry1_1=0.0;
    double Ry2_1=181.0;
    double Gy1_1=17.0;
    double Gy2_1=186.0;
    double By1_1=255.0;
    double By2_1=255.0;
	double x1_1=0.0;
    double x2_1=10.0;
    //double z1_1 = pCell->phenotype.molecular.internalized_total_substrates[chemical1_substrate_index];
    
    //Red
    double Ry1_2=255.0;
    double Ry2_2=255.0;
    double Gy1_2=0.0;
    double Gy2_2=159.0;
    double By1_2=0.0;
    double By2_2=159.0;
	double x1_2=0.0;
    double x2_2=10.0;
    //double z1_2 = pCell->phenotype.molecular.internalized_total_substrates[chemical2_substrate_index];
    
    
	/* if (internalization_flag == true)
    {
	if( pCell->phenotype.death.dead == false && pCell->type == 0 )
	{
        int R_ch1 = (int) 255.0-round((z1_1 - x1_1)/(x2_1 - x1_1)*(Ry2_1 - Ry1_1) - Ry1_1);
        R_ch1 = std::min(255,R_ch1);
        R_ch1 = std::max(0,R_ch1);
        int G_ch1 = (int) 255.0-round((z1_1 - x1_1)/(x2_1 - x1_1)*(Gy2_1 - Gy1_1) - Gy1_1);
        G_ch1 = std::min(255,G_ch1);
        G_ch1 = std::max(0,G_ch1);
        int B_ch1 = (int) 255.0-round((z1_1 - x1_1)/(x2_1 - x1_1)*(By2_1 - By1_1) - By1_1);
        B_ch1 = std::min(255,B_ch1);
        B_ch1 = std::max(0,B_ch1);
		// std::cout<<pCell->phenotype.molecular.internalized_total_substrates[chemical1_substrate_index]<<std::endl;
		char szTempString [128];
		sprintf( szTempString , "rgb(%u,%u,%u)",R_ch1, G_ch1, B_ch1);
		output[0].assign( szTempString );
        int R_ch2 = (int) 255.0-round((z1_2 - x1_2)/(x2_2 - x1_2)*(Ry2_2 - Ry1_2) - Ry1_2);
        R_ch2 = std::min(255,R_ch2);
        R_ch2 = std::max(0,R_ch2);
        int G_ch2 = (int) 255.0-round((z1_2 - x1_2)/(x2_2 - x1_2)*(Gy2_2 - Gy1_2) - Gy1_2);
        G_ch2 = std::min(255,G_ch2);
        G_ch2 = std::max(0,G_ch2);
        int B_ch2 = (int) 255.0-round((z1_2 - x1_2)/(x2_2 - x1_2)*(By2_2 - By1_2) - By1_2);
        B_ch2 = std::min(255,B_ch2);
        B_ch2 = std::max(0,B_ch2);
        //std::cout<<pCell->phenotype.molecular.internalized_total_substrates[chemical2_substrate_index]<<std::endl;
		sprintf( szTempString , "rgb(%u,%u,%u)", R_ch2 , G_ch2 , B_ch2 );
		output[2].assign( szTempString );
        //std::cout << "TEST" << std::endl;
	}
	} */

	return output; 
}
