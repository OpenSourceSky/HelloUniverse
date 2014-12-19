gal.icns: gal-256.png
	png2icns $@ $^

 #--onefile
#pyinstaller --windowed --onedir \
#	--icon=gal.icns --name Hello --noconfirm hello.py 


app: gal.icns
	pyinstaller --noconfirm Hello.spec
	cp gal.icns dist/Hello.app/Contents/Resources/icon-windowed.icns
	cp qt.conf dist/Hello.app/Contents/Resources/
	cp qt.conf dist/Hello
	mkdir dist/dmg
	cp -a dist/Hello.app dist/dmg/
	rm hello.dmg
	hdiutil create hello.dmg -volname "Hello Universe" -srcfolder dist/dmg

.PHONY: app


#
# The minimal plist provided by PyInstaller designates the icon file
# for the app as the icon-windowed.icns file in Resources. This is the
# PyInstaller logo in icns format. Support for the --icon-file option
# is promised for the future. For now you can apply your own icon
# after the app is built in several ways:
#
#    Prepare another .icns file with your own graphic, save it as
#    icon-windowed.icns replacing the default one in Resources.
#
#    Prepare an .icns file with your own graphic, place it in
#    Resources and edit the Info.plist to name it.
#
#    Prepare an .icns file with your own graphic; open in it
#    Preview.app; select-all and copy; in the Finder, Get Info on your
#    app; click the icon in the info display and paste.
#
# GraphicConverter is one of several applications that can save a JPEG
# or PNG image in the .icns format.
