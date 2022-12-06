# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['GUI.py'],
             pathex=['C:\\Windows\\System32\\downlevel', 'C:\\Windows\\SysWOW64\\downlevel', 'C:\\Users\\elisa\\T3\\Head_Kuarter\\password_generator\\Head\\mnemonic'],
             binaries=[],
             datas=[("'themes\\copy_left\\", "themes\\copy_left\\'"), ("'themes\\finances\\", "themes\\finances\\'"), ("'themes\\role_play\\", "themes\\role_play\\'"), ("'themes\\sci-fi\\", "themes\\sci-fi\\'"), ("'themes\\tourism\\*", "themes\\tourism\\'")],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
