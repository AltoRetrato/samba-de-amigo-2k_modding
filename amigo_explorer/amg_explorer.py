#!/usr/bin/python3
# -*- coding: utf-8 -*-
# By Ricardo Mendonça Ferreira - ric@mpcnet.com.br

# 2019.01.11  0.1  1st public release
# 2019.01.04  0.0  1st version

import os
import re
import csv
import json
from glob       import glob
from struct     import *
from shutil     import copy2
from subprocess import run
from samba_de_amigo_amg_dc  import SambaDeAmigoAmgDc
from samba_de_amigo_amg_wii import SambaDeAmigoAmgWii

__version__ = "0.1"

# Please set the correct paths below:
ffmpeg     = r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"                             # path to ffmpeg
wimgt      = r"E:\Games\Dreamcast\Samba2K_hack\wii\szs\bin\wimgt.exe"              # path to wimgt (from Wiimms SZS Tools)
#afs_packer = r"E:\Games\Dreamcast\Samba2K_hack\afs\afs_packer_11\AFSPacker.exe"   # path to AFS Packer
# afs_packer produces "Error: This AFS file doesn't seem to have a Filename table. This format isn't supported yet."
# I'll write my custom afs code later...
dc_path    = r"E:\Games\Dreamcast\Samba2K_hack\gdi\01-Samba_de_Amigo_2K Extracted" # path to unpacked GDI of Samba de Amigo ver. 2000
wii_path   = r"E:\Games\Dreamcast\Samba2K_hack\wii\files\songdb"                   # path to unpacked Samba de Amigo for Wii
# ========== End of user configurable section ==========  #
wii_amg    = os.path.join(wii_path, "amg"       )
wii_stream = os.path.join(wii_path, "stream"    )
wii_songdb = os.path.join(wii_path, "songdb.csv")

SHAKE = 0b0001 # 1
SHBEG = 0b0011 # 3
POSE  = 0b0100 # 4
SHEND = 0b1000 # 8
HST1  = 0b0101 # 5
HST2  = 0b0110 # 6
TL    = 2**4
ML    = 2**5
BL    = 2**6
TR    = 2**7
MR    = 2**8
BR    = 2**9
# 10-19: hustle
# 20-31: zero?
cmd_dict = {
    SHAKE: "hit",
    SHBEG: "hit rapidly begin",
    SHEND: "hit rapidly end",
    POSE : "pose",
    HST1 : "hustle begin",
    HST2 : "hustle end",
    TL   : "TL",
    ML   : "ML",
    BL   : "BL",
    TR   : "TR",
    MR   : "MR",
    BR   : "BR",
}

hustle_dict = {
     0 : "TL/TR",
     1 : "BL/BR",
     2 : "TL/ML",
     3 : "TR/MR",
     4 : "ML/BL",
     5 : "MR/BR",
     6 : "TL/BL",
     7 : "TR/BR",
     8 : "circle anti-clockwise",
     9 : "circle clockwise",
    10 : "TL/TR",
    11 : "BL/BR",
    12 : "TL/TR",
    13 : "BL/BR",
    14 : "TL/TR 2 hands",
    15 : "BL/BR 2 hands",
}

def readSongDB():
    """Read Wii's songdb.csv file into a dictionary."""
    csv_reader = csv.reader(open(wii_songdb))
    songdb  = {}
    headers = None
    for row in csv_reader:
        if not headers:
              headers = row
        else: songdb[row[1]] = dict(zip(headers, row))
    return songdb


def cmd2str(cmd):
    """Convert an Amigo bit field command into a string."""
    cmds = []
    i = cmd & 0b1111
    j = cmd >> 16 & 0xf
    cmds.append(cmd_dict.get(i, str(i)))
    if i == HST1 or i == HST2:
        # hustle command
        cmds.append(hustle_dict.get(j, str(j)))
    else:
        # hit positions - except for hustle
        for i in range(4, cmd.bit_length()):
            j = 2 ** i
            if j & cmd != 0:
                cmds.append(cmd_dict.get(j,str(i)))
    return ", ".join(cmds)


def readAllAMG(path, amg_dict):
    """Read all .AMG files in the path into the specified dictionary."""
    for fn in glob(os.path.join(path,"*.amg")):
        amg[os.path.split(fn)[-1]] = open(fn, "rb").read()
    #return amg_dict


