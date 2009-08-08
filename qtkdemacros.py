# -*- coding: utf-8 -*-

__QtBareMacros = ["Q_OBJECT", "Q_GADGET", "Q_OBJECT_CHECK", "K_DCOP"] 

def QtBareMacros(extraMacros=[]):
    macros = __QtBareMacros[:]
    macros.extend(extraMacros)
    return macros
    
__QtMacros = [
        "Q_ENUMS", "Q_PROPERTY", "Q_OVERRIDE", "Q_SETS", "Q_CLASSINFO",\
        "Q_DECLARE_OPERATORS_FOR_FLAGS", "Q_PRIVATE_SLOT", "Q_FLAGS",\
        "Q_DECLARE_INTERFACE", "Q_DECLARE_METATYPE","KDE_DUMMY_COMPARISON_OPERATOR",\
        "Q_GADGET", "K_DECLARE_PRIVATE", "PHONON_ABSTRACTBASE", "PHONON_HEIR",\
        "PHONON_OBJECT", "Q_DECLARE_PRIVATE", "QT_BEGIN_HEADER", "QT_END_HEADER",\
        "Q_DECLARE_BUILTIN_METATYPE", "Q_OBJECT_CHECK", "Q_DECLARE_PRIVATE_MI",\
        "KDEUI_DECLARE_PRIVATE", "KPARTS_DECLARE_PRIVATE", "Q_INTERFACES",\
        '__attribute__', 'Q_DISABLE_COPY', 'K_SYCOCATYPE', 'Q_DECLARE_TR_FUNCTIONS']
        
def QtMacros(extraMacros=[]):
    macros = __QtMacros[:]
    macros.extend(extraMacros)
    return macros
