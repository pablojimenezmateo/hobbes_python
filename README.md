## Dependencies

sudo apt-get install xclip xsel

Activate environment:

source ~/kivy_venv/bin/activate


# Buildozer build

For this to work we need jdk-10, but we need the file jdk-10/lib/security/cacerts from jdk-14, I just copied it

export PATH=/home/gef/Documents/Hobbes-many/kivy/jdk-10/bin/:$PATH

I also had to install build-tools as well as the android API 27 manually:

cd .buildozer/android/platform/android-sdk/tools/bin
./sdkmanager "build-tools;27.0.0"
./sdkmanager  "platform-tools" "platforms;android-27"

buildozer android debug deploy run

With:

buildozer serve

You can download the apk on your device


## Rain sound
Downloaded from https://freetousesounds.bandcamp.com/album/city-rain-sounds-empty-streets-relaxing-sound-effects


## Audio fix

Same issue on debian, and the fix for me required installation of the kivy dependencies:

So:
sudo apt-get install python-pip build-essential git python python-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

Followed by:

pip uninstall kivy

and then:

pip install --no-binary kivy kivy