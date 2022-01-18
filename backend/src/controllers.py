class BaseController:
    def __init__(self, image_controller):
        self.image_controller = image_controller
    
    def new_edit(self, pid, eid, edits, size, seed):
        img = self.image_controller.generate_image(edits, size, seed)
        return img