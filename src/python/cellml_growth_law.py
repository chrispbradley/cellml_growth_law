#!/usr/bin/env python

#> \file
#> \author Chris Bradley
#> \brief This is an example script to solve a finite elasticity problem with a growth and constituative law in CellML
#>
#> \section LICENSE
#>
#> Version: MPL 1.1/GPL 2.0/LGPL 2.1
#>
#> The contents of this file are subject to the Mozilla Public License
#> Version 1.1 (the "License"); you may not use this file except in
#> compliance with the License. You may obtain a copy of the License at
#> http://www.mozilla.org/MPL/
#>
#> Software distributed under the License is distributed on an "AS IS"
#> basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
#> License for the specific language governing rights and limitations
#> under the License.
#>
#> The Original Code is OpenCMISS
#>
#> The Initial Developer of the Original Code is University of Auckland,
#> Auckland, New Zealand and University of Oxford, Oxford, United
#> Kingdom. Portions created by the University of Auckland and University
#> of Oxford are Copyright (C) 2007 by the University of Auckland and
#> the University of Oxford. All Rights Reserved.
#>
#> Contributor(s): 
#>
#> Alternatively, the contents of this file may be used under the terms of
#> either the GNU General Public License Version 2 or later (the "GPL"), or
#> the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
#> in which case the provisions of the GPL or the LGPL are applicable instead
#> of those above. if you wish to allow use of your version of this file only
#> under the terms of either the GPL or the LGPL, and not to allow others to
#> use your version of this file under the terms of the MPL, indicate your
#> decision by deleting the provisions above and replace them with the notice
#> and other provisions required by the GPL or the LGPL. if you do not delete
#> the provisions above, a recipient may use your version of this file under
#> the terms of any one of the MPL, the GPL or the LGPL.
#>

#> Main script
# Add Python bindings directory to PATH
import sys, os

# Intialise OpenCMISS
from opencmiss.opencmiss import OpenCMISS_Python as oc

# Set problem parameters
height = 1.0
width = 1.0
length = 1.0

fibreRate = 0.01
sheetRate = 0.02
normalRate = 0.03

extension = 0.1

numberOfGaussXi = 2

startTime = 0.0
stopTime = 1.0
timeIncrement = 1.0

contextUserNumber = 1
coordinateSystemUserNumber = 1
regionUserNumber = 1
basisUserNumber = 1
generatedMeshUserNumber = 1
meshUserNumber = 1
decompositionUserNumber = 1
decomposerUserNumber = 1
geometricFieldUserNumber = 1
fibreFieldUserNumber = 2
dependentFieldUserNumber = 3
equationsSetUserNumber = 1
equationsSetFieldUserNumber = 5
growthCellMLUserNumber = 1
growthCellMLModelsFieldUserNumber = 6
growthCellMLStateFieldUserNumber = 7
growthCellMLParametersFieldUserNumber = 8
constituativeCellMLUserNumber = 2
constituativeCellMLModelsFieldUserNumber = 9
constituativeCellMLParametersFieldUserNumber = 10
constituativeCellMLIntermediateFieldUserNumber = 11
problemUserNumber = 1

InterpolationType = 1

context = oc.Context()
context.Create(contextUserNumber)

worldRegion = oc.Region()
context.WorldRegionGet(worldRegion)

oc.DiagnosticsSetOn(oc.DiagnosticTypes.FROM,[1,2,3,4,5],"Diagnostics",["FiniteElasticity_FiniteElementResidualEvaluate"])

# Get the number of computational nodes and this computational node number
computationEnvironment = oc.ComputationEnvironment()
context.ComputationEnvironmentGet(computationEnvironment)

worldWorkGroup = oc.WorkGroup()
computationEnvironment.WorldWorkGroupGet(worldWorkGroup)
numberOfComputationalNodes = worldWorkGroup.NumberOfGroupNodesGet()
computationalNodeNumber = worldWorkGroup.GroupNodeNumberGet()

# Create a 3D rectangular cartesian coordinate system
coordinateSystem = oc.CoordinateSystem()
coordinateSystem.CreateStart(coordinateSystemUserNumber,context)
coordinateSystem.DimensionSet(3)
coordinateSystem.CreateFinish()

# Create a region and assign the coordinate system to the region
region = oc.Region()
region.CreateStart(regionUserNumber,worldRegion)
region.LabelSet("Region")
region.coordinateSystem = coordinateSystem
region.CreateFinish()

