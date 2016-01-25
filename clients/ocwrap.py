from __future__ import print_function
# use either OcClient or OcClientGuiDecorator

def get_occlient(no_gui, occonf):
    import oc
    occ = oc.OcClient(occonf)

    if no_gui:
        print ("Not showing a gui")
        return occ
    else:
        try:
            import oc_gui
            return oc_gui.OcClientGuiDecorator(occ)
        except ImportError as e:
            print ("unable to import oc_gui: %s", (e,))
            return occ
