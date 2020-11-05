MHX2 - MakeHuman eXchange format 2

MHX2 is a format to copy data from MakeHuman to Blender using a JSON file. Because of triangle support, at least MakeHuman version 1.2.x is demanded.

Original version is hosted separately at https://bitbucket.org/Diffeomorphic/mhx2-makehuman-exchange. To download the repository as a zip file, go to https://bitbucket.org/Diffeomorphic/mhx2-makehuman-exchange/downloads.

The overall license for MHX2 is GPLv2, but there is an additional license clarification at https://thomasmakehuman.wordpress.com/license-information/

This is a downstream version using python3 with fixes for triangle meshes, meshes with huge numbers of vertices and for the use in blender 2.80

Instructions:

1. Copy or link the folder 9_export_mhx2 to the MakeHuman plugins folder.


2. Copy or link the folder import_runtime_mhx2 to the addons destination directory where Blender will look for user-defined add-ons. Check the Blender docs for more information.

3. Open MakeHuman and design you character. In the Files > Export tab, select MakeHuman Exchange (mhx2), select the export path, and press export.

4. Open Blender and enable the MHX2 importer. Select Edit > User Preferences. In the window that opens, select the Addons tab and then the MakeHuman category. Enable MakeHuman: Import-Runtime: MakeHuman eXchange 2 (.mhx2), and Save User Settings.

5. Select File > Import > MakeHuman (.mhx2), and navigate to the mhx2 file exported from MakeHuman.

6. By default, the exported character is imported into Blender as it appears in MakeHuman. However, if Override Export Data is selected, the character will be rebuilt according to the options that appear.