def blocks_overview(fn, data):
    """List block names and sizes for the given .AMG file."""
    print(f" {len(data):7,} {fn:22} | ", end="")
    i = 0
    head = data[i:i+4].decode()
    if head == "HEAD":
        # Dreamcast == little-endian
        print("[DC ] ", end="")
        mask = "<I"
    elif head == "DAEH":
        # Wii == big-endian
        print("[Wii] ", end="")
        mask = ">I"
    else:
        print("Wrong head format:", head)
        return
    while True:
        name = unpack(mask, data[i:i+4])[0]
        name = pack("<I", name).decode()
        if name == "END_": break
        i += 4
        size = unpack(mask, data[i:i+4])[0]
        i += 4 + size
        print(f"{name} {size:5}, ", end=" ")
        if i >= len(data): break
    print()


def dump(fn, data, block_name_regex=None):
    """Dump the contents of a given .AMG file, using the Kaitai Struct files."""
    print(f" {fn}, {len(data):7,} bytes ", end="")

    # Is it a DC or a Wii file?
    head = data[0:4].decode()
    if   head == "HEAD": # Dreamcast == little-endian
        print("[DC]")
        amg = SambaDeAmigoAmgDc.from_bytes(data)
    elif head == "DAEH": # Wii == big-endian
        print("[Wii]")
        amg = SambaDeAmigoAmgWii.from_bytes(data)
    else:
        print("-> Wrong head format:", head)
        return

    for block in amg.blocks:
        name = block.block_name.name.upper()
        # regex test - show only matching block names
        if block_name_regex:
            if not re.match(block_name_regex, name):
                continue
        # show block name & size
        print(f"   {name}", end="")
        if name == "END_":
            print("\n")
            break
        print(f" {block.block_size:5} bytes")
        # code for each block type
        if name == "HEAD":
            print("      {n:08X} | {n} entries".format(n=block.block_data.num_entries))
            for frame in block.block_data.entries:
                print(f"      {frame:08X} | frame {frame:4} ({frame/60:6.2f} s)")
        elif name == "ACT_":
            print("      {n:08X} | Act number {n}".format(n=block.block_data.act_num))
            print("      {n:08X} | {n} entries".format(n=block.block_data.num_entries))
            for entry in block.block_data.entries:
                f = entry.frame
                print(f"      {f:08X} | frame {f:4} ({f/60:6.2f} s) ", end="")
                print("{:08X} ". format(entry.dword1), end="")
                print("{:08X} ". format(entry.dword2), end="")
                print("{:08X} [".format(entry.dword3 & 0xFFFFFFFF), end="")
                print("{}, ".format(entry.dword1), end="")
                print("{}, ".format(entry.dword2), end="")
                print("{}]". format(entry.dword3))
        elif name == "CAM_":
            print("      {n:08X} | {n} entries".format(n=block.block_data.num_entries))
            for entry in block.block_data.entries:
                f = entry.frame
                print(f"      {f:08X} | frame {f:4} ({f/60:6.2f} s) ", end="")
                print("{:08X} ". format(entry.dword1), end="")
                print("{:08X} ". format(entry.dword2 & 0xFFFFFFFF), end="")
                print("{:08X} ". format(entry.dword3 & 0xFFFFFFFF), end="")
                print("{:08X} ". format(entry.dword4 & 0xFFFFFFFF), end="")
                print("{:08X} ". format(entry.dword5 & 0xFFFFFFFF), end="")
                print("{:08X} ". format(entry.dword6), end="")
                print("{:08X} [".format(entry.dword7 & 0xFFFFFFFF), end="")
                print("{}, ".format(entry.dword1), end="")
                print("{}, ".format(entry.dword2), end="")
                print("{}, ".format(entry.dword3), end="")
                print("{}, ".format(entry.dword4), end="")
                print("{}, ".format(entry.dword5), end="")
                print("{}, ".format(entry.dword6), end="")
                print("{}]". format(entry.dword7))
        elif name in set(["EASY","HARD","NORM","SUPR","DA_E","DA_H","DA_N","DA_S"]):
            print("      {n:08X} | Player {p}".format(n=block.block_data.player_number.value, p=block.block_data.player_number.name))
            print("      {n:08X} | {n} max amigo points".format(n=block.block_data.max_amigo_points))
            print("      {n:08X} | {n} commands".format(n=block.block_data.num_commands))
            for cmd in block.block_data.commands:
                f    = cmd.frame
                bf   = cmd.cmd_bitfield
                b    = f"{bf:020b}"
                cmds = cmd2str(bf)
                print(f"      {f:08X} {bf:08X} | frame {f:4} ({f/60:6.2f} s), cmd {b[0:4]} {b[4]} {b[5]} {b[6:10]} {b[10:16]} {b[16:20]} {cmds}")
        elif name == "ONSH":
            print("      {n:08X} | {n} entries".format(n=block.block_data.num_entries))
            for entry in block.block_data.entries:
                b = f"{entry:032b}"
                print(f"      {entry:08X} | {b[0:4]} {b[4:8]} {b[8:12]} {b[12:16]} {b[16:20]} {b[20:24]} {b[24:28]} {b[28:32]} [{entry}]")
        else:
            print("I don't know to handle blocks", name)
        print()


