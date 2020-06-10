import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# find_zFrame
#

class find_zFrame(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "find_zFrame" # TODO make this more human readable by adding spaces
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []
        self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# find_zFrameWidget
#

class find_zFrameWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Segmentation area
        #
        segmentationCollapsibleButton = ctk.ctkCollapsibleButton()
        segmentationCollapsibleButton.text = "Frame segmentation"
        self.layout.addWidget(segmentationCollapsibleButton)

        # Layout within the dummy collapsible button
        segmentationFormLayout = qt.QFormLayout(segmentationCollapsibleButton)

        #
        # input volume selector
        #
        self.inputSelector = slicer.qMRMLNodeComboBox()
        self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.inputSelector.selectNodeUponCreation = True
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.noneEnabled = False
        self.inputSelector.showHidden = False
        self.inputSelector.showChildNodeTypes = False
        self.inputSelector.setMRMLScene( slicer.mrmlScene )
        self.inputSelector.setToolTip( "Pick the input to the algorithm." )
        segmentationFormLayout.addRow("Input Volume: ", self.inputSelector)

        #
        # output volume selector
        #
        self.outSegmentSelector = slicer.qMRMLNodeComboBox()
        self.outSegmentSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.outSegmentSelector.selectNodeUponCreation = True
        self.outSegmentSelector.addEnabled = True
        self.outSegmentSelector.editEnabled = True
        self.outSegmentSelector.removeEnabled = True
        self.outSegmentSelector.noneEnabled = False
        self.outSegmentSelector.showHidden = False
        self.outSegmentSelector.showChildNodeTypes = False
        self.outSegmentSelector.setMRMLScene( slicer.mrmlScene )
        self.outSegmentSelector.setToolTip( "Pick the output to the algorithm." )
        segmentationFormLayout.addRow("Output Segmentation image: ", self.outSegmentSelector)
        
        #
        # output model selector
        #
        self.outSegmtModelSelector = slicer.qMRMLNodeComboBox()
        self.outSegmtModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outSegmtModelSelector.selectNodeUponCreation = True
        self.outSegmtModelSelector.addEnabled = True
        self.outSegmtModelSelector.editEnabled = True
        self.outSegmtModelSelector.removeEnabled = True
        self.outSegmtModelSelector.noneEnabled = False
        self.outSegmtModelSelector.showHidden = False
        self.outSegmtModelSelector.showChildNodeTypes = False
        self.outSegmtModelSelector.setMRMLScene( slicer.mrmlScene )
        self.outSegmtModelSelector.setToolTip( "Output model of the ZFrame" )
        segmentationFormLayout.addRow("Output Segmentation model: ", self.outSegmtModelSelector)


        #
        # Image type radios
        #
        self.imgType='MR'
        self.imgTypeHBox = qt.QHBoxLayout()
        self.MRTypRadio =    qt.QRadioButton("MR")
        self.ctTypRadio =    qt.QRadioButton("CT")
        self.MRTypRadio.setChecked(True)
        self.ctTypRadio.setChecked(False)
        self.imgTypeHBox.addWidget(self.MRTypRadio)
        self.imgTypeHBox.addWidget(self.ctTypRadio)
        segmentationFormLayout.addRow("Image modality: ", self.imgTypeHBox)
        
        self.inputSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onInputSelectorChanged)
        self.onInputSelectorChanged(self.inputSelector.currentNode())
        
        #
        # Apply Button
        #
        self.segmentButton = qt.QPushButton("Segment")
        self.segmentButton.toolTip = "Run the algorithm."
        self.segmentButton.enabled = False
        segmentationFormLayout.addRow(self.segmentButton)

        # connections
        self.segmentButton.connect('clicked(bool)', self.onsegmentButton)
        self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.outSegmentSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.MRTypRadio.connect('toggled(bool)', self.onMRTypeToggle)
        self.ctTypRadio.connect('toggled(bool)', self.onctTypeToggle)

        self.onSelect()

        ###################################################################################################
        
        #
        # Frame Generation area
        #
        frameGenerationCollapsibleButton = ctk.ctkCollapsibleButton()
        frameGenerationCollapsibleButton.text = "Reference Frame"
        self.layout.addWidget(frameGenerationCollapsibleButton)

        frameGenFormLayout = qt.QFormLayout(frameGenerationCollapsibleButton)

        #
        # checkboxes for the presence of fiducials
        #
        self.checkboxesGridLayout = qt.QGridLayout()
        # Anterior
        self.anteriorCheck = qt.QCheckBox('Anterior')
        self.checkboxesGridLayout.addWidget(self.anteriorCheck, 0,1, qt.Qt.AlignCenter)
        # Posterior
        self.posteriorCheck = qt.QCheckBox('Posterior')
        self.checkboxesGridLayout.addWidget(self.posteriorCheck, 2,1, qt.Qt.AlignCenter)
        # Left
        self.leftCheck = qt.QCheckBox('Left')
        self.checkboxesGridLayout.addWidget(self.leftCheck, 1,0, qt.Qt.AlignRight)
        # Right
        self.rightCheck = qt.QCheckBox('Right')
        self.checkboxesGridLayout.addWidget(self.rightCheck, 1,2, qt.Qt.AlignLeft)
        # Superior
        self.superiorCheck = qt.QCheckBox('Superior')
        self.checkboxesGridLayout.addWidget(self.superiorCheck, 1,1, qt.Qt.AlignCenter)
        
        frameGenFormLayout.addRow('fiducials present:', self.checkboxesGridLayout)
        
        self.outIdealModelSelector = slicer.qMRMLNodeComboBox()
        self.outIdealModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outIdealModelSelector.selectNodeUponCreation = True
        self.outIdealModelSelector.addEnabled = True
        self.outIdealModelSelector.removeEnabled = True
        self.outIdealModelSelector.noneEnabled = False
        self.outIdealModelSelector.showHidden = False
        self.outIdealModelSelector.showChildNodeTypes = False
        self.outIdealModelSelector.setMRMLScene( slicer.mrmlScene )
        self.outIdealModelSelector.setToolTip( "Pick the output model." )
        self.outIdealModelSelector.baseName = 'zFrameIdeal'
        frameGenFormLayout.addRow("Output model: ", self.outIdealModelSelector)
        
        self.genModel = qt.QPushButton('Generate Model')
        self.genModel.enabled = False
        frameGenFormLayout.addRow(self.genModel)
        
        self.fiducialsPresent_list = list()
        self.anteriorCheck.connect('stateChanged(int)', self.onAnteriorChanged)
        self.posteriorCheck.connect('stateChanged(int)', self.onPosteriorChanged)
        self.leftCheck.connect('stateChanged(int)', self.onLeftChanged)
        self.rightCheck.connect('stateChanged(int)', self.onRightChanged)
        self.superiorCheck.connect('stateChanged(int)', self.onSuperiorChanged)
        self.genModel.connect('clicked(bool)', self.onGenerateButton)
                
        ###################################################################################################
        
        frameRegistrationCollapsibleButton = ctk.ctkCollapsibleButton()
        frameRegistrationCollapsibleButton.text = 'Register Z Frames'
        self.layout.addWidget(frameRegistrationCollapsibleButton)
        
        frameRegFormLayout = qt.QFormLayout(frameRegistrationCollapsibleButton)
        
        self.movingZselector = slicer.qMRMLNodeComboBox()
        self.movingZselector.nodeTypes = ['vtkMRMLModelNode']
        self.movingZselector.selectNodeUponCreation = True
        self.movingZselector.addEnabled = False
        self.movingZselector.removeEnabled = False
        self.movingZselector.noneEnabled = False
        self.movingZselector.showHidden = False
        self.movingZselector.showChildNodeTypes = False
        self.movingZselector.setMRMLScene( slicer.mrmlScene )
        self.movingZselector.setToolTip( "pick the model of the moving Z" )
        frameRegFormLayout.addRow("Moving: ", self.movingZselector)
        
        self.fixedZselector = slicer.qMRMLNodeComboBox()
        self.fixedZselector.nodeTypes = ['vtkMRMLModelNode']
        self.fixedZselector.selectNodeUponCreation = True
        self.fixedZselector.addEnabled = False
        self.fixedZselector.removeEnabled = False
        self.fixedZselector.noneEnabled = False
        self.fixedZselector.showHidden = False
        self.fixedZselector.showChildNodeTypes = False
        self.fixedZselector.setMRMLScene( slicer.mrmlScene )
        self.fixedZselector.setToolTip( "pick the model of the fixed Z" )
        frameRegFormLayout.addRow("Fixed: ", self.fixedZselector)
        
        self.outputTransformSelector = slicer.qMRMLNodeComboBox()
        self.outputTransformSelector.nodeTypes = ['vtkMRMLTransformNode']
        self.outputTransformSelector.selectNodeUponCreation = True
        self.outputTransformSelector.addEnabled = True
        self.outputTransformSelector.removeEnabled = True
        self.outputTransformSelector.noneEnabled = False
        self.outputTransformSelector.showHidden = False
        self.outputTransformSelector.showChildNodeTypes = False
        self.outputTransformSelector.setMRMLScene( slicer.mrmlScene )
        self.outputTransformSelector.baseName = "zFrame_registration"
        self.outputTransformSelector.setToolTip( "transform that alignes moving to fixed" )
        frameRegFormLayout.addRow("Output transform: ", self.outputTransformSelector)
        
        self.registerPushButton = qt.QPushButton('Register')
        self.registerPushButton.enabled = False
        frameRegFormLayout.addRow(self.registerPushButton)
        
        self.movingZselector.connect("currentNodeChanged(vtkMRMLNode*)", self.onMovingZselectionChanged)
        self.fixedZselector.connect("currentNodeChanged(vtkMRMLNode*)", self.onfixedZselectionChanged)
        
        self.registerPushButton.connect('clicked(bool)', self.onRegisterPushButtonClicked)
        
        
        ###################################################################################################
        
        stereoPointsAdd_collbtn = ctk.ctkCollapsibleButton()
        stereoPointsAdd_collbtn.text = 'enter stereotactic points'
        self.layout.addWidget(stereoPointsAdd_collbtn)
        
        
        self.stereoPointsVBoxLayout = qt.QVBoxLayout(stereoPointsAdd_collbtn)
        self.stereoPointsFormLayout = qt.QFormLayout()
        self.pointTableView = slicer.qMRMLTableView()        
        self.stereoPointsVBoxLayout.addLayout(self.stereoPointsFormLayout)
        self.stereoPointsVBoxLayout.addWidget(self.pointTableView)
        
        
        self.fiducialSelectionCombo = slicer.qMRMLNodeComboBox()
        self.fiducialSelectionCombo.nodeTypes = ['vtkMRMLMarkupsFiducialNode']  
        self.fiducialSelectionCombo.selectNodeUponCreation = True
        self.fiducialSelectionCombo.noneEnabled = False
        self.fiducialSelectionCombo.showHidden = False
        self.fiducialSelectionCombo.showChildNodeTypes = False
        self.fiducialSelectionCombo.setMRMLScene( slicer.mrmlScene )
        self.fiducialSelectionCombo.baseName = 'Stereotactic_points'
        self.fiducialSelectionCombo.setToolTip( "select fiducial node for coordinates conversion" )
        self.stereoPointsFormLayout.addRow('fiducial group', self.fiducialSelectionCombo)
        
        self.NewPointHBox = qt.QHBoxLayout()
        
        self.nameField= qt.QLineEdit()
        self.nameField.setPlaceholderText('Add new point')
        self.NewPointHBox.addWidget(self.nameField)
        
        self.xLabel = qt.QLabel('X')
        self.xLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.xField = qt.QDoubleSpinBox()
        self.xField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.xLabel)
        self.NewPointHBox.addWidget(self.xField)
        
        self.yLabel = qt.QLabel('Y')
        self.yLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.yField = qt.QDoubleSpinBox()
        self.yField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.yLabel)
        self.NewPointHBox.addWidget(self.yField)
        
        self.zLabel = qt.QLabel('Z')
        self.zLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.zField = qt.QDoubleSpinBox()
        self.zField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.zLabel)
        self.NewPointHBox.addWidget(self.zField)
        
        self.addBtn = qt.QPushButton('+')
        self.NewPointHBox.addWidget(self.addBtn)
        
        self.stereoPointsVBoxLayout.addLayout(self.NewPointHBox)
        
        self.fiducialSelectionCombo.connect('currentNodeChanged(vtkMRMLNode*)', self.onFiducialSelectedChanged)
        self.addBtn.connect('clicked(bool)', self.onAddBtnClicked)
        
        
        ###################################################################################################

        # Add vertical spacer
        self.layout.addStretch(1)
        
        #### instantiate the logic
        self.logic = find_zFrameLogic()
    #########################################################################################################

        
    def onInputSelectorChanged(self, newNode):
        if type(newNode)==type(slicer.vtkMRMLScalarVolumeNode()):
            self.outSegmentSelector.baseName = "ZFrame_"+newNode.GetName() + '_img'
            self.outSegmtModelSelector.baseName = "ZFrame_"+newNode.GetName() + '_model'


    def onSelect(self):
        self.segmentButton.enabled = self.inputSelector.currentNode() and self.outSegmentSelector.currentNode()
    
    def onMRTypeToggle(self, checked):
            if checked: self.imgType = 'MR'
            #print("imgType: %s"%self.imgType)
    def onctTypeToggle(self, checked):
            if checked: self.imgType = 'CT'
            #print("imgType: %s"%self.imgType)
    
    def onsegmentButton(self):
        self.logic.run_leksellFiducialsSegmentation(self.inputSelector.currentNode(), self.outSegmentSelector.currentNode(), self.imgType, self.outSegmtModelSelector.currentNode())
        slicer.util.setSliceViewerLayers(background=self.inputSelector.currentNode())

        #self.outSegmtModelSelector.currentNode().SetDisplayVisibility(True)
        self.outSegmtModelSelector.currentNode().GetDisplayNode().SetColor(1,0,0)
    #########################################################################################################
    
    def onAnteriorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['A']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='A']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
    
    def onPosteriorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['P']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='P']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onLeftChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['L']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='L']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onRightChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['R']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='R']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onSuperiorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['S']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='S']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
    
    def onGenerateButton(self):
        self.logic.run_generateIdealLeksellFiducials(self.fiducialsPresent_list, self.outIdealModelSelector.currentNode())

    #########################################################################################################

    def onMovingZselectionChanged(self, newNode):
        if newNode != self.fixedZselector.currentNode() and type(newNode) == type(slicer.vtkMRMLModelNode()):
            self.registerPushButton.enabled = True
        else:
            self.registerPushButton.enabled = False
    
    def onfixedZselectionChanged(self, newNode):
        if newNode != self.movingZselector.currentNode() and type(newNode) == type(slicer.vtkMRMLModelNode()):
            self.registerPushButton.enabled = True
        else:
            self.registerPushButton.enabled = False
        
    def onRegisterPushButtonClicked(self):
        self.logic.run_zFrameRegistration(self.movingZselector.currentNode(),
                                          self.fixedZselector.currentNode(),
                                          self.outputTransformSelector.currentNode())
        slicer.util.loadTransform(os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/leksell2RAS.h5'))
    
    #########################################################################################################
    
    def onFiducialSelectedChanged(self, newNode):
        #print('selection changed !')
        coordTableName = newNode.GetName() + "_coordsConversion"
        #print('looking for '+coordTableName)
        
        if slicer.mrmlScene.GetNodesByName(coordTableName).GetNumberOfItems() == 0:
            #print('create new table')
            coordTable = slicer.vtkMRMLTableNode()
            coordTable.SetName(coordTableName)
            for col in ['Marker', 'X', 'Y', 'Z', 'R', 'A', 'S', 'i', 'j', 'k']:
                c = coordTable.AddColumn()
                c.SetName(col)
            
            slicer.mrmlScene.AddNode(coordTable)
        else:
            #print('found it !')
            coordTable = slicer.mrmlScene.GetNodesByName(coordTableName).GetItemAsObject(0)
        
        #first populate the table with the markers in the fiducialNode
        #self.fiducial2Table(coordTable, newNode)

        
        
        
        self.pointTableView.setMRMLTableNode(coordTable)
        self.pointTableView.setFirstRowLocked(True)
        self.pointTableView.show()
    def onAddBtnClicked(self):
        xyzCoord = [self.xField.value,self.yField.value,self.zField.value]
        
        coordTable = slicer.mrmlScene.GetNodesByName(self.fiducialSelectionCombo.currentNode().GetName() + "_coordsConversion").GetItemAsObject(0)
        
        self.addPointFromXYZ(coordTable, xyzCoord, self.nameField.text)
        
        self.table2Fiducial(coordTable, self.fiducialSelectionCombo.currentNode())
        
        #self.fiducial2Table(coordTable, self.fiducialSelectionCombo.currentNode())        
        
        self.nameField.setText('')
        self.xField.setValue(0.0)
        self.yField.setValue(0.0)
        self.zField.setValue(0.0)


    def addPointFromXYZ(self, tableNode, xyz, label):
        [R,A,S] = self.XYZtoRAS(xyz)
        
        print('in patient space: R,A,S: %s'%str(self.RAStoRASpat(self.XYZtoRAS(xyz))))
              
        [i,j,k] = self.RASpatToIJK(self.RAStoRASpat(self.XYZtoRAS(xyz)))
        r = tableNode.AddEmptyRow()
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Marker'), label)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('X'), '%.02f'%xyz[0])
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Y'), '%.02f'%xyz[1])
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Z'), '%.02f'%xyz[2])        
        tableNode.SetCellText(r, tableNode.GetColumnIndex('R'), '%.02f'%R)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('A'), '%.02f'%A)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('S'), '%.02f'%S)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('i'), '%.02f'%i)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('j'), '%.02f'%j)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('k'), '%.02f'%k)
        


    def fiducial2Table(self, tableNode, fiducialNode):
        for iRow in range(tableNode.GetNumberOfRows()):
            tableNode.RemoveRow(0) #always remove the first
        for iFiducial in range(fiducialNode.GetNumberOfFiducials()):
            thisPosRAS = [0,0,0]
            fiducialNode.GetNthFiducialPosition(iFiducial, thisPosRAS)
            thisLabel = fiducialNode.GetNthFiducialLabel(iFiducial)
            
            r = tableNode.AddEmptyRow()
            tableNode.SetCellText(r, tableNode.GetColumnIndex('Marker'), thisLabel)
            tableNode.SetCellText(r, tableNode.GetColumnIndex('R'), '%.02f'%thisPosRAS[0])
            tableNode.SetCellText(r, tableNode.GetColumnIndex('A'), '%.02f'%thisPosRAS[1])
            tableNode.SetCellText(r, tableNode.GetColumnIndex('S'), '%.02f'%thisPosRAS[2])
    
    def table2Fiducial(self, tableNode, fiducialNode):
        fiducialNode.RemoveAllMarkups()
        
        for iRow in range(tableNode.GetNumberOfRows()):
            fiducialNode.AddPointToNewMarkup(vtk.vtkVector3d([float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('R'))),
                                                              float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('A'))),
                                                              float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('S'))),
                                                              ]),
                                            tableNode.GetCellText(iRow, tableNode.GetColumnIndex('Marker'))
                                            )
        fiducialNode.SetNthMarkupLocked(fiducialNode.GetNumberOfFiducials()-1, True)
    
            
    def XYZtoRAS(self, xyz):
        import numpy as np
        
        if slicer.mrmlScene.GetNodesByName('leksell2RAS').GetNumberOfItems() == 0:
            slicer.util.loadTransform(os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/leksell2RAS.h5'))
        
        leksell2ras = self.transformNode_to_numpy4x4(slicer.mrmlScene.GetNodesByName('leksell2RAS').GetItemAsObject(0))

        return np.dot(leksell2ras, np.array(xyz+[1])).tolist()[:3]
    
    def RAStoRASpat(self, xyz):
        import numpy as np
        print(xyz)
        ras2patLeksell = self.transformNode_to_numpy4x4(self.outputTransformSelector.currentNode())
        
        return np.dot(ras2patLeksell, np.array(xyz+[1])).tolist()[:3]
    
    def RASpatToIJK(self, xyz):
        import numpy as np
        import sitkUtils as siu
        
        vol = siu.PullVolumeFromSlicer(self.inputSelector.currentNode().GetName())
        IJKtoPatRAS = np.zeros([4,4])
        IJKtoPatRAS[:3,:3] = np.array(vol.GetDirection()).reshape([3,3])
        IJKtoPatRAS[:3,3] = np.array(vol.GetOrigin())
        IJKtoPatRAS[3,3]=1
        
        
        #vtkMat = vtk.vtkMatrix4x4()
        #self.inputSelector.currentNode().GetIJKToRASDirectionMatrix(vtkMat)
        #IJKtoPatRAS = np.array([vtkMat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        #print(IJKtoPatRAS)
        
        ##################################################################################################################
        ########## WARNING We add the LPS2RAS matrix in between, this has been determined experimentally with the code:
        
        ########CT_mrml = slicer.mrmlScene.GetNodesByName('CTpreop_(CT)').GetItemAsObject(0)
        ########mat=vtk.vtkMatrix4x4()
        ########CT_mrml.GetIJKToRASDirectionMatrix(mat)
        ########CT_mrml = np.array([mat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        
        ########CT_itk = siu.PullVolumeFromSlicer('CTpreop_(CT)')
        ########CT_ijk2ras = np.zeros([4,4])
        ########CT_ijk2ras[:3,:3] = np.array(CT_itk.GetDirection()).reshape([3,3])
        ########CT_ijk2ras[:3,3] = np.array(CT_itk.GetOrigin())
        ########CT_ijk2ras[3,3]=1
        
        #########divide the twomatrices and round:
        ########np.dot(CT_ijk2ras, np.linalg.inv(CT_mrml))
        ##################################################################################################################
        
        LPS2RAS = np.array([-1,0,0,0, 0,-1,0,0, 0,0,1,0, 0,0,0,1]).reshape([4,4])
        
        #return np.dot(np.linalg.inv(IJKtoPatRAS), np.dot( np.linalg.inv(LPS2RAS), np.array(xyz+[1]))).tolist()[:3]
        return np.dot(np.linalg.inv(IJKtoPatRAS), np.dot(LPS2RAS, np.array(xyz+[1]))).tolist()[:3]

    
    def transformNode_to_numpy4x4(self, node):
        import numpy as np
        from vtk import vtkMatrix4x4
        vtkMat = vtkMatrix4x4()
        node.GetMatrixTransformFromWorld(vtkMat)
        
        return np.array([vtkMat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        
        
        

    def cleanup(self):
        pass


#
# find_zFrameLogic
#

class find_zFrameLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.    The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def hasImageData(self,volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if volumeNode.GetImageData() is None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True

    def isValidInputOutputData(self, inputVolumeNode, outputLabelMapNode):
        """Validates if the output is not the same as input
        """
        if not inputVolumeNode:
            logging.debug('isValidInputOutputData failed: no input volume node defined')
            return False
        if not outputLabelMapNode:
            logging.debug('isValidInputOutputData failed: no output volume node defined')
            return False
        if inputVolumeNode.GetID()==outputLabelMapNode.GetID():
            logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
            return False
        return True

    def run_leksellFiducialsSegmentation(self, inputVolume, outputVolume, imgType, outputModel):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
            return False

        logging.info('Fiducial segmentation started')

        # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
        from segmentZframe import segment_zFrame_slicer
        segment_zFrame_slicer(inputVolume, outputVolume, imgType)
        
        # create a segmentation to show the frame in 3d
        zFrameSegmentationNode = slicer.vtkMRMLSegmentationNode()
        zFrameSegmentationNode.SetName("zFrame_seg")
        slicer.mrmlScene.AddNode(zFrameSegmentationNode)
        zFrameSegmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(outputVolume)
        zFrameSegmentationNode.GetSegmentation().AddEmptySegment('zFrame')
        
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(zFrameSegmentationNode)
        segmentEditorWidget.setMasterVolumeNode(outputVolume)

        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        maxVal = slicer.util.arrayFromVolume(outputVolume).max()
        effect.setParameter("MinimumThreshold",str(1.1))
        effect.setParameter("MaximumThreshold",str(maxVal))
        zFrameSegmentationNode.CreateClosedSurfaceRepresentation()
        effect.self().onApply()
        outputModel.SetAndObservePolyData(zFrameSegmentationNode.GetClosedSurfaceRepresentation(zFrameSegmentationNode.GetSegmentation().GetNthSegmentID(0)))
        outputModel.CreateDefaultDisplayNodes()
        zFrameSegmentationNode.SetDisplayVisibility(False)
        
        logging.info('Fiducial segmentation finished')

        return True
        
    def run_generateIdealLeksellFiducials(self, fiducialList, outputModelNode):
        
        logging.info('Ideal frame generation started')
        
        import vtk, os
        fileNames = [os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/ZFrame_'+i+'.stl') for i in fiducialList]
        readers = [vtk.vtkSTLReader() for i in fileNames]
        appender = vtk.vtkAppendPolyData()
        for (thisReader,thisFile) in zip(readers, fileNames):
            thisReader.SetFileName(thisFile)
            appender.AddInputConnection(thisReader.GetOutputPort())
        appender.Update()
        #writer = vtk.vtkXMLPolyDataWriter()
        #writer.SetFileName(os.path.join(os.path.split(__file__)[0], 'test.vtp'))
        #writer.SetInputConnection(appender.GetOutputPort())
        #writer.Update()
        outputModelNode.SetPolyDataConnection(appender.GetOutputPort())
        outputModelNode.CreateDefaultDisplayNodes()
        outputModelNode.SetDisplayVisibility(True)
        outputModelNode.GetDisplayNode().SetColor(0,1,0)
        
        logging.info('Ideal frame generation done')
        
        return True

    ## Iterative Closest Point surface to suface registration, based on https://github.com/DCBIA-OrthoLab/CMFreg/blob/b5898deaf8e2017cefcaf03d61aba78e625fc924/SurfaceRegistration/SurfaceRegistration.py#L707
    def run_zFrameRegistration(self, movingZ, referenceZ, outputTransform):
        """Run the actual algorithm"""
        
        logging.info('ICP registration started')
        
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(movingZ.GetPolyData())
        icp.SetTarget(referenceZ.GetPolyData())
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfIterations(1000)
        icp.SetMaximumMeanDistance(0.001)
        #icp.SetMaximumNumberOfLandmarks(numberOfLandmarks)
        #icp.SetCheckMeanDistance(int(checkMeanDistance))
        icp.SetStartByMatchingCentroids(True)
        icp.Update()
        outputMatrix = vtk.vtkMatrix4x4()
        icp.GetMatrix(outputMatrix)
        outputTransform.SetAndObserveMatrixTransformToParent(outputMatrix)
        
        logging.info('ICP registration done')

        return True

class find_zFrameTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_find_zFrame1()

    def test_find_zFrame1(self):
        """ Ideally you should have several levels of tests.    At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).    At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.    For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import SampleData
        SampleData.downloadFromURL(
            nodeNames='FA',
            fileNames='FA.nrrd',
            uris='http://slicer.kitware.com/midas3/download?items=5767')
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = find_zFrameLogic()
        self.assertIsNotNone( logic.hasImageData(volumeNode) )
        self.delayDisplay('Test passed!')
