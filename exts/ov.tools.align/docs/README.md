# Align Tool

This tool allows you to align a single or multiple objects to match a target's position, rotation or scale.

![Align types](/exts/ov.tools.align/data/transform.png)

## Usage
1. Enable the align tool extension and you should see a window popup like below:

   ![Align Tool Window](/exts/ov.tools.align/data/window.png)
2. Select the objects you wish to align. **The last item in your selection will be the target**.

## Things to note
- Only supports World position alignment.
- Objects must be on the same level. You cannot align to a child or parent object.
- For scaling, you can only scale on a single axis.

## Adding This Extension
To add this extension to your Omniverse app:
1. Go into: Extension Manager -> Gear Icon -> Extension Search Path
2. Add this as a search path: `git://github.com/wnger/kit-extension-align?branch=main&dir=exts`
