# -*- coding: utf-8 -*-
# 
#   $Id: MainVolume.py 3326 2011-06-17 23:56:38Z jhill $
#   
#   This file is part of the BCPy2000 framework, a Python framework for
#   implementing modules that run on top of the BCI2000 <http://bci2000.org/>
#   platform, for the purpose of realtime biosignal processing.
# 
#   Copyright (C) 2007-11  Jeremy Hill, Thomas Schreiner,
#                          Christian Puzicha, Jason Farquhar
#   
#   bcpy2000@bci2000.org
#   
#   The BCPy2000 framework is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# adapted from a mail.python.org post by Ray Schumacher

__all__ = ['GetMainVolume', 'SetMainVolume']

GetMainVolume = None
SetMainVolume = None

import platform
if platform.system().lower() == 'windows': 
	import ctypes
	
	mixerSetControlDetails = ctypes.windll.winmm.mixerSetControlDetails
	mixerGetControlDetails = ctypes.windll.winmm.mixerGetControlDetailsA
	
	# Some constants
	MIXER_OBJECTF_MIXER = 0   # mmsystem.h
	VOLUME_CONTROL_ID = 0     # Same on all machines?
	SPEAKER_LINE_FADER_ID = 0 # Same on all machines?
	MINIMUM_VOLUME = 0        # fader control (MSDN Library)
	MAXIMUM_VOLUME = 65535    # fader control (MSDN Library)
	
	DWORD = ctypes.c_uint32
	
	class MIXERCONTROLDETAILS(ctypes.Structure):
		_pack_ = 1
		_fields_ = [
			('cbStruct',       DWORD),
			('dwControlID',    DWORD),
			('cChannels',      DWORD),
			('cMultipleItems', DWORD),
			('cbDetails',      DWORD),
			('paDetails',      ctypes.POINTER(ctypes.c_uint32)),
		]
	
	def SetMainVolume(volume, channel=SPEAKER_LINE_FADER_ID):
		volume = min(1.0, max(0.0, volume))
		volume = int( 0.5 + MINIMUM_VOLUME + (MAXIMUM_VOLUME - MINIMUM_VOLUME) * volume )
		
		s = MIXERCONTROLDETAILS(
			ctypes.sizeof(MIXERCONTROLDETAILS),
			channel,
			1, 0,
			ctypes.sizeof(ctypes.c_uint32),
			ctypes.pointer(ctypes.c_uint32(volume)),
		)
		ret = mixerSetControlDetails(
			VOLUME_CONTROL_ID,
			ctypes.byref(s),
			MIXER_OBJECTF_MIXER,
		)
		if ret != 0: raise WindowsError, "Error %d while setting main volume" % ret
			
	def GetMainVolume(channel=SPEAKER_LINE_FADER_ID):
		s = MIXERCONTROLDETAILS(
			ctypes.sizeof(MIXERCONTROLDETAILS),
			channel,
			1, 0,
			ctypes.sizeof(ctypes.c_uint32),
			ctypes.pointer(ctypes.c_uint32(0)),
		)
		ret = mixerGetControlDetails(
			VOLUME_CONTROL_ID,
			ctypes.byref(s),
			MIXER_OBJECTF_MIXER,
		)
		if ret != 0: raise WindowsError, "Error %d while getting mixer control details" % ret
		volume = s.paDetails.contents.value
		return (float(volume) - MINIMUM_VOLUME) / (MAXIMUM_VOLUME - MINIMUM_VOLUME)

if SetMainVolume == None:
	print __name__,'module could not find an implementation for SetMainVolume---only supported for Win32 at the moment'
