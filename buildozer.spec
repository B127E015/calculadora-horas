
[app]

title = Calculadora de Horas
package.name = calculadorahoras
package.domain = br.com.calculadorahoras

source.dir = .
source.include_exts = py,json,kv,png,jpg,atlas

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 35
android.minapi = 24
android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
