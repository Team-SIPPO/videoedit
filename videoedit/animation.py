import copy
import numpy as np

def _apeal():
    return 1.0

def _zoom(x, x_range, y_range):
    func = np.polyfit(x_range, y_range, 1)
    scale = x*func[0]+func[1]
    return scale

def _zoom_transient(x, x_range, y_range, mid_x_coef, mid_y_coef):   
    _x_range = copy.deepcopy(x_range)
    _y_range = copy.deepcopy(y_range)
    _x_range.append(x_range[0]+(x_range[1]-x_range[0])*mid_x_coef)
    _y_range.append(y_range[1]-y_range[1]*mid_y_coef)
    scale = np.poly1d(np.polyfit(_x_range, _y_range, 3))(x)
    return scale

def _zoom_in(x, x_range, y_range=[5.0, 1.0]):  # zoom in from the scale of 5.0 to 1.0
    return _zoom(x, x_range, y_range)

def _zoom_out(x, x_range, y_range=[0.5, 1.0]): # zoom out from the scale of 0.5 to 1.0
    return _zoom(x, x_range, y_range)

def _zoom_in_out(x, x_range, y_range=[5.0, 1.0], mid_x_coef=0.98, mid_y_coef=0.5):
    return _zoom_transient(x, x_range, y_range, mid_x_coef, mid_y_coef)

def _zoom_out_in(x, x_range, y_range=[0.5, 1.0], mid_x_coef=0.8, mid_y_coef=-1.5):
    return _zoom_transient(x, x_range, y_range, mid_x_coef, mid_y_coef)

def scaling(current_frame, start_frame, end_frame, animation_type="apeal"):
    scale = 1.0
    x_range = [start_frame, end_frame]
    if animation_type == "apeal":
        return _apeal()
    elif animation_type == "zoom_in":
        return _zoom_in(current_frame, x_range)
    elif animation_type == "zoom_out":
        return _zoom_out(current_frame, x_range)
    elif animation_type == "zoom_in_out":
        return _zoom_in_out(current_frame, x_range)
    elif animation_type == "zoom_out_in":
        return _zoom_out_in(current_frame, x_range)
    else:
        print(f"ERROR: there is no type such as:{type}")
    return scale

def scaling_aftergrow(current_frame, start_frame, end_frame, animation_type="apeal", aftergrow_coef=0.2):
    scale = 1.0
    aftergrow_frame = (end_frame - start_frame) * aftergrow_coef #sec x fps (considering aftergrow)
    min_frame = start_frame
    max_frame = end_frame - aftergrow_frame
    if (current_frame < max_frame):            
        scale = scaling(current_frame, start_frame, max_frame, animation_type)
    return scale