# Define basis
basis = oc.Basis()
basis.CreateStart(basisUserNumber,context)
if InterpolationType in (1,2,3,4):
    basis.type = oc.BasisTypes.LAGRANGE_HERMITE_TP
basis.numberOfXi = 3
basis.interpolationXi = [oc.BasisInterpolationSpecifications.LINEAR_LAGRANGE]*3
if(numberOfGaussXi>0):
    basis.quadratureNumberOfGaussXi = [numberOfGaussXi]*3
basis.CreateFinish()

# Start the creation of a manually generated mesh in the region
mesh = oc.Mesh()
mesh.CreateStart(meshUserNumber,region,3)
mesh.NumberOfComponentsSet(1)
mesh.NumberOfElementsSet(1)

#Define nodes for the mesh
nodes = oc.Nodes()
nodes.CreateStart(region,8)
nodes.CreateFinish()

elements = oc.MeshElements()
elements.CreateStart(mesh,1,basis)
elements.NodesSet(1,[1,2,3,4,5,6,7,8])
elements.CreateFinish()

mesh.CreateFinish() 

# Create a decomposition for the mesh
decomposition = oc.Decomposition()
decomposition.CreateStart(decompositionUserNumber,mesh)
decomposition.CreateFinish()

# Decompose 
decomposer = oc.Decomposer()
decomposer.CreateStart(decomposerUserNumber,worldRegion,worldWorkGroup)
decompositionIndex = decomposer.DecompositionAdd(decomposition)
decomposer.CreateFinish()

# Create a field for the geometry
geometricField = oc.Field()
geometricField.CreateStart(geometricFieldUserNumber,region)
geometricField.DecompositionSet(decomposition)
geometricField.TypeSet(oc.FieldTypes.GEOMETRIC)
geometricField.VariableLabelSet(oc.FieldVariableTypes.U,"Geometry")
geometricField.ComponentMeshComponentSet(oc.FieldVariableTypes.U,1,1)
geometricField.ComponentMeshComponentSet(oc.FieldVariableTypes.U,2,1)
geometricField.ComponentMeshComponentSet(oc.FieldVariableTypes.U,3,1)
if InterpolationType == 4:
    geometricField.fieldScalingType = oc.FieldScalingTypes.ARITHMETIC_MEAN
geometricField.CreateFinish()

# Update the geometric field parameters manually
# node 1
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,1,1,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,1,2,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,1,3,0.0)
# node 2
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,2,1,height)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,2,2,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,2,3,0.0)
# node 3
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,3,1,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,3,2,width)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,3,3,0.0)
# node 4
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,4,1,height)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,4,2,width)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,4,3,0.0)
# node 5
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,5,1,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,5,2,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,5,3,length)
# node 6
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,6,1,height)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,6,2,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,6,3,length)
# node 7
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,7,1,0.0)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,7,2,width)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,7,3,length)
# node 8
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,8,1,height)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,8,2,width)
geometricField.ParameterSetUpdateNodeDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,1,8,3,length)

# Update the geometric field
geometricField.ParameterSetUpdateStart(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES)
geometricField.ParameterSetUpdateFinish(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES)

# Create a fibre field and attach it to the geometric field
fibreField = oc.Field()
fibreField.CreateStart(fibreFieldUserNumber,region)
fibreField.TypeSet(oc.FieldTypes.FIBRE)
fibreField.DecompositionSet(decomposition)
fibreField.GeometricFieldSet(geometricField)
fibreField.VariableLabelSet(oc.FieldVariableTypes.U,"Fibre")
if InterpolationType == 4:
    fibreField.fieldScalingType = oc.FieldScalingTypes.ARITHMETIC_MEAN
fibreField.CreateFinish()

