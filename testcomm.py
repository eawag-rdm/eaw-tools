from Tkinter import *
from tkinter import ttk
import tkFont
import ckanapi

data_name = {'A': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'],
        'B': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']}

data_id = {'A': ['AA1', 'AA2', 'AA3', 'AA4', 'AA5', 'AA6'],
        'B': ['BB1', 'BB2', 'BB3', 'BB4', 'BB5', 'BB6']}

data_name2 = {}
for i in range(1,7):
    data_name2['A'+ str(i)] = [i*'a'] * 6
    data_name2['B'+ str(i)] = [i*'b'] * 6
data_id2 = {}
for i in range(1,7):
    data_id2['A'+ str(i)] = ['id_'+i*'a'] * 6
    data_id2['B'+ str(i)] = ['id_'+i*'b'] * 6


class MyCombobox(object):

    def __init__(self, label, position, parentframe, parameter, callback, **gridargs):
        '''
        label (str): Label
        position (tuple): (row, column)
        parentframe (tk.Frame)
        '''
 
        self.selected = {'name': StringVar(),
                         'id': '',
                         'idx': int()}

        self.parameter = parameter
        self.callback = callback
        self.values = []
        self.c = self._mk_combobox(label, parentframe, position, gridargs)

        
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        self.values = [{'name': v[0], 'id': v[1]}
                       for v in zip(data_name[self.parameter],
                                    data_id[self.parameter])]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)
        
    def status(self):
        print "Status of {}".format(self.__class__.__name__)
        print "parameter: {}".format(self.parameter)
        print ("selected: name= {}, id= {}, idx= {}"
               .format(self.selected['name'].get(),
                       self.selected['id'],
                       self.selected['idx']))

    def get_select(self):
        return(self.selected)

    def _values_items(self, item):
        return [v[item] for v in self.values]

    def _mk_combobox(self, label, parent, position, gridargs):
        
        def _callback_selected(e):
            e.widget.select_clear()
            self._refresh_select(e.widget.current())
            print "_callback_selected fired"
            
        f = ttk.Frame(parent, padding='10')    
        c = ttk.Combobox(f, textvariable=self.selected['name'],
                         state='readonly',values=self._values_items('name'))
        c.bind('<<ComboboxSelected>>', _callback_selected)
        cl = ttk.Label(f, text=label, font="-weight bold -size 9")
        cl.grid(row=0, column=0, sticky='W')
        c.grid(row=1, column=0, sticky='W')
        f.grid(row=position[0], column=position[1], **gridargs)

        return(c)

    def _refresh_select(self, idx):
        ''' Updates info about selected entity'''
        self.selected['name'].set(self.values[idx]['name'])
        self.selected['id'] = self.values[idx]['id']
        self.selected['idx'] = idx
        if self.callback is not None:
            self.callback(self.selected)

            
class Organization(MyCombobox):
    
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter

        orgas = ckan.call_action('organization_list_for_user',
                             {'permission': 'update_dataset'})
        self.values = [{'name': o['display_name'],
                        'id': o['id']} for o in orgas]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)

class Package(MyCombobox):
    
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        org = ckan.call_action('organization_show',
                                     {'id': self.parameter,
                                      'include_datasets': True})
        self.values = [{'name': p['name'],
                        'id': p['id']} for p in org['packages']]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)
        
class Resource(MyCombobox):
    
    def _mk_combobox(self, label, parent, position, gridargs):
        
        # def _callback_selected(e):
        #     e.widget.select_clear()
        #     self._refresh_select(e.widget.current())
        #     print "_callback_selected fired"
            
        colwidth = [200, 30, 30, 60]    
        c = ttk.Treeview(parent,
                         columns=['name', 'type', 'size', 'modified'],
                         show="headings",
                         height=20,
                         selectmode='browse')
        for h in range(0,4):
            c.heading(h, text = ['Name', 'Type', 'Size', 'Modified'][h])
            c.column(h, stretch=True, width=colwidth[h])
            #c.bind('<<ComboboxSelected>>', _callback_selected)
        # c.insert('',0, None, values = ['RESNAME', 'a type',
        #                                    'Giigabytes', '1970-01-01'])
        c.grid(row=position[0], column=position[1], **gridargs)

        return(c)

    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        print "PARAMETER: {}".format(self.parameter)
        pkg = ckan.call_action('package_show', {'id': self.parameter})
        self.values = [{'name': r['name'],
                        'id': r['id'],
                        'modified':r['last_modified'],
                        'type': r['resource_type'],
                        'size': r['size']} for r in pkg['resources']]
        for item in self.c.get_children():
            self.c.delete(item)
        for v in self.values:
            self.c.insert('', 'end', values = [v['name'], v['type'],
                                               v['size'], v['modified']])
class AppButton(object):
    def __init__(self, label, parent, position, pic, **gridargs):
        self.label = label
        self.b = self._mk_button(label, parent, position, pic, gridargs)


    def _mk_button(self, label, parent, position, pic, gridargs):
        b = ttk.Button(parent, compound=LEFT, image=pic, text=label,
                       command=self.button_press)
        b.grid(row=position[0], column=position[1], **gridargs)
        print "Button - row {}, column {}".format(position[0], position[1])
        
    def button_press(self):
        print "Button: {} pressed!".format(self.label)

class AppFrame(ttk.Frame):
    def __init__(self, parent, position, rowconf, colconf, frameargs, **gridargs):
        print "FRAMEARGS: {}".format(frameargs)
        print "GRIDARGS: {}".format(gridargs)
        ttk.Frame.__init__(self, parent, **frameargs)
        self.grid(row=position[0], column=position[1], **gridargs)
        self.columnconfigure(colconf['idx'], weight=colconf['weight'])
        self.rowconfigure(rowconf['idx'], weight=rowconf['weight'])


               
