import os
import xml.etree.ElementTree as ET
import sys
import base64

# Ensure definitions can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from gh_components.definitions import COMPONENTS

def dict_to_cdata(text):
    return text

def create_plugin(template_path, output_path):
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        print("Please create a blank Grasshopper file, add one standard 'Python 3' script component (from Maths > Script), and save it as template.ghx")
        return False
        
    print(f"Reading template: {template_path}")
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # In a .ghx file, the definition is inside the Archive/Chunk list
    # The actual components are under chunks with name="Definition" -> name="DefinitionObjects"
    
    def_objs = None
    for chunk in root.iter('chunk'):
        if chunk.attrib.get('name') == 'DefinitionObjects':
            def_objs = chunk
            break
            
    if def_objs is None:
        print("Error: Could not find DefinitionObjects in template.")
        return False
        
    # Find the Python component chunk
    # It should be a chunk with name="Object" inside DefinitionObjects
    py_comp = None
    for obj in def_objs.findall('chunk'):
        if obj.attrib.get('name') == 'Object':
            # check if it's a script component. A script component has 'Code' or something similar
            # or we just assume the first Object is our template python component.
            py_comp = obj
            break
            
    if py_comp is None:
        print("Error: No component found in template.")
        return False

    # Remove all existing objects from DefinitionObjects so we can add our 9
    for obj in list(def_objs):
        def_objs.remove(obj)
        
    item_count_item = def_objs.find("items/int[@name='Count']")
    
    x_offset = 0
    
    print(f"Found template component. Generating {len(COMPONENTS)} components...")
    
    for i, spec in enumerate(COMPONENTS):
        # Deep copy the python component XML
        import copy
        import uuid
        
        new_comp = copy.deepcopy(py_comp)
        
        # We need to assign a new InstanceGuid so they don't conflict
        instance_guid = str(uuid.uuid4()).upper()
        
        # The new_comp has <items> which contain string/bool/etc.
        # We need to find and update Name, NickName, Description, and Code.
        for item in new_comp.findall('.//items/*'):
            name = item.attrib.get('name')
            if name == 'Name':
                item.text = spec['name']
            elif name == 'NickName':
                item.text = spec['nickname']
            elif name == 'Description':
                item.text = spec['description']
            elif name == 'Category':
                item.text = spec['category']
            elif name == 'SubCategory':
                item.text = spec['subcategory']
            elif name == 'Code':
                item.text = spec['code']
            elif name == 'InstanceGuid':
                item.text = instance_guid
                
        # To arrange them nicely on the canvas, we modify Attributes/Pivot and Bounds
        # This requires finding the Attributes chunk
        attr_chunk = None
        for chunk in new_comp.findall('chunk'):
            if chunk.attrib.get('name') == 'Attributes':
                attr_chunk = chunk
                break
                
        if attr_chunk is not None:
            # Pivot is usually in items
            for item in attr_chunk.findall('.//items/*'):
                if item.attrib.get('name') == 'Pivot':
                    # Format is usually X,Y or something like that, or separate X and Y float items
                    pass
                if item.attrib.get('name') == 'Bounds':
                    pass
                    
        # Update inputs and outputs... 
        # Actually modifying inputs/outputs of a compiled script component in XML is VERY HARD,
        # because the internal parameters list has its own GUIDs and matching attributes.
        # It's better to just put the code in, and tell the user to configure inputs... 
        # WAIT! If I can't configure inputs programmatically easily, the generated script won't have the right inputs!
        
        def_objs.append(new_comp)
        x_offset += 200
        
    if item_count_item is not None:
        item_count_item.text = str(len(COMPONENTS))
        
    print(f"Writing {output_path}...")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print("Done! Open this file in Grasshopper, then you MUST MANUALLY configure inputs/outputs for each component to match the definitions.")
    return True

if __name__ == "__main__":
    t_path = os.path.join(os.path.dirname(__file__), "..", "src", "gh_components", "template.ghx")
    o_path = os.path.join(os.path.dirname(__file__), "..", "plugin", "rhinoPaths.ghx")
    create_plugin(t_path, o_path)