# Create the dependent field
dependentField = oc.Field()
dependentField.CreateStart(dependentFieldUserNumber,region)
dependentField.TypeSet(oc.FieldTypes.GEOMETRIC_GENERAL)  
dependentField.DecompositionSet(decomposition)
dependentField.GeometricFieldSet(geometricField) 
dependentField.DependentTypeSet(oc.FieldDependentTypes.DEPENDENT) 
dependentField.NumberOfVariablesSet(5)
dependentField.VariableTypesSet([oc.FieldVariableTypes.U,oc.FieldVariableTypes.T,oc.FieldVariableTypes.U1,oc.FieldVariableTypes.U2,oc.FieldVariableTypes.U3])
dependentField.VariableLabelSet(oc.FieldVariableTypes.U,"Dependent")
dependentField.VariableLabelSet(oc.FieldVariableTypes.T,"Traction")
dependentField.VariableLabelSet(oc.FieldVariableTypes.U1,"Strain")
dependentField.VariableLabelSet(oc.FieldVariableTypes.U2,"Stress")
dependentField.VariableLabelSet(oc.FieldVariableTypes.U3,"Growth")
dependentField.NumberOfComponentsSet(oc.FieldVariableTypes.U,4)
dependentField.NumberOfComponentsSet(oc.FieldVariableTypes.T,4)
dependentField.NumberOfComponentsSet(oc.FieldVariableTypes.U1,6)
dependentField.NumberOfComponentsSet(oc.FieldVariableTypes.U2,6)
dependentField.NumberOfComponentsSet(oc.FieldVariableTypes.U3,3)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U,4,oc.FieldInterpolationTypes.ELEMENT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.T,4,oc.FieldInterpolationTypes.ELEMENT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,1,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,2,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,3,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,4,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,5,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U1,6,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,1,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,2,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,3,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,4,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,5,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U2,6,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U3,1,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U3,2,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
dependentField.ComponentInterpolationSet(oc.FieldVariableTypes.U3,3,oc.FieldInterpolationTypes.GAUSS_POINT_BASED)
if InterpolationType == 4:
    dependentField.fieldScalingType = oc.FieldScalingTypes.ARITHMETIC_MEAN
dependentField.CreateFinish()

# Initialise dependent field from undeformed geometry
oc.Field.ParametersToFieldParametersComponentCopy(
    geometricField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,
    dependentField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1)
oc.Field.ParametersToFieldParametersComponentCopy(
    geometricField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,2,
    dependentField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,2)
oc.Field.ParametersToFieldParametersComponentCopy(
    geometricField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,3,
    dependentField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,3)
# Initialise the hydrostatic pressure
oc.Field.ComponentValuesInitialiseDP(
    dependentField,oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,4,-8.0)

# Create the equations_set
equationsSetField = oc.Field()
equationsSet = oc.EquationsSet()
equationsSetSpecification = [oc.EquationsSetClasses.ELASTICITY,
    oc.EquationsSetTypes.FINITE_ELASTICITY,
    oc.EquationsSetSubtypes.CONSTIT_AND_GROWTH_LAW_IN_CELLML]
equationsSet.CreateStart(equationsSetUserNumber,region,fibreField,
    equationsSetSpecification,equationsSetFieldUserNumber, equationsSetField)
equationsSet.CreateFinish()

equationsSet.DependentCreateStart(dependentFieldUserNumber,dependentField)
equationsSet.DependentCreateFinish()

# Create the CellML environment for the growth law
growthCellML = oc.CellML()
growthCellML.CreateStart(growthCellMLUserNumber,region)
growthCellMLIdx = growthCellML.ModelImport("simplegrowth.cellml")
growthCellML.VariableSetAsKnown(growthCellMLIdx,"Main/fibrerate")
growthCellML.VariableSetAsKnown(growthCellMLIdx,"Main/sheetrate")
growthCellML.VariableSetAsKnown(growthCellMLIdx,"Main/normalrate")
growthCellML.CreateFinish()

# Create CellML <--> OpenCMISS field maps
growthCellML.FieldMapsCreateStart()
growthCellML.CreateCellMLToFieldMap(growthCellMLIdx,"Main/lambda1",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U3,1,oc.FieldParameterSetTypes.VALUES)
growthCellML.CreateCellMLToFieldMap(growthCellMLIdx,"Main/lambda2",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U3,2,oc.FieldParameterSetTypes.VALUES)
growthCellML.CreateCellMLToFieldMap(growthCellMLIdx,"Main/lambda3",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U3,3,oc.FieldParameterSetTypes.VALUES)
growthCellML.FieldMapsCreateFinish()

# Create the CELL models field
growthCellMLModelsField = oc.Field()
growthCellML.ModelsFieldCreateStart(growthCellMLModelsFieldUserNumber,growthCellMLModelsField)
growthCellMLModelsField.VariableLabelSet(oc.FieldVariableTypes.U,"GrowthModelMap")
growthCellML.ModelsFieldCreateFinish()

