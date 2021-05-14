Release Log
===========

3.7.11
------

**Enhancements**
	* mgear_dist: New drag and drop installer [mgear_dist#62]
	* Shifter: Extending the CustomShifterStep base class functionality. [shifter#109]
	* mGear_core: Added meshNavigation.edgeLoopBetweenVertices [mgear_core#77]
	* mGear_core: Added create raycast node function in applyop.py [mgear_core#90]

**Bug Fix**
	* Shifter: Error when joint name start with number [shifter#111]
	* mGear_core: Bad IKRot rol reference anim_utils.py [shifter#82]
	* mGear_core: Remove compile PyQt ui menu command for Maya 2022 compatibility [shifter#81]
	* mGear_core: Knots saved in json file and read if they exist [shifter#76]
	* Rigbits: Fix missing import in menu.py [rigbits#68]
	* Rigbits: rbf manager, import error catch and cleanup [rigbits#73]
	* Rigbits: Fix eyebrow joint orientation [rigbits#72]
	* Shifter_EPIC_components: Improve joint placement precision on arm, leg and spine. [shifter_epic_components#20]
	* Shifter_EPIC_components: Fixed relation dict value of "knee" in EPIC_leg_01 which causes building failure in certain cases. [shifter_epic_components#19]


3.7.8
-----
**New Features**
	* CFXbits: Xgen IGS boost: New tool to create curve based grooming with xgen interactive grooming splines [cfxbits#1]
	* mGear solvers: New matrixConstraint node [mgear_solvers#5]
	* mGear_core: Add support for drag n drop of mGear filetypes, .sgt [mgear_core#79]
	* mGear_core: Deformer weight IO module [mgear_core#75]
	* mgear_dist: Drag and Drop easy installer  [mgear_dist#56]
	* Shifter: Configurable naming template. [shifter#83]
	* Shifter: Joint orientation options. [shifter#73]
	* Shifter: Plebes (a tool for rigging character generator characters with mGear). [shifter#96]
	* Shifter_EPIC_components: New set of componets specially design for Unreal engine and Games in general.

**Enhancements**
	* mGear_core: General update to add CFXbits required functions [mgear_core#63]
	* mGear_core: Skinning mismatch vertex warning should include the name of the object [mgear_core#63]
	* Shifter: Add support for #_blade in chain coponents. [shifter#107]
	* Shifter: Attributes naming using component short name(instance Name) not component type name. [shifter#95]
	* Shifter: IO return shifter rig object for NXT tools integration. [shifter#94]
	* simpleRig: Improve automatic hierarchy creation [simpleRig#8]

**Bug Fix**
	* Anim Picker: Create picker improvements [anim_picker#21]
	* Anim Picker: Duplicate behavior creates instances [anim_picker#24]
	* Anim Picker: Duplicating pickers, spacing issue [anim_picker#22]
	* Anim Picker: Fail gracefully when space switch controls are not found [anim_picker#33]
	* Anim Picker: save overlay offset when change windows size [anim_picker#19]
	* Anim Picker: UI buttons hidden in OSX [anim_picker#34]
	* Animbits: Channel Master: Channel Master: Sync with Graph editor. [animbits#54]
	* Animbits: Channel Master: sync selected channels in graph editor. [animbits#55]
	* mGear solvers: added in the clamp values for the squash and stretch node [mgear_solvers#6]
	* mGear_core: anim_utils: improve IK FK match pole vector calculation [mgear_core#65]
	* mGear_core: Attribute module new functions: Make it work with control custom names [mgear_core#62]
	* mGear_core: Mirro/flip pose not working with custom names [mgear_core#71]
	* mGear_core: Mirror/flip pose fail [mgear_core#70]
	* mGear_core: QApplication instance dont have widgetAt method on Maya 2020 [mgear_core#66]
	* mGear_core: shifter_classic_components repeatedly added to sys.path  [mgear_core#69]
	* mGear_core: Stripe pipes from skinCluster names [mgear_core#64]
	* mgear_dist: Incorrect grammar in UI [mgear_dist#26]
	* mgear_dist: update menus to str command [mgear_dist#53]
	* Rigbits: Add attr ctrl tweaks  [rigbits#60]
	* Rigbits: Add control and tweaks module controls need to create "isCtrl" control tag  [rigbits#50]
	* Rigbits: Facial rigger is compatible with Shifter's game tools [rigbits#37]
	* Rigbits: Mirror controls required target shape to exist  [rigbits#56]
	* Rigbits: RBF manager mirror with custom names  [rigbits#63]
	* Shifter: Game tools fix connection issue with new matrix constraint node. [shifter#108]
	* Shifter: Game tools is not disconnecting all the connections between rig and model. [shifter#68]
	* Shifter: Guide component scale inconsistency at creation time. [shifter#97]
	* Shifter: replaces backslashes with forward slashes for Mac OS. [shifter#101]
	* Shifter: Set by default Force uniform scaling to ON. [shifter#79]
	* Shifter_classic_components: Change on Shifter leg_2jnt_tangent component settings UI [shifter_classic_components#81]
	* Shifter_classic_components: Control_01 component space switching with mgear viewport menu [shifter_classic_components#82]
	* Shifter_classic_components: Fix for issue "Menu: Ctrl+Shift results in broken shelf items" [shifter_classic_components#87]

**WARNING**
	* mgear_dist: dropping support for Maya 2017 and older [mgear_dist#60]



3.6.0
-----
**New Features**
	* Shifter_classic_components: chain_spring_lite_stack_master_01: New component [shifter_classic_components#79]

**Enhancements**
	* Anim Picker: Add create picker menu items based on selection [anim_picker#18]
	* Anim Picker: Make select controls display more noticeable [anim_picker#16]
	* Animbits: Channel Master: Add channels from any section in ChannelBox. [animbits#50]
	* Animbits: Channel Master: Auto color options. [animbits#51]
	* Animbits: Channel Master: option to configure channel order. [animbits#37]
	* Animbits: Channel Master: Turn off real time update on scrubbing. [animbits#51]
	* Animbits: Channel Master: Use selected channels for copy/paste keyframes. [animbits#52]
	* Animbits: softTweak: add surface fallof option [animbits#53]
	* mGear_core: attribute module new functions: get_selected_channels_full_path + collect_attrs [mgear_core#56]
	* Shifter: Add Joint Names parameter for customizing joint names in guide settings. [shifter#85]
	* Shifter_classic_components: lite_chain_stack_02 component: add blend option to turn off the connection [shifter_classic_components#78]

**Bug Fix**
	* Animbits: Channel Master: Blendshape node channels bug. [animbits#49]
	* Shifter: Importing old guides with missing parameters error. [shifter#69]

3.5.1
-----
**Bug Fix**
	* mGear_core: When copy skin, match the skinningMethod as well [mgear_core#55]
	* Rigbits: RBF Manager mirror bug with Flex Add_attribute [rigbits#54]

3.5.0
-----
**New Features**
	* Animbits: Channel Master [animbits#14]
	* Shifter: Auto Fit Guide (Beta preview). [shifter#82]

**Enhancements**
	* Anim Picker: Make select controls display more noticeable [anim_picker#16]

**Bug Fix**
	* Anim Picker: CentOS and windows Maya 2019/2020 TypeErrorr [anim_picker#15]
	* mGear_core: dagmenu error when parent switch with keys on and rig with namespace [mgear_core#53]
	* mGear_core: Fix loop crash when quering tag childrens [mgear_core#52]
	* mGear_core: Fixed path handling in exportSkinPack if it is called with arguments. [mgear_core#37]
	* mGear_core: getRootNode doesn't find the root correctly [mgear_core#51]
	* mGear_core: Mirror function causes tag attributes to mirror their content [mgear_core#47]
	* mGear_core: Parent switch dag menu not working when root node is parented under a non referenced heararchy. [mgear_core#48]

3.4.0
-----
**New Features**
	* Anim Picker: New Animation Picker [anim_picker#2]
	* mGear_core: mGear viewport menu [mgear_core#38]
	* Rigbits: SDK Manager [rigbits#42]
	* Shifter_classic_components: SDK manager special component [shifter_classic_components#75]

3.3.1
-----
**Bug Fix**
	* Rigbits: Facial rigger tools QT aligment argument [rigbits#44]

3.3.0
-----
**New Features**
	* Shifter_classic_components: Cable component [shifter_classic_components#73]
	* Shifter_classic_components: UI_slider and UI_container component [shifter_classic_components#66]
	* Rigbits: New eyebrow Rigger [rigbits#40]

**Enhancements**
	* Shifter_classic_components: Control_01: Expose more space switch options [shifter_classic_components#7]

3.2.1
-----
**Enhancements**
	* Shifter_classic_components:  arm_2jnt_04: wrist align and plane normal [shifter_classic_components#58] [shifter_classic_components#59]
	* Shifter_classic_components:  S_Spine change the relative connections  [shifter_classic_components#67]
	* mGear_core: Added 2D guide root for Shifter components [mgear_core#36]
	* Shifter: Build log window clears instead of reopening. [shifter#74]

**Bug Fix**
	* Shifter: Fixed a guide renaming issue. [shifter#71]
	* Shifter: Renamed Connexion to Connection in some places.. [shifter#75]
	* Shifter: Renaming components will fail if the names are not unique. [shifter#70]
	* Shifter_classic_components: foot_bk_01 component roll_ctrl issue [shifter_classic_components#68]
	* Shifter_classic_components: Visual axis reference for control_01 and arm_2jnt_04 is not scaling correctly  [shifter_classic_components#57]
	* Shifter_classic_components: Fixes building of chain_01 when set to IK only  [shifter_classic_components#65]
	* Shifter_classic_components:  spine_S_shape rename bug  [shifter_classic_components#50]
	* mGear_core: dag.findComponentChildren2 fails after a rig was built. [mgear_core#32] [mgear_core#35]
	* mGear_core: QDragListView ignores drop event on self  [mgear_core#34][mgear_core#33]

3.2.0
-----
**New Features**
	* Animbits: Animation GPU cache manager [animbits#11]
	* Rigbits: New Facial Rigger  [rigbits#28][rigbits#27][rigbits#64][rigbits#33][rigbits#32]
	* Shifter_classic_components: new arm and leg with elbow and knee thickness control [shifter_classic_components#55]
	* Shifter_classic_components: New component arm_2jnt_03 with align wrist with guide option [shifter_classic_components#53]
	* Shifter_classic_components: New component mouth_02 [shifter_classic_components#51]

**Enhancements**
	* Rigbits: Mirror Controls Shape Tool [rigbits#25]
	* Rigbits: RBF manager updated with support for non-control objects  [rigbits#31]
	* Shifter_classic_components: control_01, arm_2jnt_04 add orientation visual feedback [shifter_classic_components#54]

3.1.1
-----
**New Features**
	* shifter_classic_components: New Component: chain_IK_with_variable FK and stack connection [shifter_classic_components#43]
	* shifter_classic_components: New Component: chain_net_01 [shifter_classic_components#42]
	* shifter_classic_components: new component: Lite chain stack [shifter_classic_components#40]

**Enhancements**
	* mgear_core:implemented filesize compression for jSkin and gSkin (pull request #28)
	* Rigbits: Update tweakers modules [rigbits#18]
	* Shifter: add optional uihost argument on addAnimParam and addAnimEnumParam [shifter#60]
	* Shifter: avoid negative scaling in joints [shifter#59]
	* Shifter: inspect settings open tap option [shifter#62]
	* Shifter: Shared custom step fix color feedback and hover information [shifter#57]
	* shifter_classic_components: chain_net_01: improve pickwalk [shifter_classic_components#47]
	* shifter_classic_components: Chains with stack connection should have connection offset options [shifter_classic_components#46]
	* shifter_classic_components: Review channel hosts for stack connection chains [shifter_classic_components#44]
	* simpleRig: handle geometry selection option when convert to shifter rig [simpleRig#6]
	* Synoptic: Fix refresh needed on togglButtons and on visibility/control tabs [synoptic#13]

**Bug Fix**
	* mgear_core: attribute module log error wrong flags [mgear_core#29]
	* shifter_classic_components: chain FK with variable IK the extreme controls should not be on 0 or 1.0 of the path [shifter_classic_components#45]

3.0.5
-----
**Bug Fix**
	* mGear_core: Attribute: moveChannel doesn't support float attr [mgear_core#27]
	* mGear_core: Callback manager: UserTimeChangedManager change condition state to playingBackAuto [mgear_core#28]
	* Rigbits: Eye rigger and Lips Rigger bad naming in rig curves [rigbits#21]
	* Shifter: Export guide to template (.sgt) will break component parent references if name is not unique [shifter#58]


3.0.4
-----
**Bug Fix**
	* Synoptic: Fix refresh needed on togglButtons and on visibility/control tabs [synoptic#13]
	* mGear_core: Node: controller_tag_connect fail if ctl parent doesn't have tag [mgear_core#24]
	* Shifter_classic_components: Eye component update structure [shifter_classic_components#39]
	* Shifter_classic_components: Spine FK: fisrt joint moving with IK chest control [shifter_classic_components#38]
	* Shifter: custom step template still have old name import [shifter#56]
	* Rigbits: hotkey creation command has bad imports [rigbits#19]
	* Shifter: serialized guide with none parent components issue [shifter#55]
	* Rigbits: Ghost control creator and Tweaks should handle ctrl Tag and custom pickwalk [rigbits#20]

3.0.3
-----
**New Features**
	* Flex: Flex is the mGear models (geometry) update tool inside rigs.
	* Shifter: Build Rig from file [shifter#20]
	* Shifter: Game Tools,  for decouple deform and control rig [shifter#6]
	* Shifter: Guide Relative placement [shifter#14]
	* Shifter: Guide serialization to json
	* Shifter: New Guide manager
	* Shifter: Serialized Diff Tool
	* Shifter: Serialized Guide Explorer
	* Shifter_classic_components: New Component: Chain FK spline with variable IK controls [shifter_classic_components#26]
	* Shifter_classic_components: New Component: Chain IK spline with variable FK controls [shifter_classic_components#30]
	* Shifter_classic_components: New Component: Chain Stack [shifter_classic_components#32]
	* Shifter_classic_components: New Component: shoulder_02 [shifter_classic_components#25]
	* Shifter_classic_components: New Component: Spine FK [shifter_classic_components#31]
	* Shifter_classic_components: New Component: Tangent_spline_01 [shifter_classic_components#28]
	* Shifter_classic_components: New Component: Whip chain [shifter_classic_components#27]


**Enhancements**
	* Animbits: softTweak: make UI dockable [animbits#8]
	* Crank: Make UI dockable [crank#3]
	* Crank: Shot Sculpting tool, General update initial Goals [crank#1]
	* mGear_core: attribute: FCurveParamDef should store the samples from getFCurveValues [mgear_core#12]
	* mGear_core: attribute: ParamDef: Dict serialisation [mgear_core#11]
	* mGear_core: pyQt: showDialog option to make windows dockable [mgear_core#6]
	* mGear_core: Skin module: Review it and update use Json and pickle [mgear_core#20] [mgear_core#23]
	* Shifter: Custom step list. Visual cue for shared custom step [shifter#51]
	* Shifter: FCurveParamDef should store the samples from getFCurveValues in value of paramDef [shifter#26]
	* Shifter: update menu with new functionalities [shifter#37]
	* Shifter: Update modal position menu to QT modern version [shifter#46]
	* Shifter_classic_components: add new upv roll control to arm_2jnt  [shifter_classic_components#36]
	* Shifter_classic_components: Add UniScale option for games compatible  [shifter_classic_components#9]
	* Shifter_classic_components: arm_2jnt_01 and leg_2jnt_01: Make optional the extra support joint in the articulations [shifter_classic_components#3]

**API Changes**
	* mgear_dist: Modularisation of mgear [mgear_dist#11]

**Bug Fix**
	* mGear_core: Attribute: channelWrangler apply config from script fails due to attributeError [mgear_core#21]
	* mGear_core: curve: create_curve_from_data_by_name should not take the name from the first shape [mgear_core#17]
	* mGear_core: curve: importing curve while rebuild hierarchy will fail if the parent object don't have unique name [mgear_core#18]
	* Rigbits: Duplicate symmetry bad import string [Rigbits#13]
	* Rigbits: Replace Shape Command doesn't handle if the target object have input connections in the shape [Rigbits#12]
	* Shifter: Component connector: standard fallback [shifter#27]
	* Shifter: Component space references: add checker for space references names [shifter#16]
	* SimpleRig: re-import configuration dont link unselectable geometry [simpleRig#1]


2.6.1
-----
**New Features**
	* Animbits: Crank shot sculpt  [mgear#233]
	* Rigbits: RBF Manager: support for non-control objects  [mgear#228]

2.5.24
-----
**New Features**
	* mGear: IO curves [mgear#76]
	* Rigbits: RBF Manager [mgear#183]
	* Rigbits: set driven key module [mgear#160]
	* Simple Rig: 2.0 [mgear#163]
	* Synoptic: Control lister Tab [mgear#99]
	* Synoptic: geometry visibility manager Tab [mgear#130]
	* Synoptic: Spine IK <--> FK animation transfer [mgear#169]

**Enhancements**
	* Animbits: SoftTweak tool update [mgear#167]
	* mGear: skin: copy skin [mgear#168]
	* Shifter: chain_FK_spline_01: keep length multiplayer channel [mgear#199]
	* Shifter: chain_FK_spline_02: add extra Tweak option [mgear#202]
	* Shifter: component ctrlGrp should be inherit from parent component [mgear#181]
	* Shifter: Component Lite chain and chain FK spline mirror auto pose configuration if override negate axis direction in R [mgear#198]
	* Shifter: Component Lite chain and chain FK spline mirror auto pose configuration if override negate axis direction in R [mgear#198]
	* Shifter: Control_01: lock sizeRef axis [mgear#156]
	* Shifter: Custom Step List: Highlight Background quicksearch [mgear#203]
	* Shifter: Lock joint channels if "separated joint structure" is unchek [mgear#182]
	* Shifter: Make not keyable the joints channel if jnt_org is checked [mgear#188]
	* Shifter: neck_ik: add option to orient IK to world space [mgear#159]
	* Shifter: Partial build skip custom steps [mgear#154]
	* Shifter: spine_S_Shape: add option to orient IK to world space [mgear#164]
	* Shifter: Turn on/off custom steps [mgear#189]

**Bug Fix**
	* mGear:  curve.addCnsCurve: modify the center list in some situations [mgear#172]
	* Rigbits: Blended Gimmick joints bad naming with multy selection [mgear#153]
	* Shifter: 3jnt leg roundness att for knee and ankle [mgear#144]
	* Shifter: add_controller_tag. Fail on Maya old versions [mgear#187]
	* Shifter: Component: spine_IK_02: Last FK control don't have correct attr [mgear#161]
	* Shifter: Controller tag lost if export selection the rig [mgear#175]
	* Shifter: Joint connection: Maya evaluation Bug [mgear#210]
	* Shifter: leg_2jnt and leg _2jnt_freetangents not taking max stretch default setting [mgear#162]
	* Shifter: Spine S Shape: bad build with offset on fk controls [mgear#146]
	* Simple Rig: BBox computation fails with lights [mgear#212]
	* Synoptic: IK/FK transfer doesn't save keyframes on blend channel [mgear#180]
	* Synoptic: IK<->FK transfer strange refresh [mgear#173]

**Known Issues**
	* Shifter: Undo Build from selection crash maya. Now flush Undo to avoid possible crash [mgear#74]


2.4.2
-----
**Bug Fix**
	* Animbits: SoftTweak root lost relative position to parent [mgear#143]

2.4.1
-----
**Bug Fix**
	* Shifter: Rotation inverted on joints with negative scale [mgear#142]

2.4.0
-----
**New Features**
	* Animbits: SoftTweaks tool [mgear#133]
	* LINUX: Maya 2018 solvers
	* Rigbits: Eye rigger tool [mgear#127]
	* Rigbits: Lips Rigger tool [mgear#128]
	* Shifter: New Component: Chain FK spline Component [mgear#104]
	* Shifter: New Component: Lite FK chain [mgear#115]
	* Shifter: New Component: Spine_S_shape [mgear#96]

**Enhancements**
	* Shifter: Add alias names for space references [mgear#110]
	* Shifter: Add visual crv connection for the upVector controls [mgear#124]
	* Shifter: arm and leg 2jnt: add optional controls x Joint [mgear#114]
	* Shifter: chain_FK_spline: add option to control visibility of controls [mgear#136]
	* Shifter: Hide controls on Playback rig setting [mgear#131]
	* Shifter: Improve parallel evaluation [mgear#123]
	* Shifter: Lite_chain and Chain_FK_spline. Option to override side negation [mgear#139]
	* Shifter: Neck_ik_01: add option to have only IK space reference [mgear#132]
	* Shifter: Review rollspline solver precision values [mgear#138]
	* Shifter: Set all controls shape to d1 curves [mgear#118]
	* Shifter: Set to False the default use of uniscale in joints [mgear#117]
	* Shifter: Update component with Proxy attributes [mgear#111]

**Bug Fix**
	* Shifter: Bindpose bug with custom controllers grp [mgear#134]
	* Shifter: Component addJnt error if negative scaling [mgear#141]
	* Shifter: Extracted controls doesn't clean shape name [mgear#135]
	* Shifter: leg_2jnt_01 maxStretch setting is lost at build time [mgear#140]
	* Shifter: Maya 2018.2 flip in leg_2jnt_01 component [mgear#125]

2.3.0
-----
**Enhancements**
	* mGear: Attribute: addAttribute not setting default attribute value. [mgear#84]
	* mGear: Attribute: update with lock and unlock attribute functions [mgear#83]
	* mGear: PEP8 Style Refactor [mgear#100]
	* mGear: Refactor all exception handling [mgear#88]
	* mGear: Vendoring QT [mgear#89]
	* Shifter: Build command review and log popup window [mgear#73]
	* Shifter: Change Global_C0_ctl to World_ctl [mgear#66]
	* Shifter: Control_01: Add option to have mirror behaviour [mgear#68]
	* Shifter: Improve rig build speed [mgear#65]
	* Shifter: Leg_2jnts_freeTangents_01:no ikFoot in upvref attribute [mgear#62]
	* Shifter: Reload components in custom path [mgear#78]
	* Shifter: Update guide structure in pre custom step [mgear#101]
	* Simple Rig: Update functionality revision  [mgear#71]
	* Synoptic: spring bake util [mgear#61]

**Bug Fix**
	* Rigbits: createCTL function issue [mgear#59]
	* Rigbits: export skin pack error with crvs [mgear#56]
	* Rigbits: skin: There is a case in exportSkin function breaks the existing file [mgear#58]
	* Shifter: 3 joint leg: soft Ik range min in graph editor [mgear#82]
	* Shifter: arm_2jnt_freeTangents_01 no attribute 'rollRef' [mgear#63]
	* Shifter: Arms auto upvector and shoulder space jump [mgear#85]
	* Shifter: Chain_spring_01: pop if manipulate FK ctl after Bake [mgear#75]
	* Shifter: Connect Ctl_vis [mgear#103]
	* Shifter: Control_01: rotation axis is missing Y lock [mgear#74]
	* Shifter: Japanese Ascii [mgear#79]
	* Shifter: Spring chain: lock control parent and bake spring bug [mgear#67]
	* Shifter: Synoptic: IK/FK Match with arm_ms_2jnt_01 [mgear#80]

**Known Issues**
	* Shifter: Undo Build from selection crash maya [mgear#74]

2.2.4
-----
**Enhancements**
	* Shifter: Global scale and size of controllers. [mgear#50]

2.2.3
-----
**Enhancements**
	* Shifter: Custom Steps: Added Stop Build and Try again option if step fail.[mgear#43]

**Bug Fix**
	* Synoptic: Match IK/FK with split ctl for trans and rot [mgear#54]

2.2.2
-----
**Enhancements**
	* Shifter: Components: Legs: Mirror axis behavior on upv and mid ctl [mgear#47]
	* Shifter: Componets: Arms: IK ctl mirror behaviour [mgear#48]
	* Shifter: arm roll new reference connector [mgear#53]

**Bug Fix**
	* Shifter: component UI min division hang. Check all components [mgear#42]
	* Shifter: quadruped rig not being created in 2018 [ mgear#44]
	* Shifter: Close settings Exception on Maya 2018: Note: This is a workaround. The issue comes from Maya 2018 [mgear#49]

2.2.1
-----
**Bug Fix**
	* Shifter: Component: Hydraulic: Fix bad reference connector
	* Docs: Text error fix
	* Shifter: Text error fix

2.2.0
-----
**New Features**
	* Maya 2018 compatible
	* Simple autorig This a new rigging sytem for basic props.
	* Channel Wrangler: Channel manager with export import options.

**Enhancements**
	* Synoptic: key/select all for custom widgets
	* Skin IO: IO skin for curves & nurbs
	* Skin IO: Now can export with Skin Packs. Every object will be in a separated file.
	* Shifter: custom Sets: Now is possible to add custom sets to shifter components
	* Shifter: Now all the controls are Tag as a control (> Maya 2016.5)
	* Shifter: Custom Rig controls navigation
	* Shifter: Custom steps IO to JSON file.
	* Shifter: Componente: Chain_01: Non uniform scaling for FK controls
	* Shifter: Now the controls have unchecked historical interest from ctl shapes for cleaner channel box
	* Rigbits: Now replace shape support multiple shapes
	* mGear: Menu updated with about info and useful links
	* mGear: Added support for RGB color on icons/Controls

**Bug Fix**
	* Shifter: component: freetangent arm and leg: Fixed joint offset in the extremes
	* General: Fixed bad parenting for PySide dialogs.


2.1.1
-----
**New Features**
	* mGear solvers: New vertex position node.  This node gets the vertex position in worldspace.
	* Rigbits: New rigging commont library with toos and functions to help the rigging system. This library is meant to be use with custom steps or other rigging tools.
	* Shifter: Components: New  Components from Miles Cheng "arm_ms_2jnt_01", "shoulder_ms_2jnt_01" and "leg_ms_2jnt_01"
	* Shifter: Components: New enviroment variable: MGEAR_SHIFTER_COMPONENT_PATH (only project components)
	* Shifter: Custom Step: New enviroment variable: MGEAR_SHIFTER_CUSTOMSTEP_PATH to stablish relative paths for the custom steps data.
	* Shifter: New Channel naming options

**Improvements**
	* Improved error logging for custom steps and Synoptic.
	* Shifter: Clean up jnt_org empty groups after rig build.
	* Shifter: Components: Updated neck with optiona tangent controls.
	* Shifter: Components: Arm have a new option to separate the IK controls in rotation and translation control
	* Shifter: Components: Control extraction name buffer to avoid name clashing for ctl extraction on guides
	* Shifter: Components: Pin elbow/knee
	* Shifter: Components: Spine updated: Autobend optional control and optional mid tangent control
	* Shifter: Components: Arms mid ctl and upv with optinal mirror behaviour.
	* Shifter: Custom step using class implementation
	* Shifter: Track information (rig Asset, components used version and mGear version)
	* Synoptic: General visual and structure improvement. Big Thanks to Yamahigashi-san.
	* Synoptic: IK/FK animation transfer
	* Shifter: Updated biped guide
	* Shifter: Updated Quadruped guide

**Bug Fix**
	* Bad layout on setting windows with HDPI displays.
	* Shifter: Components: General clean up and bug fixing (Please check github commint for more info).
	* Issue mgear#9  leg_3jnt: Flip offset rz double connection
	* Issue mgear#13  Chain_01 IK refs not being connected

2.0
---
**New Features**
	* Custom enviroment variables for synoptic: MGEAR_SYNOPTIC_PATH
	* cvWrap deformer included.
	* Gimmick joints basic tools
	* Mocap HumanIK mapping tool for standard Shifter biped
	* New Component settings view.
	* New Documentation
	* New licensing under MIT license terms.
	* Pre and Post custom Steps.
	* Shifter: Modular rigging sytem rebranded.
	* Shifter: Quadrupeds template and new leg component for 3 bones legs.
	* Shifter: Single Hierarchy Joint connexion
	* Shifter: Update Guides Command.
	* Synoptic view Updated.

**Inprovements**
	* Component guides will snap to parent position at creation time.
	* Duplicate symmetry can find partial chain names. Is not needed to duplicate from the top root of the branch.
	* Groups and dag pose connected to rig base node. This will avoid lost elements if we export selection.
	* Guide Blades have new attr to control the  roll offset
	* mGear version and other useful information in guide root.
	* Newly created guide components automatic update of the side and uiHost from the parent attributes.
	* Shifter componets full review and functions unified.





