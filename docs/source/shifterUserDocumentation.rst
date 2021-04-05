Shifter User Documentation
##########################

WIP section: Please visit:
`mGear Youtube channel <https://www.youtube.com/c/mgearriggingframework/>`_

* components
* creating new components
* guides templates and basic rig building
* stepped rig building
* scalability and reusability
* gotchas
* tips


Plebes - Instant Rigged Characters Using mGear
==============================================

Plebes is a simple template based tool to quickly rig characters from various character generators, such as DazStudio, Character Creator 3,  MakeHuman or Mixamo. What it does is build an mGear rig that matches the proportions of your character, and then constrains the joints of that character to the rig with just a few clicks.

.. image:: images/shifter/plebes_ui.png

How to Rig Plebes
-----------------

1) Open Plebes interface from the mGear>Shifter>Plebes... menu.
2) Export the character from the character generator as FBX and bring it into Maya.
3) Select the **Character Template** that matches your character generator.
4) Follow the template specific instructions in the Plebes interface.
5) Press **Import Guides** to import the mGear biped guides.
6) Press **Align Guides** to align the mGear guides to your character's joints.
7) Look over the guides, and manually adjust any that are off (e.g. typically the heel and sides of the feet).
8) Press **Build Rig** to build the rig.
9) Press **Attach Plebe to Rig** to constrain the character to the mGear rig. This  also removes any locks, keys/connections and/or limits on the translate, rotate and scale attributes on the character's original joints.

You can delete the rig, adjust the guides and rebuild it, like you can normally with mGear, by simply deleting the "rig" group and running the last two steps again.

.. note::
   Some character generators build their characters with completely straight or misaligned elbows and knees, which makes it impossible for mGear to figure out where to aim the knee or elbow, so you may need to rotate the joints slightly before aligning the guides to them, to make sure they are pointing in the right direction.

Known Limitations
-----------------

Plebes is meant to quickly rig generic characters, typically for use in the background or for crowd agents, so has some limitations. If you need more of a hero rig, you can use the guide placement as a starting point, but it's probably a good idea to skin the character directly to your mGear joints, rather than using **Attach Plebe to Rig**. Other known limitations include:

- Stretching and scaling of limbs may not work correctly for all templates, though it should work fine for all "normal" animation.
- Some characters come with additional joints, such as face joints, that Plebes does not add any controls to.

Plebe Templates
---------------

What gets aligned and constrained to what is defined by simple JSON templates. Plebes ships with templates for the several commonly used character genrators, but should you want to add more or modify the existing ones, you can easily do so. You can define the location of additional templates by defining the environment variable PLEBE_TEMPLATES_DIR. You can have multiple template dirs, so you can add your custom ones from your home folder or project specific ones as needed, just make sure each tamplate has a unique name.

The templates look like this:


.. code-block:: json

    {
        "help": "This show up when you hover over the template menu.",
        "root": "CC_Base_BoneRoot",
        "guides": [
            {"guide": "CC_Base_BoneRoot"},
            {"neck_C0_tan0": [
                "CC_Base_NeckTwist01",
                "CC_Base_NeckTwist02"
            ]}
        ],
        "settings": [
            {"arm_L0_root": [
                { "div0": 1 },
                { "div1": 1 },
                { "supportJoints": 0}
            ]}
        ],
        "joints": [
            {"local_C0_ctl": {
                "joint": "CC_Base_BoneRoot",
                "constrain": "111"}
            },
            {"spine_C0_0_jnt": {
                "joint": "CC_Base_Hip",
                "constrain": "110"}
            }
        ]
    }

- **help** - Documentation that shows up in the interface, detaling any specific things you need to do to work with this template.
- **root** - The top level joint/node from the character generator.
- **guides** - List of which guides to position at which joints.
    - If you match it to a list of joints, like with the neck above, it will be placed between them.
- **settings** - Settings to adjust on the guides before building the rig. Typically this is number of twist joints, but can be any attribute and value combination.
- **joints** - List of mGear joints and which of the character's joints to constrain to it.
    - **joint** - Name of the character's joint to constrain to mGear.
    - **constain** - Three 0 or 1's. First is if to point constraint, second is orient and third is scale.