def dump_old(fn, data, block_name_regex=None):
    print(f" {fn}, {len(data):7,} bytes ", end="")
    i = 0
    head = data[i:i+4].decode()
    if head == "HEAD":
        # Dreamcast == little-endian
        print("[DC]")
        mask = "<I"
    elif head == "DAEH":
        # Wii == big-endian
        print("[Wii]")
        mask = ">I"
    else:
        print("-> Wrong head format:", head)
        return
    while True:
        name = unpack(mask, data[i:i+4])[0]
        name = pack("<I", name).decode()
        if block_name_regex:
            if re.match(block_name_regex, name):
                  out = print
            else: out = lambda *x, end=None: None
        else:
            out = print
        out(f"   {name}", end="")
        if name == "END_": 
            print()
            break
        i += 4
        size = unpack(mask, data[i:i+4])[0]
        out(f" {size:5} bytes")
        i += 4
        end = i+size
        num = 0
        while i < end:
            dword = unpack(mask, data[i:i+4])[0]
            if name == "HEAD":
                if   num == 0: out(f"      {dword:08X} | {dword} entries")
                else         : out(f"      {dword:08X} | frame {dword:4} ({dword/60:6.2f} s)")
            elif name == "ACT_":
                if   num == 0: out(f"      {dword:08X} | Act number {dword}")
                elif num == 1: out(f"      {dword:08X} | {dword} entries")
                else       : 
                    out(f"      {dword:08X} | frame {dword:4} ({dword/60:6.2f} s) ", end="")
                    #if dword == 0 and num != 2:
                    #    i += 4
                    #    print()
                    #    continue
                    l1 = []
                    l2 = []
                    for j in range(3):
                        i += 4; 
                        dword = unpack(mask, data[i:i+4])[0]
                        value = unpack('i', pack('<I', dword))[0]
                        l1.append(f"{dword:08X}")
                        l2.append(f"{value}")
                    out(" ".join(l1), f" [{', '.join(l2)}]")
            elif name == "CAM_":
                if   num == 0: out(f"      {dword:08X} | {dword} entries")
                else       : 
                    out(f"      {dword:08X} | frame {dword:4} ({dword/60:6.2f} s) ", end="")
                    if dword == 0 and num != 1:
                        i += 4
                        print()
                        continue
                    l1 = []
                    l2 = []
                    for j in range(7):
                        i += 4; 
                        dword = unpack(mask, data[i:i+4])[0]
                        value = unpack('i', pack('<I', dword))[0]
                        l1.append(f"{dword:08X}")
                        l2.append(f"{value}")
                    out(" ".join(l1), f" [{', '.join(l2)}]")
            elif name in set(["EASY","HARD","NORM","SUPR","DA_E","DA_H","DA_N","DA_S"]):
                if   num == 0: out(f"      {dword:08X}          | Player {dword}")
                elif num == 1: out(f"      {dword:08X}          | {dword} max amigo points")
                elif num == 2: out(f"      {dword:08X}          | {dword} commands")
                else:
                    if dword == 0:
                        out(f"      {dword:08X}          |")
                    else:
                        i   += 4
                        num += 1
                        dword2 = unpack(mask, data[i:i+4])[0]
                        cmds   = cmd2str(dword2)
                        b      = f"{dword2:020b}"
                        out(f"      {dword:08X} {dword2:08X} | frame {dword:4} ({dword/60:6.2f} s), cmd {b[0:4]} {b[4]} {b[5]} {b[6:10]} {b[10:16]} {b[16:20]} {cmds}")
            else:
                out(f"{dword:08X} ", end="")
            i   += 4
            num += 1
        out()
        if i >= len(data): break
    print()


