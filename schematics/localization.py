import gettext
import os

locale_path = os.path.realpath('.') + '/schematics/locale'
gettext.bind_textdomain_codeset('schematics', codeset='UTF-8')  
t = gettext.translation('schematics', locale_path, languages=['pt_BR'], fallback=False, codeset='UTF-8')
_ = t.ugettext
ngettext = t.ungettext