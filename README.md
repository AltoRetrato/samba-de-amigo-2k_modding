## Samba de Amigo Ver. 2000: modding tools and information.
![Samba de Amigo](docs/title.png)

[Samba de Amigo](https://en.wikipedia.org/wiki/Samba_de_amigo) is a rhythm game developed by Sonic Team and published by Sega. There are versions for arcade machines, Dreamcast and Wii consoles.

[Samba de Amigo: Ver. 2000](https://en.wikipedia.org/wiki/Samba_de_amigo#Ver._2000) was released for the Dreamcast only in Japan, including 20 new songs and new playing modes.

Here you'll find information and tools to help you mod "Samba de Amigo: Ver. 2000" for the Dreamcast, such as adding English translations and custom songs. This can put your old maracas to good use again! :)

#### What's currently available
 - [description of all files in the Samba de Amigo ver. 2000 GDI image](docs/Samba%20de%20Amigo%20ver.%202000%20-%20list%20of%20files.txt) (including Japanese to English translations).
 - [description of the .AMG ("Amigo") file format](docs/Samba%20de%20Amigo%20ver.%202000%20-%20AMG%20file%20format.txt)
 - [amigo_explorer.py](/amigo_explorer), a console script to dump, analyse & convert Amigo files. It also allows you to import Wii songs into a Dreamcast GDI image, and (in the future) might help you translate the game from Japanese to English.
 - [Kaitai Struct files (.ksy)](/amigo_explorer) describing the Amigo .AMG file format for Samba de Amigo ver. 2000 (Dreamcast) and for the Wii. I also provided the "compiled" parsers in Python (currently only for reading).
 
 #### To-do
 - [ ] create GUI Python script to simplify GDI modding:
   - [ ] include [gditools Python library](https://sourceforge.net/projects/dcisotools/) to manipulate GDI images.
   - [ ] include / port other libraries to manipulate sound & image files.
   - [ ] create option to enable "downloaded" songs (saving time & VMU space).
   - [ ] create option to change save file name (so you can have a save for each pack of songs).
   - [ ] create an Amigo file viewer / editor ([amigo_explorer.py](/amigo_explorer) is more than halfway there).
   - [ ] enable (semi-)automatic importing / conversion of songs from:
     - [X] Wii version ([amigo_explorer.py](/amigo_explorer) already does this)
     - [ ] Shakatto Tambourine (Naomi)
     - [ ] MiniMoni. Shakatto Tambourine! Dapyon! (PS)
     - [ ] StepMania, etc.