def search_cmd(fn, data, cmd):
    """Used to inspect hustle commands, by showing only files with the given command.
       Then play those songs, record a video and match what you see with what tou get...
    """
    i = 0
    head = data[i:i+4].decode()
    if head == "HEAD":
        # Dreamcast == little-endian
        mask = "<I"
    elif head == "DAEH":
        # Wii == big-endian
        mask = ">I"
    else:
        print("-> Wrong head format:", head)
        return
    found = {}
    while True:
        name = unpack(mask, data[i:i+4])[0]
        name = pack("<I", name).decode()
        if name == "END_": 
            break
        i += 4
        size = unpack(mask, data[i:i+4])[0]
        i += 4
        end = i+size
        num = 0
        player = None
        while i < end:
            dword = unpack(mask, data[i:i+4])[0]
            if name in set(["DA_E","DA_H","DA_N","DA_S"]): # "EASY","HARD","NORM","SUPR",
                if   num == 0: player = dword
                elif num >= 3:
                    if dword != 0:
                        i   += 4
                        num += 1
                        dword2 = unpack(mask, data[i:i+4])[0]
                        bin_cmd = f"{dword2:020b}"
                        if bin_cmd.startswith(cmd):
                            found[f"P{2-player} {name}"] = True
            i   += 4
            num += 1
        if i >= len(data): break
    if found:
        print(f"{fn} [{'; '.join(found.keys())}]")


def call_ffmpeg(args):
    cp = run(args)
    if cp.returncode != 0:
        print("Oops! Seems like audio conversion went wrong...")
        print("Arguments used:", args)
        print("Return code...:", cp.returncode)


def convert_audio(fnWii, fnDC):
    yn = input("Convert audio as well? (Y/N) ")
    if yn.lower().startswith("y"):
        if not os.path.exists(ffmpeg):
            print(f"Could not find {ffmpeg} - edit this script and/or check your paths and try again.")
            exit()
        call_ffmpeg([ffmpeg, "-i", fnWii, fnDC])
        # Create PRE audio file
       #songdb = readSongDB()
        wiiKey = os.path.splitext(os.path.split(fnWii)[-1])[0]
        start  = 10 # int(songdb.get(wiiKey, {}).get("pre start milsec",    "0")) // 1000
        end    = 30 # int(songdb.get(wiiKey, {}).get("pre end milsec",  "22000")) // 1000
        dur    = end -start
        p1, p2 = os.path.split(fnDC)
        fnPre  = os.path.join(p1, "PRE_" + p2)
        call_ffmpeg([ffmpeg, "-ss", str(start), "-t", str(dur), "-i", fnWii, "-af", f"afade=in:st=0:d=1,afade=out:st={dur-2}:d=2", fnPre])


class Dword_Buffer():
    """Helper class for file conversion."""
    
    def __init__(self):
        self.data = []
        self.current_size = 0
        self.final_size   = 0
    
    def set_final_size(self, value):
        self.current_size = 0
        self.final_size   = value
    
    def b(self, value):
        """Store a Python binary."""
        self.data.append(value)
        self.current_size += len(value)

    def i(self, value):
        """Store a Python integer as binary dword."""
        self.b(pack("<I", value & 0xFFFFFFFF))

   #def s(self, value): i(pack("<I", unpack("<I",value.encode())[0]))

    def pad(self):
        """Top-up a block size with zeros."""
        diff = self.final_size - self.current_size
        if diff:
            self.data.append(b'\x00' * diff)

    def data_bytes(self):
        """Return a bytes object with the data stored so far."""
        return b"".join(self.data)


