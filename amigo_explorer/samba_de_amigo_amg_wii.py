# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class SambaDeAmigoAmgWii(KaitaiStruct):
    """Samba de Amigo is a rhythm game developed by Sonic Team and published
    by Sega. There are versions for arcades, the Sega Dreamcast 
    and the Nintendo Wii.
    
    Each song in the game has a corresponding .AMG ("Amigo") file,
    with all the movements ("commands") and timing (as FPS @ 60 Hz)
    for each play mode.
    
    This file format is currently a WORK IN PROGRESS!!!
    """

    class BlockNameEnum(Enum):
        head = 1145128264
        hard = 1146241352
        da_e = 1163870532
        onsh = 1213419087
        da_h = 1214202180
        norm = 1297239886
        da_n = 1314865476
        supr = 1380996435
        da_s = 1398751556
        easy = 1498628421
        end_ = 1598312005
        cam_ = 1598898499
        act_ = 1599357761

    class PlayerEnum(Enum):
        player2 = 0
        player1 = 1
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.blocks = []
        i = 0
        while True:
            _ = self._root.Block(self._io, self, self._root)
            self.blocks.append(_)
            if _.block_name == self._root.BlockNameEnum.end_:
                break
            i += 1

    class BlockHead(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_entries = self._io.read_u4be()
            self.entries = [None] * (self.num_entries)
            for i in range(self.num_entries):
                self.entries[i] = self._io.read_u4be()



    class CamData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.frame = self._io.read_u4be()
            self.dword1 = self._io.read_u4be()
            self.dword2 = self._io.read_s4be()
            self.dword3 = self._io.read_u4be()
            self.dword4 = self._io.read_u4be()
            self.dword5 = self._io.read_s4be()
            self.dword6 = self._io.read_u4be()
            self.dword7 = self._io.read_s4be()


    class BlockAct(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.act_num = self._io.read_u4be()
            self.num_entries = self._io.read_u4be()
            self.entries = [None] * (self.num_entries)
            for i in range(self.num_entries):
                self.entries[i] = self._root.ActData(self._io, self, self._root)



    class Command(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.frame = self._io.read_u4be()
            if self.frame != 0:
                self.cmd_bitfield = self._io.read_u4be()


        @property
        def cmd_hustle(self):
            """Hustle command."""
            if hasattr(self, '_m_cmd_hustle'):
                return self._m_cmd_hustle if hasattr(self, '_m_cmd_hustle') else None

            self._m_cmd_hustle = (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 0 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 1 else (u"TL/ML" if ((self.cmd_bitfield >> 16) & 15) == 2 else (u"TR/MR" if ((self.cmd_bitfield >> 16) & 15) == 3 else (u"ML/BL" if ((self.cmd_bitfield >> 16) & 15) == 4 else (u"MR/BR" if ((self.cmd_bitfield >> 16) & 15) == 5 else (u"TL/BL" if ((self.cmd_bitfield >> 16) & 15) == 6 else (u"TR/BR" if ((self.cmd_bitfield >> 16) & 15) == 7 else (u"circle anti-clockwise" if ((self.cmd_bitfield >> 16) & 15) == 8 else (u"circle clockwise" if ((self.cmd_bitfield >> 16) & 15) == 9 else (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 10 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 11 else (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 12 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 13 else (u"TL/TR 2 hands" if ((self.cmd_bitfield >> 16) & 15) == 14 else (u"BL/BR 2 hands" if ((self.cmd_bitfield >> 16) & 15) == 15 else u"unknown command"))))))))))))))))
            return self._m_cmd_hustle if hasattr(self, '_m_cmd_hustle') else None

        @property
        def cmd_hustle_bits(self):
            """Hustle command (bits 16-19)."""
            if hasattr(self, '_m_cmd_hustle_bits'):
                return self._m_cmd_hustle_bits if hasattr(self, '_m_cmd_hustle_bits') else None

            self._m_cmd_hustle_bits = (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 0 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 1 else (u"TL/ML" if ((self.cmd_bitfield >> 16) & 15) == 2 else (u"TR/MR" if ((self.cmd_bitfield >> 16) & 15) == 3 else (u"ML/BL" if ((self.cmd_bitfield >> 16) & 15) == 4 else (u"MR/BR" if ((self.cmd_bitfield >> 16) & 15) == 5 else (u"TL/BL" if ((self.cmd_bitfield >> 16) & 15) == 6 else (u"TR/BR" if ((self.cmd_bitfield >> 16) & 15) == 7 else (u"circle anti-clockwise" if ((self.cmd_bitfield >> 16) & 15) == 8 else (u"circle clockwise" if ((self.cmd_bitfield >> 16) & 15) == 9 else (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 10 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 11 else (u"TL/TR" if ((self.cmd_bitfield >> 16) & 15) == 12 else (u"BL/BR" if ((self.cmd_bitfield >> 16) & 15) == 13 else (u"TL/TR 2 hands" if ((self.cmd_bitfield >> 16) & 15) == 14 else (u"BL/BR 2 hands" if ((self.cmd_bitfield >> 16) & 15) == 15 else u"unknown hustle command"))))))))))))))))
            return self._m_cmd_hustle_bits if hasattr(self, '_m_cmd_hustle_bits') else None

        @property
        def cmd_reserved_bits(self):
            """Unused / reserved."""
            if hasattr(self, '_m_cmd_reserved_bits'):
                return self._m_cmd_reserved_bits if hasattr(self, '_m_cmd_reserved_bits') else None

            self._m_cmd_reserved_bits = (self.cmd_bitfield >> 20)
            return self._m_cmd_reserved_bits if hasattr(self, '_m_cmd_reserved_bits') else None

        @property
        def cmd_type(self):
            """Command type (bits 0-3)."""
            if hasattr(self, '_m_cmd_type'):
                return self._m_cmd_type if hasattr(self, '_m_cmd_type') else None

            self._m_cmd_type = (u"hit" if (self.cmd_bitfield & 15) == 1 else (u"pose" if (self.cmd_bitfield & 15) == 4 else (u"hit rapidly, begin" if (self.cmd_bitfield & 15) == 3 else (u"hit rapidly, end" if (self.cmd_bitfield & 15) == 8 else (u"hustle begin" if (self.cmd_bitfield & 15) == 5 else (u"hustle end" if (self.cmd_bitfield & 15) == 6 else u"unknown command"))))))
            return self._m_cmd_type if hasattr(self, '_m_cmd_type') else None

        @property
        def cmd_pos(self):
            """Command position (bits 4-9)."""
            if hasattr(self, '_m_cmd_pos'):
                return self._m_cmd_pos if hasattr(self, '_m_cmd_pos') else None

            self._m_cmd_pos = [(u"TL" if ((self.cmd_bitfield >> 4) & 1) == 1 else u""), (u"ML" if ((self.cmd_bitfield >> 5) & 1) == 1 else u""), (u"BL" if ((self.cmd_bitfield >> 6) & 1) == 1 else u""), (u"TR" if ((self.cmd_bitfield >> 7) & 1) == 1 else u""), (u"MR" if ((self.cmd_bitfield >> 8) & 1) == 1 else u""), (u"BR" if ((self.cmd_bitfield >> 9) & 1) == 1 else u"")]
            return self._m_cmd_pos if hasattr(self, '_m_cmd_pos') else None

        @property
        def sec(self):
            """Time value in seconds @ 60 Hz."""
            if hasattr(self, '_m_sec'):
                return self._m_sec if hasattr(self, '_m_sec') else None

            self._m_sec = (self.frame / 60.0)
            return self._m_sec if hasattr(self, '_m_sec') else None


    class BlockCam(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_entries = self._io.read_u4be()
            self.entries = [None] * (self.num_entries)
            for i in range(self.num_entries):
                self.entries[i] = self._root.CamData(self._io, self, self._root)



    class Block(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.block_name = self._root.BlockNameEnum(self._io.read_u4be())
            if self.block_name != self._root.BlockNameEnum.end_:
                self.block_size = self._io.read_u4be()

            if self.block_name != self._root.BlockNameEnum.end_:
                _on = self.block_name
                if _on == self._root.BlockNameEnum.hard:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.head:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockHead(io, self, self._root)
                elif _on == self._root.BlockNameEnum.onsh:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockOnsh(io, self, self._root)
                elif _on == self._root.BlockNameEnum.supr:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.da_e:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.easy:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.cam_:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockCam(io, self, self._root)
                elif _on == self._root.BlockNameEnum.da_s:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.da_h:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.norm:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                elif _on == self._root.BlockNameEnum.act_:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAct(io, self, self._root)
                elif _on == self._root.BlockNameEnum.da_n:
                    self._raw_block_data = self._io.read_bytes(self.block_size)
                    io = KaitaiStream(BytesIO(self._raw_block_data))
                    self.block_data = self._root.BlockAmigos(io, self, self._root)
                else:
                    self.block_data = self._io.read_bytes(self.block_size)



    class BlockAmigos(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.player_number = self._root.PlayerEnum(self._io.read_u4be())
            self.max_amigo_points = self._io.read_u4be()
            self.num_commands = self._io.read_u4be()
            self.commands = [None] * (self.num_commands)
            for i in range(self.num_commands):
                self.commands[i] = self._root.Command(self._io, self, self._root)



    class ActData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.frame = self._io.read_u4be()
            self.dword1 = self._io.read_u4be()
            self.dword2 = self._io.read_u4be()
            self.dword3 = self._io.read_u4be()


    class BlockOnsh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_entries = self._io.read_u4be()
            self.entries = [None] * (self.num_entries)
            for i in range(self.num_entries):
                self.entries[i] = self._io.read_u4be()