# Create the CELL parameters field
growthCellMLParametersField = oc.Field()
growthCellML.ParametersFieldCreateStart(growthCellMLParametersFieldUserNumber,growthCellMLParametersField)
growthCellMLParametersField.VariableLabelSet(oc.FieldVariableTypes.U,"GrowthParameters")
growthCellML.ParametersFieldCreateFinish()
#
growthCellMLParametersField.ComponentValuesInitialiseDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,1,fibreRate)
growthCellMLParametersField.ComponentValuesInitialiseDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,2,sheetRate)
growthCellMLParametersField.ComponentValuesInitialiseDP(oc.FieldVariableTypes.U,oc.FieldParameterSetTypes.VALUES,3,normalRate)

# Create the CELL state field
growthCellMLStateField = oc.Field()
growthCellML.StateFieldCreateStart(growthCellMLStateFieldUserNumber,growthCellMLStateField)
growthCellMLStateField.VariableLabelSet(oc.FieldVariableTypes.U,"GrowthState")
growthCellML.StateFieldCreateFinish()

# Create the CellML environment for the consitutative law
constituativeCellML = oc.CellML()
constituativeCellML.CreateStart(constituativeCellMLUserNumber,region)
constituativeCellMLIdx = constituativeCellML.ModelImport("mooneyrivlin.cellml")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E11")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E12")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E13")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E22")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E23")
constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/E33")
#constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/c1")
#constituativeCellML.VariableSetAsKnown(constituativeCellMLIdx,"equations/c2")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev11")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev12")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev13")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev22")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev23")
constituativeCellML.VariableSetAsWanted(constituativeCellMLIdx,"equations/Tdev33")
constituativeCellML.CreateFinish()

# Create CellML <--> OpenCMISS field maps
constituativeCellML.FieldMapsCreateStart()
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,1,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E11",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,2,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E12",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,3,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E13",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,4,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E22",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,5,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E23",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateFieldToCellMLMap(dependentField,oc.FieldVariableTypes.U1,6,oc.FieldParameterSetTypes.VALUES,
    constituativeCellMLIdx,"equations/E33",oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev11",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,1,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev12",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,2,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev13",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,3,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev22",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,4,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev23",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,5,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.CreateCellMLToFieldMap(constituativeCellMLIdx,"equations/Tdev33",oc.FieldParameterSetTypes.VALUES,
    dependentField,oc.FieldVariableTypes.U2,6,oc.FieldParameterSetTypes.VALUES)
constituativeCellML.FieldMapsCreateFinish()

# Create the CELL models field
constituativeCellMLModelsField = oc.Field()
constituativeCellML.ModelsFieldCreateStart(constituativeCellMLModelsFieldUserNumber,constituativeCellMLModelsField)
constituativeCellMLModelsField.VariableLabelSet(oc.FieldVariableTypes.U,"ConstituativeModelMap")
constituativeCellML.ModelsFieldCreateFinish()

# Create the CELL parameters field
constituativeCellMLParametersField = oc.Field()
constituativeCellML.ParametersFieldCreateStart(constituativeCellMLParametersFieldUserNumber,constituativeCellMLParametersField)
constituativeCellMLParametersField.VariableLabelSet(oc.FieldVariableTypes.U,"ConstituativeParameters")
constituativeCellML.ParametersFieldCreateFinish()

# Create the CELL intermediate field
constituativeCellMLIntermediateField = oc.Field()
constituativeCellML.IntermediateFieldCreateStart(constituativeCellMLIntermediateFieldUserNumber,constituativeCellMLIntermediateField)
constituativeCellMLIntermediateField.VariableLabelSet(oc.FieldVariableTypes.U,"ConstituativeIntermediate")
constituativeCellML.IntermediateFieldCreateFinish()

# Create equations
equations = oc.Equations()
equationsSet.EquationsCreateStart(equations)
equations.sparsityType = oc.EquationsSparsityTypes.SPARSE
equations.outputType = oc.EquationsOutputTypes.NONE
equationsSet.EquationsCreateFinish()

# Define the problem
problem = oc.Problem()
problemSpecification = [oc.ProblemClasses.ELASTICITY,
        oc.ProblemTypes.FINITE_ELASTICITY,
        oc.ProblemSubtypes.FINITE_ELASTICITY_WITH_GROWTH_CELLML]
