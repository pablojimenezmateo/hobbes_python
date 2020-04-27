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