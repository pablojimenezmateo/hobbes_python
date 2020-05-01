# Hobbes desktop

My own notetaking application.

**Features**:

* Notes are written in Markdown
* There is no fancy fileformat, just plain folders and txt files
* Version control using git
* If the origin is set on git, you get online backups as well (gitlab, github, bitbucket...)
* You can have multiple note sources 
* Fast note search using Whoosh (ctrl + G to activate)
* Note view, Renderer view or Split view update in realtime (ctrl + l to toggle)
* There is a tiny slider on the bottom left that plays rain sounds when volume > 0 (if volume is zero the sound stops all together)
* Crossplatform (Linux, Windows, Mac)

## Dependencies

sudo apt-get install xclip xsel

## How to build
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
Downloaded from https://freetousesounds.bandcamp.com/album/city-rain-sounds-empty-streets-relaxing-sound-effects and adapted to a perfect loop using Audacity.