def convert(fn, data, hack_data=None):
    """Convert an Wii's .AMG file to the Dreamcast format."""
    fnWii = os.path.join(wii_amg, fn)
    fnOut = os.path.join(dc_path, "VAMOS_A_CARNAVAL.AMG")
    yn = input(f"""Will convert [{fnWii}]
and write to [{fnOut}]
OK? (Y/N) """)
    if yn.lower().startswith("y"):
        amg = SambaDeAmigoAmgWii.from_bytes(data)
        out = Dword_Buffer()

        # "Hack" to replace some blocks in the Wii file with blocks from a Dreamcast .AMG
        hack_blocks = None
        if hack_data:
            hack = SambaDeAmigoAmgDc.from_bytes(hack_data)
            hack_blocks = { b"HEAD_": [], b"ACT_": [], b"CAM_": [] }
            for block in hack.blocks:
                block_name = block.block_name.name.upper().encode()
                if block_name in hack_blocks:
                    hack_blocks[block_name].append(block)                    

        for block in amg.blocks:
            # block name
            block_name = block.block_name.name.upper().encode()
            if block_name == b"ONSH": continue # skip this block entirely
            out.b(block_name)
            if block_name == b"END_": continue # this block has no contents (not eveven size)

            # Replace Wii blocks with other data?
            if hack_data:
                if block_name in hack_blocks:
                    block = hack_blocks[block_name].pop(0)

            # block size (in bytes)
            out.i(block.block_size)
            out.set_final_size(block.block_size)

            # block data - varies by block type
            if block_name == b"HEAD":
                out.i(block.block_data.num_entries)
                for frame in block.block_data.entries:
                    out.i(frame)
                out.pad()
            elif block_name == b"ACT_":
                out.i(block.block_data.act_num)
                out.i(block.block_data.num_entries)
                for entry in block.block_data.entries:
                    out.i(entry.frame )
                    out.i(entry.dword1)
                    out.i(entry.dword2)
                    out.i(entry.dword3)
                out.pad()
            elif block_name == b"CAM_":
                out.i(block.block_data.num_entries)
                for entry in block.block_data.entries:
                    out.i(entry.frame )
                    out.i(entry.dword1)
                    out.i(entry.dword2)
                    out.i(entry.dword3)
                    out.i(entry.dword4)
                    out.i(entry.dword5)
                    out.i(entry.dword6)
                    out.i(entry.dword7)
                out.pad()
            elif block_name in set([b"EASY",b"HARD",b"NORM",b"SUPR",b"DA_E",b"DA_H",b"DA_N",b"DA_S"]):
                out.i(block.block_data.player_number.value)
                out.i(block.block_data.max_amigo_points)
                out.i(block.block_data.num_commands)
                for cmd in block.block_data.commands:
                    out.i(cmd.frame)
                    out.i(cmd.cmd_bitfield)
                out.pad()
            else:
                print("I don't know to handle blocks", block_name)
        open(fnOut,"wb").write(out.data_bytes())
        fnWii = os.path.join(wii_stream, fn)
        fnWii = os.path.splitext(fnWii)[0] + ".brstm"
        fnDC  = os.path.splitext(fnOut)[0] + ".ADX"
        convert_audio(fnWii, fnDC)
        print("Conversion done! You can rebuild your GDI now.")


