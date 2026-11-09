[app]
title = COSTIFY
package.name = costify
package.domain = com.costify.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0

android.permissions =
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
