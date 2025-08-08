#!/bin/bash
set -e

# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y git curl unzip xz-utils zip libglu1-mesa

# 2. Download Flutter SDK if not already present
if [ ! -d "$HOME/flutter" ]; then
  git clone https://github.com/flutter/flutter.git -b stable $HOME/flutter
fi

# 3. Add Flutter to PATH for this session and future sessions
export PATH="$PATH:$HOME/flutter/bin"
if ! grep -q 'export PATH="$PATH:$HOME/flutter/bin"' ~/.bashrc; then
  echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.bashrc
fi

# 4. Run flutter doctor
flutter doctor

# 5. Go to project directory
cd ~/lvl_up

# 6. Get dependencies, run tests, and build APK
flutter pub get
flutter test
flutter build apk --release

# 7. Restart backend service
sudo systemctl restart ai-backend-python

echo "\n✅ Flutter app tested, built, and backend restarted!"
echo "APK is at: ~/lvl_up/build/app/outputs/flutter-apk/app-release.apk" 