def convert_old(fn, data):
    # Convert AMG
    fnWii = os.path.join(wii_amg, fn)
    fnOut = os.path.join(dc_path, "VAMOS_A_CARNAVAL.AMG")
    yn = input(f"Will convert [{fnWii}]\nand write to [{fnOut}]\nOK? (Y/N) ")
    if yn.lower().startswith("y"):
        data2 = []
        i     = 0
        while True:
            # block name
            block_name = pack("<I", unpack(">I", data[i:i+4])[0])
            i += 4
            if block_name != b"ONSH": 
                data2.append(block_name)
            if block_name == b"END_": 
                #print()
                break
            # block size (in bytes)
            block_size = unpack(">I", data[i:i+4])[0]
            i += 4
            if block_name != b"ONSH": 
                data2.append(pack("<I", block_size))
            # block data
            block_data = data[i:i+block_size]
            i += len(block_data)

            if block_name == b"ONSH":
                pass # don't save this block data
            elif block_name == b"CAM_":
                # save no. of entries
                num_entries = unpack(">I", block_data[0:4])[0]
                block_data  = block_data[4:]
                entry_size  = 8*4
                data2.append(pack("<I", num_entries))
                # reverse each entry (set of 8 dwords)
                for n in range(num_entries):
                    for j in range(entry_size, 0, -4):
                        data2.append(pack("<I", unpack(">I", block_data[j-4:j])[0]))
                    block_data = block_data[entry_size:]
                # save any remaining data?
                while block_data:
                    data2.append(pack("<I", unpack(">I", block_data[0:4])[0]))
                    block_data = block_data[4:]
            elif block_name == b"ACT_":
                # save act_num
                act_num    = unpack(">I", block_data[0:4])[0]
                block_data = block_data[4:]
                data2.append(pack("<I", act_num))
                # save no. of entries
                num_entries = unpack(">I", block_data[0:4])[0]
                block_data  = block_data[4:]
                entry_size  = 4*4
                data2.append(pack("<I", num_entries))
                # reverse each entry (set of 8 dwords)
                for n in range(num_entries):
                    for j in range(entry_size, 0, -4):
                        data2.append(pack("<I", unpack(">I", block_data[j-4:j])[0]))
                    block_data = block_data[entry_size:]
                # save any remaining data?
                while block_data:
                    data2.append(pack("<I", unpack(">I", block_data[0:4])[0]))
                    block_data = block_data[4:]
            else:
                for j in range(0, len(block_data), 4):
                    data2.append(pack("<I", unpack(">I", block_data[j:j+4])[0]))
#~ 0123 4567 89ab
#~ sizeU=12
#~ j    |    k
#~ 0: 4 | 8:12
#~ 4: 8 | 4: 8
#~ 8:12 | 0: 4
        data2 = b"".join(data2)
        open(fnOut,"wb").write(data2)
        # Convert ADX
        yn = input("Done! Convert audio as well? (Y/N) ")
        if yn.lower().startswith("y"):
            fnWii    = os.path.join(wii_stream, fn)
            fnWii    = os.path.splitext(fnWii)[0] + ".brstm"
            fnOutAdx = os.path.splitext(fnOut)[0] + ".ADX"
            if not os.path.exists(ffmpeg):
                print(f"Could not find {ffmpeg} - edit this script and/or check your paths and try again.")
                exit()
            args = [ffmpeg, "-i", fnWii, fnOutAdx]
            cp   = run(args)
            if cp.returncode == 0:
                print("All seems well!")
            else:
                print("Oops! Seems like audio conversion went wrong...")
                print("Arguments used:", args)
                print("Return code...:", cp.returncode)


def filePicker(amg):
    # List files
    fns   = sorted(amg)
    ncols = 3
    nrows = 1 + (len(fns) -1) // ncols
    lines = [f"{i+1:3}. {fns[i]}"  for i in range(len(fns))]
    cols  = [lines[i:i+nrows] for i in range(0, len(lines), nrows)]
    max_w = []
    for c in cols:
        max_w.append( max([len(c[r]) for r in range(len(c))]) )
    for r in range(len(cols[0])):
        for c in range(ncols):
            if len(cols[c]) > r:
                print(f"| {cols[c][r]:{max_w[c]}} ", end = "")
        print("|")

    # Ask for file number
    fi = input("\nFile number: ")
    print()
    if fi:
        fi = int(fi)
        if 0 <= fi < len(fns):
            return fns[fi]
    return None


def translate():
    yn = input(f"""This will overwrite extracted GDI files. Proceed? (Y/N) """)
    if yn.lower().startswith("y"):
        # Some translations can be accomplished in different ways, such as patching the main binary or external files.
        # I'll try to minimize binary patching (at least for now).
        paths = {
            "DC" : dc_path,
            "WII": wii_path,
        }
        # These "patches" structures can become external JSON files later. This should help patching other games!
        # patches_copy = files that will simply be copied as is.
        patches_copy = (
            # Directly copy files: [source, destination, comment]
            (("DC","NOTICE_ENGLISH.ADX"), ("DC","NOTICE1.ADX"), 'Audio: "To avoid hitting maracas, stand on the footprints marked on the mat below" (22.09 s)'),
        )
        # Code to perform the patches.
        for entry in patches_copy:
            source, dest, comment = entry
            print(f" - {comment}")
            source = os.path.join(paths[source[0]], source[1])
            dest   = os.path.join(paths[dest  [0]], dest  [1])
            copy2(source, dest)

        # Problem: how to deal with AFS and TPL files? Perhaps I'll create more .ksy files...
        #~ patches_images = (
            #~ # Convert Wii images to Dreamcast: [afs, name, wii, comment]
            #~ ("AFS_CHALLENGE.AFS", "cha_mt01", "challenge_course.tpl"),
        #~ )        
        #~ for entry in patches_copy:
            #~ print(entry)

        print("\nTranslation done! You can rebuild your GDI now.")


