MHX2 - MakeHuman eXchange format 2

MHX2 replaces the old MHX format that has been bundled with MakeHuman. Contrary to the first version, which was a Blender-specific format, MHX2 is not tied to a specific application. Instead it exports relevant information about the MakeHuman meshes and materials, which allows importers to build their own application-specific rigs. Currently there is only an importer for Blender, but mhx2 importers for other applications will eventually be welcomed. Support for the old MHX format will eventually be terminated.

MHX2 is not part of the MakeHuman distribution. It is hosted separately at https://bitbucket.org/Diffeomorphic/mhx2-makehuman-exchange. To download the repository as a zip file, go to https://bitbucket.org/Diffeomorphic/mhx2-makehuman-exchange/downloads.

Instructions.

1. Copy or link the folder 9_export_mhx2 to the MakeHuman plugins folder.


2. Copy or link the folder import_runtime_mhx2 to the addons destination directory where Blender will look for user-defined add-ons. Depending on the OS, this may be:

    Windows 7: C:\Users\%username%\AppData\Roaming\Blender Foundation\Blender\2.6x\scripts\addons

    Windows XP: C:\Documents and Settings\%username%\Application Data\Blender Foundation\Blender\2.6x\scripts\addons

    Vista: C:\Program Files\Blender Foundation\Blender\%blenderversion%\scripts\addons (this is valid at least for blender 2.69)

    Linux: /home/$user/.blender/$version/scripts/addons


3. Open MakeHuman and design you character. In the Files > Export tab, select MakeHuman Exchange (mhx2), select the export path, and press export.

4. Open Blender and enable the MHX2 importer. Select File > User Preferences. In the window that opens, select the Addons tab and then the MakeHuman category. Enable MakeHuman: Import-Runtime: MakeHuman eXchange 2 (.mhx2), and Save User Settings.

5. In the File tab, enable Auto Run Python Scripts and Save User Settings.

6. Select File > Import > MakeHuman (.mhx2), and navigate to the mhx2 file exported from MakeHuman.

7. By default, the exported character is imported into Blender as it appears in MakeHuman. However, if Override Export Data is selected, the character will be rebuilt according to the options that appear.