problem.CreateStart(problemUserNumber,context,problemSpecification)
problem.CreateFinish()

# Create control loops
timeLoop = oc.ControlLoop()
problem.ControlLoopCreateStart()
problem.ControlLoopGet([oc.ControlLoopIdentifiers.NODE],timeLoop)
timeLoop.TimesSet(startTime,stopTime,timeIncrement)
problem.ControlLoopCreateFinish()

# Create problem solvers
odeIntegrationSolver = oc.Solver()
nonlinearSolver = oc.Solver()
linearSolver = oc.Solver()
cellMLEvaluationSolver = oc.Solver()
problem.SolversCreateStart()
problem.SolverGet([oc.ControlLoopIdentifiers.NODE],1,odeIntegrationSolver)
problem.SolverGet([oc.ControlLoopIdentifiers.NODE],2,nonlinearSolver)
nonlinearSolver.outputType = oc.SolverOutputTypes.MONITOR
nonlinearSolver.NewtonJacobianCalculationTypeSet(oc.JacobianCalculationTypes.FD)
nonlinearSolver.NewtonAbsoluteToleranceSet(1e-14)
nonlinearSolver.NewtonSolutionToleranceSet(1e-14)
nonlinearSolver.NewtonRelativeToleranceSet(1e-14)
nonlinearSolver.NewtonCellMLSolverGet(cellMLEvaluationSolver)
nonlinearSolver.NewtonLinearSolverGet(linearSolver)
linearSolver.linearType = oc.LinearSolverTypes.DIRECT
problem.SolversCreateFinish()

# Create nonlinear equations and add equations set to solver equations
nonlinearEquations = oc.SolverEquations()
problem.SolverEquationsCreateStart()
nonlinearSolver.SolverEquationsGet(nonlinearEquations)
nonlinearEquations.sparsityType = oc.SolverEquationsSparsityTypes.SPARSE
nonlinearEquationsSetIndex = nonlinearEquations.EquationsSetAdd(equationsSet)
problem.SolverEquationsCreateFinish()

# Create CellML equations and add growth and constituative equations to the solvers
growthEquations = oc.CellMLEquations()
constituativeEquations = oc.CellMLEquations()
problem.CellMLEquationsCreateStart()
odeIntegrationSolver.CellMLEquationsGet(growthEquations)
growthEquationsIndex = growthEquations.CellMLAdd(growthCellML)
cellMLEvaluationSolver.CellMLEquationsGet(constituativeEquations)
constituativeEquationsIndex = constituativeEquations.CellMLAdd(constituativeCellML)
problem.CellMLEquationsCreateFinish()

# Prescribe boundary conditions (absolute nodal parameters)
boundaryConditions = oc.BoundaryConditions()
nonlinearEquations.BoundaryConditionsCreateStart(boundaryConditions)

#Set x=0 nodes to no x displacment in x. Set x=width nodes to 10% x displacement
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,1,1,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,3,1,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,5,1,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,7,1,oc.BoundaryConditionsTypes.FIXED,0.0)

boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,2,1,oc.BoundaryConditionsTypes.FIXED,extension*width)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,4,1,oc.BoundaryConditionsTypes.FIXED,extension*width)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,6,1,oc.BoundaryConditionsTypes.FIXED,extension*width)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,8,1,oc.BoundaryConditionsTypes.FIXED,extension*width)

# Set y=0 nodes to no y displacement
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,1,2,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,2,2,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,5,2,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,6,2,oc.BoundaryConditionsTypes.FIXED,0.0)

# Set z=0 nodes to no y displacement
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,1,3,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,2,3,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,3,3,oc.BoundaryConditionsTypes.FIXED,0.0)
boundaryConditions.AddNode(dependentField,oc.FieldVariableTypes.U,1,1,4,3,oc.BoundaryConditionsTypes.FIXED,0.0)

nonlinearEquations.BoundaryConditionsCreateFinish()

# Solve the problem
problem.Solve()

if not os.path.exists("./results"):
    os.makedirs("./results")

# Export results
fields = oc.Fields()
fields.CreateRegion(region)
fields.NodesExport("./results/CellMLGrowth","FORTRAN")
fields.ElementsExport("./results/CellMLGrowth","FORTRAN")
fields.Finalise()