if __name__ == '__main__':
    print(f"Amigo (.AMG) Explorer v. {__version__}, by ric@mpcnet.com.br\n")
    # Read all AMG files to a dict
    amg = {}
    readAllAMG(dc_path,  amg)
    readAllAMG(wii_amg,  amg)
    print(f"{len(amg)} .AMG files:")

    while True:
        opt = input("""
    1. Overview of all files and blocks
    2. Dump one file
    3. Dump all files
    4. Search for a hustle command
    5. Convert a Wii song to Dreamcast
    6. Translate Dreamcast game

       Your option: """)
        print()

        # === Get an overview of all blocks in all files
        if opt == "1":
            for fn in sorted(amg):
                blocks_overview(fn, amg[fn])

        # === Dump a single file
        elif opt == "2":
            fn = filePicker(amg)
            if fn:
                dump(fn, amg[fn])

        # === Dump all files (optionally, only regex matching block names)
        elif opt == "3":
            block_type_regex = {
                "1" : { "regex": ".*",   "title":"All blocks" },
                "2" : { "regex": "HEAD", "title":"HEAD" },
                "3" : { "regex": "CAM_", "title":"CAM_" },
                "4" : { "regex": "ACT_", "title":"ACT_" },
                "5" : { "regex": "DA_?", "title":"Amigo non-Hustle blocks" },
                "6" : { "regex": "(EASY|NORM|HARD|SUPR)", "title":"Amigo Hustle blocks" },
            }
            for i in sorted(block_type_regex):
                print(f"{i}. {block_type_regex[i]['title']}")
            print()
            block_type = input("   Block type to display (enter number or regex): ")
            print()
            if block_type:
                for fn in sorted(amg):
                    dump(fn, amg[fn], block_type_regex.get(block_type,{}).get("regex", block_type))

        # === Show songs + stages containing the specified command
        elif opt == "4":
            cmd = input("Type in binary (4 bits) the 'hustle' command to search for: ")
            if cmd:
                for fn in sorted(amg):
                    search_cmd(fn, amg[fn], cmd)

        # === Convert a single file
        elif opt == "5":
            fn = filePicker(amg)
            if fn:
                convert(fn, amg[fn], amg["SAMBA_DE_JANEIRO.AMG"])

        # === Translate game
        elif opt == "6":
            translate()
        
        # === Quit
        else: break



