"""
Sample Grasshopper Python 3 Component.
"""
import rhinoscriptsyntax as rs
import Grasshopper

class SampleComponent(Grasshopper.Kernel.GH_ScriptInstance): # or ghpythonlib.componentbase.executingcomponent
    def RunScript(self, A, B):
        """
        Calculates the sum of two inputs.
        
        Args:
            A: First input
            B: Second input
            
        Returns:
            result: The sum of A and B
        """
        if A is not None and B is not None:
            result = A + B
        else:
            result = None
            
        return result