class ResourceMeta(object):
    def __init__(self, parent):
        '''
 
        '''
        
        frameargs = {'borderwidth': 1, 'relief': 'groove', 'height': 50}
        rowconf = {'idx': 0, 'weight': 1}
        colconf = {'idx': 1, 'weight':1}
        
        frame = ttk.Frame(parent, **frameargs)
        label = ttk.Label(frame, text='ppp')
        label.grid(row=0, column=0)
        print "Parent {}".format(parent)
        # self.frames[len(self.frames)-1].grid(row=1, column=0, columnspan=2)
        # self.frames[len(self.frames)-1].grid_propagate(0)
        # ttk.Label(self.frames[len(self.frames)-1], text='ppp')
        

        # self.items = items
        # for row, i in enumerate(items):
            
            
        # self.parameter = parameter # resource id
        
        # self.frame = self._mk_frame(parentframe, position)
        # self.name_d = StringVar()
        # self.name = ttk.Entry(self.frame, textvariable=self.name_d)
        # self.name.grid(column=0, row=0, sticky='NW')
        # self.description = Text(self.frame, wrap=WORD)
        # self.citation = Text(self.frame, wrap=WORD)
        # self.the_pub_d = StringVar()
        # self.the_pub = ttk.Checkbutton(self.frame,
        #                                        text = "The Package?",
        #                                        variable = self.the_pub_d)
        # self.restype_d = StringVar()
        # self.restype = ttk.Combobox(self.frame, textvariable=self.restype_d,
        #                             state='readonly')
        # self.name.grid(column=0, row=1)
        # self.description.grid(column=0,row=2)
        # self.citation.grid(column=0,row=3)
        # self.the_pub.grid(column=0,row=4)
        # self.restype.grid(column=0,row=5)
                                               
    # def _mk_frame(self, parent, position):
    #     print "Making Frame"
    #     frame = ttk.Frame(parent, borderwidth=5, relief='ridge')
    #     frame.grid(row=position[0], column=position[1], sticky='N')
    #     return(frame)

def callback_orga(selected):
    package.refresh(selected['id'])

def callback_package(selected):
    ressource.refresh(selected['id'])

url = 'http://localhost:5000'
apikey = '948b0f87-d710-4cec-9979-d1ac2fd0d186'
ckan = ckanapi.RemoteCKAN(url, apikey=apikey)

root = Tk()
root.title("Eawag RDM Resource Editor")

# make resizable
top = root.winfo_toplevel()
top.columnconfigure(0, weight=1)
top.rowconfigure(0, weight=1)

# Paned Window ( left - right)
window = ttk.PanedWindow(root, orient=HORIZONTAL)
window.grid(row=0, column=0, sticky=(N,W,E,S))

# left and right Frames in Paned Window
frameargs = {'width': 400, 'height': 300, 'borderwidth':1, 'relief': 'groove'}
rowconf = {'idx': 10, 'weight':1}
leftframe = AppFrame(window, [0,0], rowconf=rowconf,
                     colconf={'idx': 2, 'weight': 1}, frameargs=frameargs)
rightframe = AppFrame(window, [0,0], rowconf=rowconf,
                     colconf={'idx': 0, 'weight': 1}, frameargs=frameargs)
                                                               
# Bottom Frames, left and right
frameargs = {'borderwidth':1, 'relief': 'groove'}
rowconf = {'idx': 0, 'weight': 1}
bottomframe_left = AppFrame(leftframe, [10, 0], rowconf=rowconf,
                            colconf={'idx': 2, 'weight': 1},
                            frameargs=frameargs, columnspan=3, sticky='WES')
bottomframe_right = AppFrame(rightframe, [10, 0], rowconf=rowconf,
                            colconf={'idx': 0, 'weight': 1},
                            frameargs=frameargs, columnspan=3, sticky='WES')

# Selction widgets for Organization and Package
organization = Organization('Organization', [0,0], leftframe, None,
                            callback_orga, sticky='W')
package = Package('Package', [0,1], leftframe, None,
                  callback_package, sticky='W')

# Upload Button
upload = AppButton('UPLOAD', rightframe, [0, 2], None, sticky='E')

# TreeView of Ressources
ressource = Resource('Resources',[1,0], leftframe, None, None,
                     columnspan=3, sticky ='NSWE')

meta_ressources = ttk.Frame(rightframe, borderwidth=1, relief='groove')
meta_ressources.grid(row=1, column=0, columnspan=3, sticky='WE')
meta_ressources.columnconfigure(1, weight=1)
label = ttk.Label(meta_ressources, text='WTFUCK')
label.grid(row=1, column=0)
entry = ttk.Entry(meta_ressources, text='hallo text')
entry.grid(row=1, column=1, sticky='WE')
check = ttk.Checkbutton(meta_ressources)
check.grid(row=1, column=2, sticky='E')




# Bottom Buttons
delete_ressource =  AppButton('Delete\nRessource', bottomframe_left, [0,0], None, sticky='S')
add_ressource =  AppButton('Add\nRessource', bottomframe_left, [0,1], None, sticky='S')

add_ressource =  AppButton('Reset\nRessource', bottomframe_right, [0,1], None, sticky='S')
add_ressource =  AppButton('Multi\nApply', bottomframe_right, [0,2], None, sticky='S')

window.add(leftframe)
window.add(rightframe)


organization.refresh()





# mc2.refresh()