""" The contents of .AMG files are organized into blocks, each with a 4 character name.

In a typical Samba de Amigo ver. 2000 .AMG file, these are the blocks found, in order:
  |HEAD|CAM_|EASY|EASY|HARD|HARD|DA_E|DA_E|DA_H|DA_H|DA_N|DA_N|DA_S|DA_S|ACT_|NORM|NORM|ACT_|ACT_|ACT_|SUPR|SUPR|

Wii .AMG files have an exclusive block type (ONSH).

Here's how many blocks exists, on average, in all .AMG files, per console:

|   |HEAD|CAM_|EASY|HARD|DA_E|DA_H|DA_N|DA_S|ACT_|NORM|SUPR|ONSH|END_|
|DC |  1 |  1 |  2 |  2 |  2 |  2 |  2 |  2 | 3.4|  2 |  2 |  - |  1 |
|Wii|  1 |  1 |  2 |  2 |  2 |  2 |  2 |  2 | 2.3|  2 |  2 |  1 |  1 |

Block types & description:

    HEAD: sequence of frame numbers when camera position & animation changes.

"Amigo" blocks: timed commands the player must perform.
Same block name always appears twice, once for each player.
    EASY: easy mode
    NORM: normal mode
    HARD: hard mode
    SUPR: super hard mode
    DA_E: hustle easy mode
    DA_H: hustle hard mode
    DA_N: hustle normal mode
    DA_S: hustle super hard mode

Other blocks:
    CAM_: camera?
    ACT_: actor(s)? In IDA, bin search for ACT_ (ACT_STOP, ...)
    ONSH: Wii only, training related?

Final block:
    END_: end of file

Each Amigo block has a player number (dword, 0=player 2, 1=player 1),
max. Amigo points (dword) and a certain number of entries/commands (dword).
Each entry has a frame number (dword) and a command (dword).

The command bitfield seems to have this format:

       circle?
  ,____|_________________ hustle cmd
  |    |   ,_____________ hustle speed ? might use bits 9 & 8, too?
  |    |   |      ,______ cmd pos
  |    |   |      |    ,_ cmd
__|_   | __|_ ____|_ __|_
1111 1 1 1111   
9876 5 4 3210 987654 3210
---- - - ---- ------ ----
0011 0 0 0101 000000 0101

cmd (bits 0-3):
    cmd & 0xf == 1 ? "hit"
    cmd & 0xf == 4 ? "pose"
    cmd & 0xf == 3 ? "hit rapidly, begin"
    cmd & 0xf == 8 ? "hit rapidly, end"
    cmd & 0xf == 5 ? "hustle begin"
    cmd & 0xf == 6 ? "hustle end"

cmd pos (bits 4-9):
    bit 4: TL (top, left)
    bit 5: ML (medium, left)
    bit 6: BL (bottom, left)
    bit 7: TR (top, right)
    bit 8: MR (medium, right)
    bit 9: BR (bottom, right)

hustle speed (bits 10-13):
    Seems to influence the hustle speed, but I'm not sure if it is linear...
    Might include bits 8-9 and 14 (even 15) as well.

circle (bit 14):
    bit 14: 1 when hustle cmd is "circle *", but not always...

(bit 15: always zero)

hustle cmd (bits 16-19):
    hustle cmd >> 16 & 0xf ==  0 ? "TL/TR"
    hustle cmd >> 16 & 0xf ==  1 ? "BL/BR"
    hustle cmd >> 16 & 0xf ==  2 ? "TL/ML"
    hustle cmd >> 16 & 0xf ==  3 ? "TR/MR"
    hustle cmd >> 16 & 0xf ==  4 ? "ML/BL"
    hustle cmd >> 16 & 0xf ==  5 ? "MR/BR"
    hustle cmd >> 16 & 0xf ==  6 ? "TL/BL"
    hustle cmd >> 16 & 0xf ==  7 ? "TR/BR"
    hustle cmd >> 16 & 0xf ==  8 ? "circle anti-clockwise"
    hustle cmd >> 16 & 0xf ==  9 ? "circle clockwise"
    hustle cmd >> 16 & 0xf == 10 ? "TL/TR"
    hustle cmd >> 16 & 0xf == 11 ? "BL/BR"
    hustle cmd >> 16 & 0xf == 12 ? "TL/TR"
    hustle cmd >> 16 & 0xf == 13 ? "BL/BR"
    hustle cmd >> 16 & 0xf == 14 ? "TL/TR 2 hands"
    hustle cmd >> 16 & 0xf == 15 ? "BL/BR 2 hands"


For a full format description, see Kaitai Struct .ksy files.
"""

""" Video capture, conversion, inspection:
Run emulator, press [Win]+[G] to record, play one level, stop recording.
Trim video to start as soon as screen isn't black.
Get starting position by playing with ffplay, press [S] to step frame by frame.
Trim with:
    ffmpeg -i "nullDC....mp4" -seek2any true -ss 3.93 samba_de_janeiro_hustle_superhard.mp4
"""


""" To investigate / try:
 - IDA: see "act" stuff in "debug_extra_edit?", "aStand" (stand, jump, side_step, fr_bk_step, act_bakuten, act_object)
 - Check if ACT_ has a field with 6 values range
 - Check if a song have the same animations in all levels
 - Check frame when an extra/actor do an action (e.g., jump) and look for it in HEAD, CAM_, ACT_
 - Use CAM_ & ACT_ from another song

Bamboleo DC vs Wii
 - Wii block order is different - does it matter? (it seems it doesn't)
 - HEAD - same content!
 - CAM_ - VERY different!
 - ACT_ - 0 & 1 are identical, 2 & 3 are slightly different
 - Amigo blocks - VERY similar, same format
"""
