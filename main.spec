# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/home/gef/Documents/Hobbes-many/hobbes_debug/hobbes_python'],
             binaries=[],
             datas=[('media', './media'), ('hobbes.kv', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[

             "ffpyplayer",
             "xmlrpc",
             "defusedxml",
             "PIL",
             "docutils",
             "ssl",
             "crypto",
             "buildozer",
             "cairocffi",
             "CairoSVG",
             "m2r",
             "Pygments",
             "pyperclip",
             "urllib3",
             "zipp",
             "lib2to3",

            'kivy.core.audio',

            'kivy.core.audio.audio_avplayer',
            'kivy.core.audio.audio_ffpyplayer',
            'kivy.core.audio.audio_gstplayer',
            'kivy.core.audio.audio_pygame',
            'kivy.core.audio.audio_sdl2',

            'kivy.core.camera',

            'kivy.core.camera.camera_android',
            'kivy.core.camera.camera_gi',
            'kivy.core.camera.camera_opencv',
            'kivy.core.camera.camera_picamera',

            'kivy.core.clipboard.clipboard_android',
            'kivy.core.clipboard.clipboard_dbusklipper',
            'kivy.core.clipboard.clipboard_dummy',
            'kivy.core.clipboard.clipboard_gtk3',
            'kivy.core.clipboard.clipboard_nspaste',
            'kivy.core.clipboard.clipboard_pygame',
            'kivy.core.clipboard.clipboard_winctypes',

            'kivy.core.spelling',

            'kivy.core.spelling.spelling_enchant',
            'kivy.core.spelling.spelling_osxappkit',

            'kivy.core.text._text_pango',
            'kivy.core.text.text_pango',
            'kivy.core.text.text_pil',
            'kivy.core.text.text_pygame',

            'kivy.core.image.img_dds',
            'kivy.core.image.img_ffpyplayer',
            'kivy.core.image.img_gif',
            'kivy.core.image.img_pil',
            'kivy.core.image.img_pygame',
            'kivy.core.image.img_tex',

            'kivy.core.window.window_egl_rpi',
            'kivy.core.window.window_info',
            'kivy.core.window.window_pygame',

            'kivy.graphics.cgl_backend.cgl_debug',
            'kivy.graphics.cgl_backend.cgl_mock',

            'kivy.graphics.svg',
            'kivy.graphics.tesselator',

            'xml.etree.cElementTree'
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='hobbes',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
