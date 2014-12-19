import os

# -*- mode: python -*-
a = Analysis(['hello.py'],
             pathex=[os.getcwd()],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Hello',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='gal.icns')

a.datas += Tree('data/ephemerides', prefix='data/ephemerides')
a.datas += [('data/example.jpg', 'data/example.jpg', 'DATA'),
            ('data/example.wcs', 'data/example.wcs', 'DATA'),]

a.binaries += [('libqjpeg.dylib', '/usr/local/Cellar/qt/4.8.6/plugins/imageformats/libqjpeg.dylib', 'BINARY')]
#a.binaries += [('plugins/libqjpeg.dylib', '/usr/local/Cellar/qt/4.8.6/plugins/imageformats/libqjpeg.dylib', 'BINARY')]
#a.binaries += [('plugins/imageformats/libqjpeg.dylib', '/usr/local/Cellar/qt/4.8.6/plugins/imageformats/libqjpeg.dylib', 'BINARY')]

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='Hello')

app = BUNDLE(coll,
             name='Hello.app',
             icon='gal.icns')
