gal.icns: gal-256.png
	png2icns $@ $^

 #--onefile
#pyinstaller --windowed --onedir \
#	--icon=gal.icns --name Hello --noconfirm hello.py 


app: gal.icns
	pyinstaller --noconfirm Hello.spec
	cp gal.icns dist/hello.app/Contents/Resources/icon-windowed.icns
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
